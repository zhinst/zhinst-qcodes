from .base import ZIBaseInstrument
from qcodes.instrument.channel import ChannelList, InstrumentChannel
import qcodes.utils.validators as vals

import zhinst.toolkit as tk
from zhinst.toolkit.control.drivers.uhfqa import (
    ReadoutChannel,
    AWG as UHFQA_AWG,
    UHFScope as UHFQA_Scope,
)
from typing import List, Dict, Union
import numpy as np


class AWG(InstrumentChannel):
    """Device-specific *AWG Core* for the *UHFQA*.

    Inherits from :class:`InstrumentChannel` and wraps around a `AWGCore` for
    *HDAWG* from :mod:`zhinst-toolkit`. This class adds Parameters from the
    :mod:`zhinst-toolkit` as *QCoDeS Parameters* and wraps all methods of the
    *toolkit's* `AWGCore`.

    Arguments:
        name (str): The name of the `AWG` submodule.
        parent_instr (:class:`qcodes.instrument.base.Instrument`): The QCoDeS
            parent instrument of the `InstrumentChannel`.
        parent_contr (:class:`zhinst.toolkit.BaseInstrument`): The `_controller`
            of the parent instrument that is used for getting and setting
            parameters.

    Attributes:
        output1 (:class:`Parameter`): The state
            of the output of channel 1. Can be one of {'on', 'off'}.
        output2 (:class:`Parameter`): The state
            of the output of channel 2. Can be one of {'on', 'off'}.
        gain1 (:class:`Parameter`): Gain of the
            output channel 1. The value must be between -1 and +1 (default: +1).
        gain2 (:class:`Parameter`): Gain of the
            output channel 2. The value must be between -1 and +1 (default: +1).
        waveforms (list): A list of `Waveforms` that respresent the queue of
            waveforms to upload to the device when the sequence type is
            *'Simple'*.
        is_running (bool): A flag that shows if the `AWG Core` is currently
            running or not.
        index (int): The index of the `AWG Core` in the list of *awgs*.

    """

    def __init__(self, name: str, parent_instr, parent_contr) -> None:
        super().__init__(parent_instr, name)
        self._awg = UHFQA_AWG(parent_contr, 0)
        self._awg._setup()
        self._awg._init_awg_params()
        self._add_qcodes_awg_params()

    def _add_qcodes_awg_params(self):
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "output1",
            unit=self._awg.output1._unit,
            docstring=self._awg.output1.__repr__(),
            get_cmd=self._awg.output1,
            set_cmd=self._awg.output1,
            label="Output Ch 1",
        )
        self.add_parameter(
            "output2",
            unit=self._awg.output2._unit,
            docstring=self._awg.output2.__repr__(),
            get_cmd=self._awg.output2,
            set_cmd=self._awg.output2,
            label="Output Ch 2",
        )
        self.add_parameter(
            "gain1",
            unit=self._awg.gain1._unit,
            docstring=self._awg.gain1.__repr__(),
            get_cmd=self._awg.gain1,
            set_cmd=self._awg.gain1,
            label="Gain Ch 1",
        )
        self.add_parameter(
            "gain2",
            unit=self._awg.gain2._unit,
            docstring=self._awg.gain2.__repr__(),
            get_cmd=self._awg.gain2,
            set_cmd=self._awg.gain2,
            label="Gain Ch 2",
        )
        self.add_parameter(
            "single",
            unit=self._awg.single._unit,
            docstring=self._awg.single.__repr__(),
            get_cmd=self._awg.single,
            set_cmd=self._awg.single,
            label="AWG Single Shot Mode",
        )

    def outputs(self, value=None):
        """Sets both signal outputs simultaneously.

        Arguments:
            value (tuple): Tuple of values {'on', 'off'} for channel 1
                and 2 (default: None).

        Returns:
            A tuple with the states {'on', 'off'} for the two output
            channels if the keyword argument is not given.

        Raises:
            ValueError: If the `value` argument is not a list or tuple
                of length 2.

        """
        return self._awg.outputs(value=value)

    def run(self, sync=True) -> None:
        """Run the AWG Core.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after enabling the AWG Core (default: True).

        """
        self._awg.run(sync=sync)

    def stop(self, sync=True) -> None:
        """Stop the AWG Core.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after disabling the AWG Core (default: True).

        """
        self._awg.stop(sync=sync)

    def wait_done(self, timeout: float = 10, sleep_time: float = 0.005) -> None:
        """Wait until the AWG Core is finished.

        Arguments:
            timeout (float): The maximum waiting time in seconds for the
                AWG Core (default: 10).
            sleep_time (float): Time in seconds to wait between
                requesting AWG state

        Raises:
            ToolkitError: If the AWG is running in continuous mode.
            TimeoutError: If the AWG is not finished before the timeout.

        """
        self._awg.wait_done(timeout=timeout, sleep_time=sleep_time)

    def compile(self) -> None:
        """Compiles the current SequenceProgram on the AWG Core.

        Raises:
            ToolkitConnectionError: If the AWG Core has not been set up
                yet
            ToolkitError: if the compilation has failed or the ELF
                upload is not successful.
            TimeoutError: if the program upload is not completed before
                timeout.

        """
        self._awg.compile()

    def reset_queue(self) -> None:
        """Resets the waveform queue to an empty list."""
        self._awg.reset_queue()

    def queue_waveform(
        self,
        wave1: Union[List, np.array],
        wave2: Union[List, np.array],
        delay: float = 0,
    ) -> None:
        """Queues up a waveform to the *AWG Core*.

        Uploading custom waveforms is only possible when using the
        *'Simple'* or *'Custom'* sequence types. The waveform is
        specified with two numpy arrays for the two channels of the
        *AWG Core*. The waveform will then automatically align them to
        the correct minimum waveform length, sample granularity and
        scaling. An individual delay can be specified to shift the
        individual waveform with respect to the time origin of the
        period.

        Arguments:
            wave1 (array like): A list or array of samples in the
                waveform to be queued for channel 1. An empty list '[]'
                will upload zeros of the minimum waveform length.
            wave2 (array like): A list or array of samples in the
                waveform to be queued for channel 2. An empty list '[]'
                will upload zeros of the minimum waveform length.
            delay (float): An individual delay for the queued sequence
                with respect to the time origin. Positive values shift
                the start of the waveform forwards in time. (default: 0)

        Raises:
            ToolkitError: If the sequence is not of type *'Simple'* or
                *'Custom'*.

        """
        self._awg.queue_waveform(wave1, wave2, delay=delay)

    def replace_waveform(
        self,
        wave1: Union[List, np.array],
        wave2: Union[List, np.array],
        i: int = 0,
        delay: float = 0,
    ) -> None:
        """Replaces the data in a waveform in the queue.

        The new data must have the same length as the previous data
        s.t. the waveform data can be replaced without recompilation of
        the sequence program.

        Arguments:
            wave1 (array): Waveform to replace current wave for
                Channel 1.
            wave2 (array): Waveform to replace current wave for
                Channel 2.
            i (int): The index of the waveform in the queue to be
                replaced.
            delay (int): An individual delay in seconds for this
                waveform w.r.t. the time origin of the sequence
                (default: 0).

        Raises:
            ValueError: If the given index is out of range.

        """
        self._awg.replace_waveform(wave1, wave2, i=i, delay=delay)

    def upload_waveforms(self) -> None:
        """Uploads all waveforms in the queue to the AWG Core.

        This method only works as expected if the Sequence Program is in
        'Simple' or 'Custom' modes and has been compiled beforehand.
        See :func:`compile_and_upload_waveforms(...)`.
        """
        self._awg.upload_waveforms()

    def compile_and_upload_waveforms(self) -> None:
        """Compiles the Sequence Program and uploads the queued waveforms.

        Simply combines the two methods to make sure the sequence is compiled
        before the waveform queue is uplaoded.
        """
        self._awg.compile_and_upload_waveforms()

    def set_sequence_params(self, **kwargs) -> None:
        """Sets the parameters of the *Sequence Program*.

        Passes all the keyword arguments to the `set_param(...)` method of the
        *Sequence Program*. The available sequence parameters may vary between
        different sequences. For a list of all current sequence parameters see
        the method `sequence_params()`.

        They include:
            *'sequence_type', 'period', 'repetitions', 'trigger_mode',
            'trigger_delay', ...*

            >>> hdawg.awgs[0].set_sequence_params(
            >>>     sequence_type="Simple",
            >>>     trigger_mode="Send Trigger",
            >>>     repetitions=1e6,
            >>>     alignemnt="Start with Trigger"
            >>> )

        """
        self._awg.set_sequence_params(**kwargs)

    def sequence_params(self) -> None:
        """Returns the current seuence parameters.

        Returns:
            A dictionary with the current sequence parameters.

        """
        return self._awg.sequence_params

    @property
    def waveforms(self):
        return self._awg.waveforms

    @property
    def is_running(self):
        return self._awg.is_running

    @property
    def index(self):
        return self._awg.index


class Channel(InstrumentChannel):
    """Implements a *Readout Channel* for the *UHFQA*.

    Inherits from :class:`InstrumentChannel` and wraps around a `ReadoutChannel`
    for *UHFQA* from :mod:`zhinst-toolkit`. This class adds *Parameters* from
    the :mod:`zhinst-toolkit` as *QCoDeS Parameters* and wraps all methods of
    the *toolkit's* `ReadoutChannel`.

    This class represents the signal processing chain for one of the ten
    :class:`ReadoutChannels` of a UHFQA. One channel is typically used for
    dispersive resonator readout of a superconducting Qubit.

        >>> ch = uhfqa.channels[0]
        >>> uhfqa.result_source("Threshold")
        >>> ...
        >>> ch.enable()
        >>> ch.readout_frequency(85.6e6)
        >>> ch.rotation(123.4)
        >>> ch.threshold(-56.78)
        >>> ...
        >>> ch.result()
        array([0.0, 1.0, 1.0, 1.0, 0.0, ...])

    The readout channel can be enabled with `enable()` which means that the
    weighted integration mode is activated and integration weights are set to
    demodulate the signal at the given readout frequency. If the channel is
    enabled, the readout parameters are also used for signal generation in the
    :class:`AWGCore` if the sequence type is set to "Readout".

    Arguments:
        name (str): The name of the `Channel` submodule.
        parent_instr (:class:`qcodes.instrument.base.Instrument`): The QCoDeS
            parent instrument of the `InstrumentChannel`.
        parent_contr (:class:`zhinst.toolkit.BaseInstrument`): The `_controller`
            of the parent instrument that is used for getting and setting
            parameters.

    Attributes:
        index (int): The index of the Readout Channel from 1 - 10.
        rotation (:class:`Parameter`): The
            rotation applied to the signal in IQ plane. The angle is specified
            in degrees.
        threshold (:class:`Parameter`): The
            signal threshold used for state discrimination in the thresholding
            unit.
        result (:class:`Parameter`): This
            read-only Parameter holds the result vector for the given readout
            channel as a 1D numpy array.

    """

    def __init__(self, name: str, index: int, parent_instr, parent_contr) -> None:
        super().__init__(parent_instr, name)
        self._channel = ReadoutChannel(parent_contr, index)
        self._channel._init_channel_params()
        self._add_qcodes_channel_params()

    def _add_qcodes_channel_params(self):
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "rotation",
            unit=self._channel.rotation._unit,
            docstring=self._channel.rotation.__repr__(),
            get_cmd=self._channel.rotation,
            set_cmd=self._channel.rotation,
            label="Rotation",
        )
        self.add_parameter(
            "threshold",
            unit=self._channel.threshold._unit,
            docstring=self._channel.threshold.__repr__(),
            get_cmd=self._channel.threshold,
            set_cmd=self._channel.threshold,
            label="Threshold",
            vals=vals.Numbers(),
        )
        self.add_parameter(
            "readout_frequency",
            unit="Hz",
            docstring="Readout frequency of the channel. Is used to create a readout "
            "tone and to set the integration weights.",
            get_cmd=self._channel.readout_frequency,
            set_cmd=self._channel.readout_frequency,
            label="Readout Frequency",
            vals=vals.Numbers(),
        )
        self.add_parameter(
            "int_weights_envelope",
            docstring="Envelope values multiplied with the integration weights.",
            get_cmd=self._channel.int_weights_envelope,
            set_cmd=self._channel.int_weights_envelope,
            label="Integration Weights Envelope",
        )
        self.add_parameter(
            "readout_amplitude",
            unit="Hz",
            docstring="The amplitude of the readout tone associated with this channel. "
            "Used in a 'Readout' sequence.",
            get_cmd=self._channel.readout_amplitude,
            set_cmd=self._channel.readout_amplitude,
            label="Readout Amplitude",
            vals=vals.Numbers(),
        )
        self.add_parameter(
            "phase_shift",
            unit="Hz",
            docstring="The phase shift of the readout tone associated with this "
            "channel. Used in a 'Readout' sequence.",
            get_cmd=self._channel.phase_shift,
            set_cmd=self._channel.phase_shift,
            label="Readout Phase Shift",
            vals=vals.Numbers(),
        )
        self.add_parameter(
            "result",
            unit=self._channel.result._unit,
            docstring=self._channel.result.__repr__(),
            get_cmd=self._channel.result,
            label="Result",
        )

    def enabled(self) -> None:
        """Returns if weighted integration is enabled."""
        return self._channel.enabled()

    def enable(self) -> None:
        """Enable weighted integration for this channel.

        This method also sets the corresponding integration weights to
        demodulate at the given readout frequency.
        """
        self._channel.enable()

    def disable(self) -> None:
        """Disable weighted integration for this channel.

        This method also resets the corresponding integration weights.
        """
        self._channel.disable()

    @property
    def index(self):
        return self._channel.index


class Scope(InstrumentChannel):
    """Device-specific *Scope* for the *UHFQA*."""

    def __init__(self, name: str, parent_instr, parent_contr) -> None:
        super().__init__(parent_instr, name)
        self._scope = UHFQA_Scope(parent_contr)
        self._scope._setup()
        self._scope._init_scope_params()
        self._scope._init_scope_settings()
        self._add_qcodes_scope_params()

    def _add_qcodes_scope_params(self):
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "single",
            unit=self._scope.single._unit,
            docstring=self._scope.single.__repr__(),
            get_cmd=self._scope.single,
            set_cmd=self._scope.single,
            label="Scope Single Shot Mode",
        )
        self.add_parameter(
            "length",
            unit=self._scope.length._unit,
            docstring=self._scope.length.__repr__(),
            get_cmd=self._scope.length,
            set_cmd=self._scope.length,
            label="Length of Scope Shot",
        )
        self.add_parameter(
            "trigger_source",
            unit=self._scope.trigger_source._unit,
            docstring=self._scope.trigger_source.__repr__(),
            get_cmd=self._scope.trigger_source,
            set_cmd=self._scope.trigger_source,
            label="Scope Trigger Source",
        )
        self.add_parameter(
            "trigger_level",
            unit=self._scope.trigger_level._unit,
            docstring=self._scope.trigger_level.__repr__(),
            get_cmd=self._scope.trigger_level,
            set_cmd=self._scope.trigger_level,
            label="Scope Trigger Level",
        )
        self.add_parameter(
            "trigger_enable",
            unit=self._scope.trigger_enable._unit,
            docstring=self._scope.trigger_enable.__repr__(),
            get_cmd=self._scope.trigger_enable,
            set_cmd=self._scope.trigger_enable,
            label="Enable Triggered Scope Shot",
        )
        self.add_parameter(
            "trigger_reference",
            unit=self._scope.trigger_reference._unit,
            docstring=self._scope.trigger_reference.__repr__(),
            get_cmd=self._scope.trigger_reference,
            set_cmd=self._scope.trigger_reference,
            label="Trigger Reference Position",
        )
        self.add_parameter(
            "trigger_holdoff",
            unit=self._scope.trigger_holdoff._unit,
            docstring=self._scope.trigger_holdoff.__repr__(),
            get_cmd=self._scope.trigger_holdoff,
            set_cmd=self._scope.trigger_holdoff,
            label="Hold off Time Inbetween Acquiring Triggers",
        )

    def arm(
        self, sync=True, num_records: int = None, averager_weight: int = None
    ) -> None:
        """Prepare the scope for recording.

        This method tells the scope module to be ready to acquire data
        and resets the scope module's progress to 0.0. Optionally, the
        *number of records* and *averager weight* can be set when
        specified as keyword argument. If it is not specified, it is not
        changed.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after preparing scope (default: True).
            num_records (int): The number of scope records to acquire
                (default: None).
            averager_weight (int): Averager weight parameter.
                Averaging is disabled if it is set to 1. For values
                greater than 1, the scope  record shots are averaged
                using an exponentially weighted moving average
                (default: None).

        """
        self._scope.arm(
            sync=sync, num_records=num_records, averager_weight=averager_weight
        )

    def run(self, sync=True) -> None:
        """Run the scope recording.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after enabling the scope (default: True).

        """
        self._scope.run(sync=sync)

    def arm_and_run(self, num_records: int = None, averager_weight: int = None) -> None:
        """Arm the scope and start recording

        Simply combines the methods arm and run. A synchronisation
        is performed between the device and the data server after
        preparing scope.

        Arguments:
            num_records (int): The number of scope records to acquire
                (default: None).
            averager_weight (int): Averager weight parameter.
                Averaging is disabled if it is set to 1. For values
                greater than 1, the scope  record shots are averaged
                using an exponentially weighted moving average
                (default: None).

        """
        self._scope.arm_and_run(
            num_records=num_records, averager_weight=averager_weight
        )

    def stop(self, sync=True) -> None:
        """Stops the scope recording.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after disabling the scope (default: True).

        """
        self._scope.stop(sync=sync)

    def wait_done(self, timeout: float = 10, sleep_time: float = 0.005) -> None:
        """Wait until the Scope recording is finished.

        Arguments:
            timeout (float): The maximum waiting time in seconds for the
                Scope (default: 10).
            sleep_time (float): Time in seconds to wait between
                requesting the progress and records values

        Raises:
            TimeoutError: If the Scope recording is not done before the
                timeout.

        """
        self._scope.wait_done(timeout=timeout, sleep_time=sleep_time)

    def read(
        self,
        channel=None,
        blocking: bool = True,
        timeout: float = 10,
        sleep_time: float = 0.005,
    ):
        """Read out the recorded data from the specified channel of the scope.

        Arguments:
            channel (int): The scope channel to read the data from. If
                no channel is specified, the method will return the data
                for all channels (default: None).
            blocking (bool): A flag that specifies if the program
                should be blocked until the Scope Module has received
                and  processed the desired number of records
                (default: True).
            timeout (float): The maximum waiting time in seconds for the
                Scope (default: 10).
            sleep_time (float): Time in seconds to wait between
                requesting the progress and records values

        Raises:
            TimeoutError: If the Scope recording is not done before the
                timeout.

        Returns:
            A dictionary showing the recorded data and scope time.

        """
        return self._scope.read(
            channel=channel, blocking=blocking, timeout=timeout, sleep_time=sleep_time
        )

    def channels(self, value=None):
        """Set all Scope channels simultaneously.

        Arguments:
            value (tuple): Tuple of values {'on', 'off'} for channel 1
                and 2 (default: None).

        Returns:
            A tuple with the states {'on', 'off'} for all input channels.

        """
        return self._scope.channels(value=value)

    def mode(self, value=None):
        """Set or get scope data processing mode.

        Arguments:
            value (str): Can be either "time" or "FFT" (default: None).

        Returns:
            If no argument is given the method returns the current
            scope data processing mode.

        """
        return self._scope.mode(value=value)

    def num_records(self, value=None):
        """Set or get the number of scope records to acquire.

        Arguments:
            value (int): The number of scope records to acquire
                (default: None).

        Returns:
            If no argument is given the method returns the current
            number of scope records to acquire.

        """
        return self._scope.num_records(value=value)

    def averager_weight(self, value=None):
        """Set or get the averager weight parameter.

        Arguments:
            value (int): Averager weight parameter. Averaging is
                disabled if it is set to 1. For values greater than 1,
                the scope record shots are averaged using an
                exponentially weighted moving average (default: None).

        Returns:
            If no argument is given the method returns the current
            scope data processing mode.

        """
        return self._scope.averager_weight(value=value)

    @property
    def is_running(self):
        return self._scope.is_running


class UHFQA(ZIBaseInstrument):
    """QCoDeS driver for the *Zurich Instruments UHFQA*.

    Inherits from :class:`ZIBaseInstrument`. Initializes some *submodules*
    from the device's nodetree and a device-specific *AWG Core*. It also
    features a :class:`ChannelList` of ten *Readout Channels*
    (:class:`Channel`).

    Arguments:
        name (str): The internal QCoDeS name of the instrument.
        serial (str): The device serial number, e.g. *'dev1234'*.

    Keyword Arguments:
        interface (str): The interface used to connect to the
            device. (default: '1gbe')
        host (str): Address of the data server. (default: 'localhost')
        port (int): Port used to connect to the data server. (default: 8004)
        api (int): Api level used for the data server. (default: 6)

    Attributes:
        awg (:class:`zhinst.qcodes.uhfqa.AWG`): A *UHFQA* specific *AWG Core*.
        channels (:class:`ChannelList`): A list of ten *Readout Channels*
            (:class:`zhinst.qcodes.uhfqa.Channel`).

    """

    def __init__(
        self,
        name: str,
        serial: str,
        interface: str = "1gbe",
        host: str = "localhost",
        port: int = 8004,
        api: int = 6,
        **kwargs,
    ) -> None:
        super().__init__(name, "uhfqa", serial, interface, host, port, api, **kwargs)
        submodules = self.nodetree_dict.keys()
        blacklist = ["awgs", "scopes"]
        [self._init_submodule(key) for key in submodules if key not in blacklist]

    def _connect(self) -> None:
        """Connects the device to the data server.

        Instantiates the device controller from :mod:`zhinst-toolkit`, sets up
        the data server and connects the device the data server. This method is
        called from `__init__` of the :class:`BaseInstrument` class.

        """
        self._controller = tk.UHFQA(
            self._name,
            self._serial,
            interface=self._interface,
            host=self._host,
            port=self._port,
            api=self._api,
        )
        self._controller.setup()
        self._controller.connect_device()
        self.connect_message()
        self.nodetree_dict = self._controller.nodetree._nodetree_dict
        self._init_readout_channels()
        self._init_awg_channels()
        self._init_scope()
        self._add_qcodes_params()

    def _init_readout_channels(self):
        # init submodules for ReadoutChannels
        channel_list = ChannelList(self, "channels", Channel)
        for i in range(10):
            channel_list.append(Channel(f"ch-{i}", i, self, self._controller))
        channel_list.lock()
        self.add_submodule("channels", channel_list)

    def _init_awg_channels(self):
        # init submodule AWG
        self.add_submodule("awg", AWG("awg", self, self._controller))

    def _init_scope(self):
        # init submodule Scope
        self.add_submodule("scope", Scope("scope", self, self._controller))

    def _add_qcodes_params(self):
        # add custom parameters as QCoDeS parameters
        super()._add_qcodes_params()
        self.add_parameter(
            "crosstalk_matrix",
            docstring="The 10x10 crosstalk suppression matrix that multiplies the 10 "
            "signal paths. Can be set only partially.",
            get_cmd=self._controller.crosstalk_matrix,
            set_cmd=self._controller.crosstalk_matrix,
            label="Crosstalk Matrix",
        )
        sources = [
            "Crosstalk",
            "Integration",
            "Threshold",
            "Crosstalk Correlation",
            "Threshold Correlation",
            "Rotation",
        ]
        self.add_parameter(
            "result_source",
            docstring=f"The signal source for QA Results. Has to be one of {sources}.",
            get_cmd=self._controller.result_source,
            set_cmd=self._controller.result_source,
            label="Result Source",
            vals=vals.Enum(*sources),
        )
        self.add_parameter(
            "integration_time",
            unit=self._controller.integration_time._unit,
            docstring=self._controller.integration_time.__repr__(),
            get_cmd=self._controller.integration_time,
            set_cmd=self._controller.integration_time,
            label="Integration Time",
        )
        self.add_parameter(
            "integration_length",
            unit=self._controller.integration_length._unit,
            docstring=self._controller.integration_length.__repr__(),
            get_cmd=self._controller.integration_length,
            set_cmd=self._controller.integration_length,
            label="Integration Length",
        )
        self.add_parameter(
            "averaging_mode",
            docstring=self._controller.averaging_mode._description,
            get_cmd=self._controller.averaging_mode,
            set_cmd=self._controller.averaging_mode,
            label="Averaging Mode",
            vals=vals.Enum("Cyclic", "Sequential"),
        )
        self.add_parameter(
            "qa_delay",
            docstring="The adjustment in the the quantum analyzer delay "
            "in units of samples.",
            get_cmd=self._controller.qa_delay,
            set_cmd=self._controller.qa_delay,
            label="Quantum Analyzer Delay",
            vals=vals.Numbers(),
        )
        self.add_parameter(
            "ref_clock",
            unit=self._controller.ref_clock._unit,
            docstring=self._controller.ref_clock.__repr__(),
            get_cmd=self._controller.ref_clock,
            set_cmd=self._controller.ref_clock,
            label="Intended Reference Clock Source",
        )

    def factory_reset(self, sync=True) -> None:
        """Load the factory default settings.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after loading the factory preset (default: True).

        """
        self._controller.factory_reset(sync=sync)

    def arm(self, length=None, averages=None) -> None:
        """Prepare UHFQA for result acquisition.

        This method enables the QA Results Acquisition and resets the
        acquired points. Optionally, the *result length* and
        *result averages* can be set when specified as keyword
        arguments. If they are not specified,they are not changed.

        Arguments:
            length (int): If specified, the length of the result vector
                will be set before arming the UHFQA readout
                (default: None).
            averages (int): If specified, the result averages will be
                set before arming the UHFQA readout (default: None).

        """
        self._controller.arm(length=length, averages=averages)

    def enable_readout_channels(self, channels: List = range(10)) -> None:
        """Enable weighted integration on the specified readout
         channels.

        Arguments:
            channels (list): A list of indices of channels to enable.
                (default: range(10))

        Raises:
            ValueError: If the channel list contains an element outside
                the allowed range.

        """
        self._controller.enable_readout_channels(channels=channels)

    def disable_readout_channels(self, channels: List = range(10)) -> None:
        """Disable weighted integration on the specified readout
        channels.

        Arguments:
            channels (list): A list of indices of channels to disable.
                (default: range(10))

        Raises:
            ValueError: If the channel list contains an element outside
                the allowed range.

        """
        self._controller.disable_readout_channels(channels=channels)

    def enable_qccs_mode(self) -> None:
        """Configure the instrument to work with PQSC.

        This method sets the reference clock source and DIO settings
        correctly to connect the instrument to the PQSC.
        """
        self._controller.enable_qccs_mode()

    def enable_manual_mode(self) -> None:
        """Disconnect from the PQSC.

        This method sets the reference clock source and DIO settings to
        factory default states and the instrument is disconnected from
        the PQSC.
        """
        self._controller.enable_manual_mode()

    @property
    def allowed_sequences(self):
        return self._controller.allowed_sequences

    @property
    def allowed_trigger_modes(self):
        return self._controller.allowed_trigger_modes
