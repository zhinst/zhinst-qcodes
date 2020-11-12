from .base import ZIBaseInstrument
from qcodes.instrument.channel import ChannelList, InstrumentChannel
import qcodes.utils.validators as vals

import zhinst.toolkit as tk
from zhinst.toolkit.control.drivers.uhfqa import ReadoutChannel, AWG as UHFQA_AWG
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
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "output1",
            unit=self._awg.output1._unit,
            docstring=self._awg.output1.__repr__(),
            get_cmd=self._awg.output1,
            set_cmd=self._awg.output1,
            label="Output Ch 1",
            vals=vals.OnOff(),
        )
        self.add_parameter(
            "output2",
            unit=self._awg.output2._unit,
            docstring=self._awg.output2.__repr__(),
            get_cmd=self._awg.output2,
            set_cmd=self._awg.output2,
            label="Output Ch 2",
            vals=vals.OnOff(),
        )
        self.add_parameter(
            "gain1",
            unit=self._awg.gain1._unit,
            docstring=self._awg.gain1.__repr__(),
            get_cmd=self._awg.gain1,
            set_cmd=self._awg.gain1,
            label="Gain Ch 1",
            vals=vals.Numbers(-1, 1),
        )
        self.add_parameter(
            "gain2",
            unit=self._awg.gain2._unit,
            docstring=self._awg.gain2.__repr__(),
            get_cmd=self._awg.gain2,
            set_cmd=self._awg.gain2,
            label="Gain Ch 2",
            vals=vals.Numbers(-1, 1),
        )

    def run(self) -> None:
        """Runs the *AWG Core*."""
        self._awg.run()

    def stop(self) -> None:
        """Stops the *AWG Core*."""
        self._awg.stop()

    def wait_done(self, timeout: float = 100) -> None:
        """Waits until the *AWG Core* is finished running. 
        
        Keyword Arguments:
            timeout (int): A timeout in seconds after which the AWG is stopped 
                (default: 100)

        """
        self._awg.wait_done(timeout=timeout)

    def compile(self) -> None:
        """Compiles the current *Sequence Program* on the *AWG Core*.
        
        Raises:
            `ToolkitError`: If the *AWG Core* has not been set up yet.
            `ToolkitError`: If the compilation has failed.
            `Warning`: If the compilation has finished with a warning.

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
        
        Uploading custom waveforms is only possible when using the *'Simple'* 
        sequence type. The waveform is specified with two numpy arrays for the 
        two channels of the *AWG Core*. The waveform will then automatically 
        align them to the correct minimum waveform length, sample granularity 
        and scaling. An individual delay can be specified to shift the 
        individual waveform with respect to the time origin of the period.
        
        Arguments:
            wave1 (array like): A list or array of samples in the waveform to be 
                queued for channel 1. An empty list '[]' will upload zeros of 
                the minimum waveform length.
            wave2 (array like): A list or array of samples in the waveform to be 
                queued for channel 2. An empty list '[]' will upload zeros of 
                the minimum waveform length.
        
        Keyword Arguments:
            delay (float): An individual delay for the queued sequence with 
                respect to the time origin. Positive values shift the start of 
                the waveform forwards in time. (default: 0)

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
        
        The new data must have the same length as the previous data s.t. the 
        waveform data can be replaced without recompilation of the sequence 
        program.
        
        Arguments:
            wave1 (array): Waveform to replace current wave for Channel 1.
            wave2 (array): Waveform to replace current wave for Channel 2.
        
        Keyword Arguments:
            i (int): The index of the waveform in the queue to be replaced.
            delay (int): An individual delay in seconds for this waveform w.r.t. 
                the time origin of the sequence. (default: 0)
        
        """
        self._awg.replace_waveform(wave1, wave2, i=i, delay=delay)

    def upload_waveforms(self) -> None:
        """Uploads all waveforms in the queue to the AWG Core.

        This method only works as expected if the Sequence Program is in 
        'Simple' mode and has been compiled beforehand.
        
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
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "rotation",
            unit=self._channel.rotation._unit,
            docstring=self._channel.rotation.__repr__(),
            get_cmd=self._channel.rotation,
            set_cmd=self._channel.rotation,
            label="Rotation",
            vals=vals.Numbers(),
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
            docstring="Readout frequency of the channel. Is used to create a readout tone and to set the integration weights.",
            get_cmd=self._channel.readout_frequency,
            set_cmd=self._channel.readout_frequency,
            label="Readout Frequency",
            vals=vals.Numbers(0),
        )
        self.add_parameter(
            "readout_amplitude",
            unit="Hz",
            docstring="The amplitude of the readout tone associated with this channel. Used in a 'Readout' sequence.",
            get_cmd=self._channel.readout_amplitude,
            set_cmd=self._channel.readout_amplitude,
            label="Readout Amplitude",
            vals=vals.Numbers(),
        )
        self.add_parameter(
            "phase_shift",
            unit="Hz",
            docstring="The phase shift of the readout tone associated with this channel. Used in a 'Readout' sequence.",
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
        self.add_parameter(
            "enabled",
            unit="Boolean",
            docstring="Enable or disable the weighted integration for this readout channel with 'channel.enable()' or 'channel.disable()'.",
            get_cmd=self._channel.enabled,
            label="Enabled",
            vals=vals.Bool(),
        )

    def enabled(self) -> None:
        """Returns if weighted integration is enabled."""
        return self._channel.enabled()

    def enable(self) -> None:
        """
        Enables the readout channel. This enables weighted integration mode, 
        sets the itnegration time to its default (2 us) and sets the 
        corresponding integration weights to demodulate at the given readout 
        frequency.

        """
        self._channel.enable()

    def disable(self) -> None:
        """
        Disables the readout channel and resets the integration weigths 
        corresponding to this channel.
        
        """
        self._channel.disable()

    @property
    def index(self):
        return self._channel.index


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
        blacklist = [
            "awgs",
            "scopes",
        ]
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
        self._controller.connect_device(nodetree=False)
        self.connect_message()
        self._get_nodetree_dict()
        # init submodules for ReadoutChannels and AWG
        channel_list = ChannelList(self, "channels", Channel)
        for i in range(10):
            channel_list.append(Channel(f"ch-{i}", i, self, self._controller))
        channel_list.lock()
        self.add_submodule("channels", channel_list)
        self.add_submodule("awg", AWG("awg", self, self._controller))
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "crosstalk_matrix",
            docstring="The 10x10 crosstalk suppression matrix that multiplies the 10 signal paths. Can be set only partially.",
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
            docstring="The integration time used for demodulation in seconds. Can be up to 2.27 us when using weighted integration and up to 50 us in spectroscopy mode.",
            get_cmd=self._controller.integration_time,
            set_cmd=self._controller.integration_time,
            label="Integration Time",
            vals=vals.Numbers(0, 50e-6),
        )
        self.add_parameter(
            "averaging_mode",
            docstring=self._controller.averaging_mode._description,
            get_cmd=self._controller.averaging_mode,
            set_cmd=self._controller.averaging_mode,
            label="Averaging Mode",
            vals=vals.Enum("Cyclic", "Sequential"),
        )

    def arm(self, length=None, averages=None) -> None:
        """Prepare UHFQA for result acquisition.

        This method enables the QA Results Acquisition and resets the acquired 
        points. Optionally, the *result length* and *result averages* can be set 
        when specified as keyword arguments. If they are not specified, they are 
        not changed.  

        Keyword Arguments:
            length (int): If specified, the length of the result vector will be 
                set before arming the UHFQA readout. (default: None)
            averages (int): If specified, the result averages will be set before 
                arming the UHFQA readout. (default: None)

        """
        self._controller.arm(length=length, averages=averages)

    def enable_readout_channels(self, channels: List = range(10)) -> None:
        """Enables weighted integration on the specified readout channels.
        
        Keyword Arguments:
            channels (list): A list of indices of channels to enable. 
                (default: range(10))
        
        """
        self._controller.enable_readout_channels(channels=channels)

    def disable_readout_channels(self, channels: List = range(10)) -> None:
        """Disables weighted integration on the specified readout channels.
        
        Keyword Arguments:
            channels (list): A list of indices of channels to disable. 
                (default: range(10))
        
        """
        self._controller.disable_readout_channels(channels=channels)
