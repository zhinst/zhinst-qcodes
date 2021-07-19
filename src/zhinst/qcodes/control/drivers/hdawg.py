from .base import ZIBaseInstrument
import zhinst.toolkit as tk
from zhinst.toolkit.control.drivers.hdawg import AWG as HDAWG_AWG, CT as HDAWG_CT

from qcodes.instrument.channel import ChannelList, InstrumentChannel
import qcodes.utils.validators as vals
from typing import List, Dict, Union
import numpy as np


class AWG(InstrumentChannel):
    """Device-specific *AWG Core* for the *HDAWG*.

    Inherits from :class:`InstrumentChannel` and wraps around a `AWGCore` for
    *HDAWG* from :mod:`zhinst-toolkit`. This class adds *Parameters* from the
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
        output1 (:class:`Parameter`): State of the output 1, i.e. one of
            {'on', 'off'}.
        output2 (:class:`Parameter`): State of the output 2, i.e. one of
            {'on', 'off'}.
        modulation_freq (:class:`Parameter`): Frequency of the modulation in
            Hz if IQ modulation is enabled.
        modulation_phase_shift (:class:`Parameter`): Phase shift in degrees
            between I and Q quadratures if IQ modulation is enabled
            (default: 90).
        gain1 (:class:`Parameter`): Gain of the output channel 1 if IQ
            modulation is enabled. Must be between -1 and +1 (default: +1).
        gain2 (:class:`Parameter`): Gain of the output channel 2 if IQ
            modulation is enabled. Must be between -1 and +1 (default: +1).
        waveforms (list): A list of `Waveforms` that respresent the queue of
            waveforms to upload to the device when the sequence type is
            *'Simple'*.
        is_running (bool): A flag that shows if the `AWG Core` is currently
            running or not.
        index (int): The index of the `AWG Core` in the list of *awgs*.

    """

    def __init__(self, name: str, index: int, parent_instr, parent_contr) -> None:
        InstrumentChannel.__init__(self, parent_instr, name)
        self._awg = HDAWG_AWG(parent_contr, index)
        self._awg._setup()
        self._awg._init_awg_params()
        self._add_qcodes_awg_params()
        self._init_ct()

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
            "modulation_phase_shift",
            unit=self._awg.modulation_phase_shift._unit,
            docstring=self._awg.modulation_phase_shift.__repr__(),
            get_cmd=self._awg.modulation_phase_shift,
            set_cmd=self._awg.modulation_phase_shift,
            label="Modulation Phase Shift",
            vals=vals.Numbers(),
        )
        self.add_parameter(
            "modulation_freq",
            unit=self._awg.modulation_freq._unit,
            docstring=self._awg.modulation_freq.__repr__(),
            get_cmd=self._awg.modulation_freq,
            set_cmd=self._awg.modulation_freq,
            label="Modulation Frequency",
            vals=vals.Numbers(),
        )
        self.add_parameter(
            "single",
            unit=self._awg.single._unit,
            docstring=self._awg.single.__repr__(),
            get_cmd=self._awg.single,
            set_cmd=self._awg.single,
            label="Single Run",
        )
        self.add_parameter(
            "zsync_register_mask",
            unit=self._awg.zsync_register_mask._unit,
            docstring=self._awg.zsync_register_mask.__repr__(),
            get_cmd=self._awg.zsync_register_mask,
            set_cmd=self._awg.zsync_register_mask,
            label="ZSYNC Register Mask",
        )
        self.add_parameter(
            "zsync_register_shift",
            unit=self._awg.zsync_register_shift._unit,
            docstring=self._awg.zsync_register_shift.__repr__(),
            get_cmd=self._awg.zsync_register_shift,
            set_cmd=self._awg.zsync_register_shift,
            label="ZSYNC Register Shift",
        )
        self.add_parameter(
            "zsync_register_offset",
            unit=self._awg.zsync_register_offset._unit,
            docstring=self._awg.zsync_register_offset.__repr__(),
            get_cmd=self._awg.zsync_register_offset,
            set_cmd=self._awg.zsync_register_offset,
            label="ZSYNC Register Offset",
        )
        self.add_parameter(
            "zsync_decoder_mask",
            unit=self._awg.zsync_decoder_mask._unit,
            docstring=self._awg.zsync_decoder_mask.__repr__(),
            get_cmd=self._awg.zsync_decoder_mask,
            set_cmd=self._awg.zsync_decoder_mask,
            label="ZSYNC Decoder Mask",
        )
        self.add_parameter(
            "zsync_decoder_shift",
            unit=self._awg.zsync_decoder_shift._unit,
            docstring=self._awg.zsync_decoder_shift.__repr__(),
            get_cmd=self._awg.zsync_decoder_shift,
            set_cmd=self._awg.zsync_decoder_shift,
            label="ZSYNC Decoder Shift",
        )
        self.add_parameter(
            "zsync_decoder_offset",
            unit=self._awg.zsync_decoder_offset._unit,
            docstring=self._awg.zsync_decoder_offset.__repr__(),
            get_cmd=self._awg.zsync_decoder_offset,
            set_cmd=self._awg.zsync_decoder_offset,
            label="ZSYNC Decoder Offset",
        )

    def _init_ct(self):
        # init submodule for CT
        self.add_submodule(
            "ct",
            CT(
                "ct",
                self,
                self._awg,
                "https://docs.zhinst.com/hdawg/commandtable/v2/schema",
            ),
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

    def enable_iq_modulation(self) -> None:
        """Enables IQ Modulation by on the *AWG Core*.

        This method applies the corresponding settings for IQ modulation using
        one of the internal oscillators and two sine generators. The sines are
        used to modulate the AWG output channels. The *parameters*
        `modulation_freq`, `modulation_phase_shift` and `gain1`, `gain2`
        correspond to the settings of the oscillator and the sine generators.

        """
        self._awg.enable_iq_modulation()

    def disable_iq_modulation(self) -> None:
        """Disables IQ modulation on the *AWG Core*.

        Resets the settings of the sine generators and the AWG modulation.

        """
        self._awg.disable_iq_modulation()

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

    def sequence_params(self) -> Dict:
        """Returns the current sequence parameters.

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


class CT(InstrumentChannel):
    """Device-specific CommandTable for HDAWG."""

    def __init__(self, name: str, parent_instr, parent_contr, ct_schema_url) -> None:
        super().__init__(parent_instr, name)
        self._ct = HDAWG_CT(parent_contr, ct_schema_url)

    def load(self, table):
        """Load a given command table to the instrument"""
        self._ct.load(table)


class HDAWG(ZIBaseInstrument):
    """QCoDeS driver for the *Zurich Instruments HDAWG*.

    Inherits from :class:`ZIBaseInstrument`. Initializes some *submodules*
    from the device's nodetree and a :class:`ChannelList` of device-specific
    `AWGs` for high-level control of the *AWG Cores*.

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
        awgs (:class:`ChannelList`): A list of four *HDAWG* specific
            *AWG Cores* (:class:`zhinst.qcodes.hdawg.AWG`).

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
        super().__init__(name, "hdawg", serial, interface, host, port, api, **kwargs)
        submodules = self.nodetree_dict.keys()
        # initialize submodules from nodetree with blacklist
        blacklist = ["awgs"]
        [self._init_submodule(key) for key in submodules if key not in blacklist]

    def _connect(self) -> None:
        """Connects the device to the data server.

        Instantiates the device controller from :mod:`zhinst-toolkit`, sets up
        the data server and connects the device the data server. This method is
        called from `__init__` of the :class:`BaseInstrument` class.

        """
        self._controller = tk.HDAWG(
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
        self._init_awg_channels()
        self._add_qcodes_params()

    def _init_awg_channels(self):
        # initialize ChannelList of AWGs
        channel_list = ChannelList(self, "awgs", AWG)
        for i in range(4):
            channel_list.append(AWG(f"awg-{i}", i, self, self._controller))
        channel_list.lock()
        self.add_submodule("awgs", channel_list)

    def _add_qcodes_params(self):
        # add custom parameters as QCoDeS parameters
        super()._add_qcodes_params()
        self.add_parameter(
            "ref_clock",
            unit=self._controller.ref_clock._unit,
            docstring=self._controller.ref_clock.__repr__(),
            get_cmd=self._controller.ref_clock,
            set_cmd=self._controller.ref_clock,
            label="Intended Reference Clock Source",
        )
        self.add_parameter(
            "ref_clock_status",
            unit=self._controller.ref_clock_status._unit,
            docstring=self._controller.ref_clock_status.__repr__(),
            get_cmd=self._controller.ref_clock_status,
            set_cmd=self._controller.ref_clock_status,
            label="Status Reference Clock",
        )

    def factory_reset(self, sync=True) -> None:
        """Load the factory default settings.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after loading the factory preset (default: True).

        """
        self._controller.factory_reset(sync=sync)

    def enable_qccs_mode(self) -> None:
        """Configure the instrument to work with PQSC

        This method sets the reference clock source and DIO settings
        correctly to connect the instrument to the PQSC.
        """
        self._controller.enable_qccs_mode()

    def enable_manual_mode(self) -> None:
        """Disconnect from PQSC

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
