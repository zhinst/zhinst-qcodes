from .base import ZIBaseInstrument
from qcodes.instrument.channel import ChannelList, InstrumentChannel

import zhinst.toolkit as tk
from zhinst.toolkit.control.drivers.shfqa import (
    Channel as SHFQA_Channel,
    Generator as SHFQA_Generator,
    Sweeper as SHFQA_Sweeper,
    Scope as SHFQA_Scope,
)
from typing import List, Dict, Union
import numpy as np


class Channel(InstrumentChannel):
    """Device-specific *Channel* for the *SHFQA*."""

    def __init__(self, name: str, index: int, parent_instr, parent_contr) -> None:
        super().__init__(parent_instr, name)
        self._channel = SHFQA_Channel(parent_contr, index)
        self._channel._init_channel_params()
        self._add_qcodes_channel_params()
        self._init_generator()
        self._init_sweeper()

    def _add_qcodes_channel_params(self):
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "input",
            docstring=self._channel.input.__repr__(),
            get_cmd=self._channel.input,
            set_cmd=self._channel.input,
            label="Enable Signal Input",
        )
        self.add_parameter(
            "input_range",
            unit=self._channel.input_range._unit,
            docstring=self._channel.input_range.__repr__(),
            get_cmd=self._channel.input_range,
            set_cmd=self._channel.input_range,
            label="Maximal Range of the Signal Input Power",
        )
        self.add_parameter(
            "output",
            docstring=self._channel.output.__repr__(),
            get_cmd=self._channel.output,
            set_cmd=self._channel.output,
            label="Enable Signal Output",
        )
        self.add_parameter(
            "output_range",
            unit=self._channel.output_range._unit,
            docstring=self._channel.output_range.__repr__(),
            get_cmd=self._channel.output_range,
            set_cmd=self._channel.output_range,
            label="Maximal Range of the Signal Output Power",
        )
        self.add_parameter(
            "center_freq",
            unit=self._channel.center_freq._unit,
            docstring=self._channel.center_freq.__repr__(),
            get_cmd=self._channel.center_freq,
            set_cmd=self._channel.center_freq,
            label="Center Frequency of the Analysis Band",
        )
        self.add_parameter(
            "mode",
            docstring=self._channel.mode.__repr__(),
            get_cmd=self._channel.mode,
            set_cmd=self._channel.mode,
            label="Spectroscopy or Qubit Readout Mode Selection",
        )

    def _init_generator(self):
        # init submodule for Generator
        self.add_submodule("generator", Generator("generator", self, self._channel))

    def _init_sweeper(self):
        # init submodule for Sweeper
        self.add_submodule("sweeper", Sweeper("sweeper", self, self._channel))


class Generator(InstrumentChannel):
    """Device-specific *Generator* for the *SHFQA*."""

    def __init__(self, name: str, parent_instr, parent_contr) -> None:
        super().__init__(parent_instr, name)
        self._generator = SHFQA_Generator(parent_contr)
        self._generator._setup()
        self._generator._init_generator_params()
        self._add_qcodes_generator_params()

    def _add_qcodes_generator_params(self):
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "enable",
            docstring=self._generator.enable.__repr__(),
            get_cmd=self._generator.enable,
            set_cmd=self._generator.enable,
            label="Enable the Sequencer",
        )
        self.add_parameter(
            "dig_trigger1_source",
            docstring=self._generator.dig_trigger1_source.__repr__(),
            get_cmd=self._generator.dig_trigger1_source,
            set_cmd=self._generator.dig_trigger1_source,
            label="Digital Trigger 1 Source",
        )
        self.add_parameter(
            "dig_trigger2_source",
            docstring=self._generator.dig_trigger2_source.__repr__(),
            get_cmd=self._generator.dig_trigger2_source,
            set_cmd=self._generator.dig_trigger2_source,
            label="Digital Trigger 2 Source",
        )
        self.add_parameter(
            "ready",
            docstring=self._generator.ready.__repr__(),
            get_cmd=self._generator.ready,
            set_cmd=self._generator.ready,
            label="Sequencer is Ready",
        )

    def run(self) -> None:
        """Run the generator."""
        self._generator.run()

    def stop(self) -> None:
        """Stops the generator."""
        self._generator.stop()

    def wait_done(self, timeout: float = 10) -> None:
        """Waits until the Generator is finished.

        Keyword Arguments:
            timeout (int): The maximum waiting time in seconds for the
                Generator (default: 10).

        """
        self._generator.wait_done(timeout)

    def compile(self) -> None:
        """Compile the current SequenceProgram and load it to sequencer."""
        return self._generator.compile()

    def reset_queue(self) -> None:
        """Resets the waveform queue to an empty list."""
        self._generator.reset_queue()

    def queue_waveform(self, wave: Union[List, np.array], delay: float = 0) -> None:
        """Add a new waveform to the queue.

        Arguments:
            wave (array): The waveform to be queued as a 1D numpy array.

        Keyword Arguments:
            delay (int): An individual delay in seconds for this waveform
                w.r.t. the time origin of the sequence. (default: 0)

        Raises:
            Exception: If the sequence is not of type *'Custom'*.
        """
        self._generator.queue_waveform(wave, delay=delay)

    def upload_waveforms(self) -> None:
        """Upload all waveforms in the queue to the Generator.

        This method only works as expected if the Sequence Program has
        been compiled beforehand.
        See :func:`compile_and_upload_waveforms(...)`.

        """
        self._generator.upload_waveforms()

    def compile_and_upload_waveforms(self) -> None:
        """Compiles the Sequence Program and uploads the queued waveforms.

        Simply combines the two methods to make sure the sequence is compiled
        before the waveform queue is uplaoded.

        """
        self._generator.compile_and_upload_waveforms()

    def set_sequence_params(self, **kwargs) -> None:
        """Sets the parameters of the Sequence Program.

        Passes all the keyword arguments to the `set_param(...)` method
        of the Sequence Program. The available sequence parameters may
        vary between different sequences. For a list of all current
        sequence parameters see the property `sequence_params`.

        They include *'sequence_type'*, *'period'*, *'repetitions'*,
        *'trigger_mode'*, *'trigger_delay'*, ...

            >>> shfqa.channels[0].generator.set_sequence_params(
            >>>     sequence_type="Custom",
            >>>     program = seqc_program_string,
            >>>     custom_params = [param1, param2],
            >>> )

        """
        self._generator.set_sequence_params(**kwargs)

    @property
    def name(self):
        return self._generator.name

    @property
    def waveforms(self):
        return self._generator.waveforms

    @property
    def is_running(self):
        return self._generator.is_running

    @property
    def sequence_params(self):
        return self._generator.sequence_params


class Sweeper(InstrumentChannel):
    """Device-specific *Sweeper* for the *SHFQA*."""

    def __init__(self, name: str, parent_instr, parent_contr) -> None:
        super().__init__(parent_instr, name)
        self._sweeper = SHFQA_Sweeper(parent_contr)
        self._sweeper._init_sweeper_params()
        self._add_qcodes_sweeper_params()

    def _add_qcodes_sweeper_params(self):
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "oscillator_gain",
            unit=self._sweeper.oscillator_gain._unit,
            docstring=self._sweeper.oscillator_gain.__repr__(),
            get_cmd=self._sweeper.oscillator_gain,
            set_cmd=self._sweeper.oscillator_gain,
            label="Gain of Digital Oscillator",
        )
        self.add_parameter(
            "integration_time",
            unit=self._sweeper.integration_time._unit,
            docstring=self._sweeper.integration_time.__repr__(),
            get_cmd=self._sweeper.integration_time,
            set_cmd=self._sweeper.integration_time,
            label="Integration Time",
        )
        self.add_parameter(
            "integration_length",
            unit=self._sweeper.integration_length._unit,
            docstring=self._sweeper.integration_length.__repr__(),
            get_cmd=self._sweeper.integration_length,
            set_cmd=self._sweeper.integration_length,
            label="Integration Length",
        )

    def trigger_source(self, source=None):
        """Set or get the trigger source for the sweeper.

        Keyword Arguments:
            source (str): Trigger source of the sweeper
                (default: None).

        """
        return self._sweeper.trigger_source(source)

    def trigger_level(self, level=None):
        """Set or get the trigger level for the sweeper.

        Keyword Arguments:
            level (float): Trigger level of the sweeper
                (default: None).

        """
        return self._sweeper.trigger_level(level)

    def trigger_imp50(self, imp50=None):
        """Set or get the trigger input impedance setting for the sweeper.

        Keyword Arguments:
            imp50 (bool): Trigger input impedance selection for the
                sweeper. When set to True, the trigger input impedance is
                50 Ohm. When set to False, it is 1 kOhm (default: None).

        """
        return self._sweeper.trigger_imp50(imp50)

    def start_frequency(self, freq=None):
        """Set or get the start frequency for the sweeper.

        Keyword Arguments:
            freq (float): Start frequency in Hz of the sweeper
                (default: None).

        """
        return self._sweeper.start_frequency(freq)

    def stop_frequency(self, freq=None):
        """Set or get the stop frequency for the sweeper.

        Keyword Arguments:
            freq (float): Stop frequency in Hz of the sweeper
                (default: None).

        """
        return self._sweeper.stop_frequency(freq)

    def num_points(self, num=None):
        """Set or get the number of points for the sweeper.

        Keyword Arguments:
            num (int): Number of frequency points to sweep between
                start and stop frequency values (default: None).
        """
        return self._sweeper.num_points(num)

    def mapping(self, map=None):
        """Set or get the mapping configuration for the sweeper.

        Keyword Arguments:
            map (str): Mapping that specifies the distances between
                frequency points of the sweeper. Can be either "linear"
                or "log" (default: None).
        """
        return self._sweeper.mapping(map)

    def num_averages(self, num=None):
        """Set or get the number of averages for the sweeper.

        Number of averages specifies how many times a frequency point
        will be measured and averaged.

        Keyword Arguments:
            num (int): Number of times the sweeper measures one
                frequency point (default: None).
        """
        return self._sweeper.num_averages(num)

    def averaging_mode(self, mode=None):
        """Set or get the averaging mode for the sweeper.

        Keyword Arguments:
            mode (str): Averaging mode for the sweeper.
        Can be either "pointwise" or "sweepwise".
            "pointwise": A frequency point is measured the number of
                times specified by the number of samples setting. In
                other words, the same frequency point is measured
                repeatedly until the number of samples is reached and
                the sweeper then moves to the next frequency point.
            "sweepwise": All frequency points are measured once from
                start frequency to stop frequency. The sweeper then
                moves back to start frequency and repeats the sweep
                the number of times specified by the number of samples
                setting.
            (default: None).
        """
        return self._sweeper.averaging_mode(mode)

    def run(self):
        """Perform a sweep with the specified settings."""
        return self._sweeper.run()

    def get_result(self):
        """Get the measurement data of the last sweep.

        Returns:
             A dictionary with measurement data of the last sweep
        """
        return self._sweeper.get_result()

    def plot(self):
        """Plot power over frequency for last sweep."""
        return self._sweeper.plot()


class Scope(InstrumentChannel):
    """Device-specific *Scope* for the *SHFQA*."""

    def __init__(self, name: str, parent_instr, parent_contr) -> None:
        super().__init__(parent_instr, name)
        self._scope = SHFQA_Scope(parent_contr)
        self._scope._init_scope_params()
        self._add_qcodes_scope_params()

    def _add_qcodes_scope_params(self):
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "enable",
            docstring=self._scope.enable.__repr__(),
            get_cmd=self._scope.enable,
            set_cmd=self._scope.enable,
            label="Enable Acquisition of Scope Shots",
        )
        self.add_parameter(
            "channel1",
            docstring=self._scope.channel1.__repr__(),
            get_cmd=self._scope.channel1,
            set_cmd=self._scope.channel1,
            label="Enable Recording for Scope Channel 1",
        )
        self.add_parameter(
            "channel2",
            docstring=self._scope.channel2.__repr__(),
            get_cmd=self._scope.channel2,
            set_cmd=self._scope.channel2,
            label="Enable Recording for Scope Channel 2",
        )
        self.add_parameter(
            "channel3",
            docstring=self._scope.channel3.__repr__(),
            get_cmd=self._scope.channel3,
            set_cmd=self._scope.channel3,
            label="Enable Recording for Scope Channel 3",
        )
        self.add_parameter(
            "channel4",
            docstring=self._scope.channel4.__repr__(),
            get_cmd=self._scope.channel4,
            set_cmd=self._scope.channel4,
            label="Enable Recording for Scope Channel 4",
        )
        self.add_parameter(
            "input_select1",
            docstring=self._scope.input_select1.__repr__(),
            get_cmd=self._scope.input_select1,
            set_cmd=self._scope.input_select1,
            label="Select Input Signal for Scope Channel 1",
        )
        self.add_parameter(
            "input_select2",
            docstring=self._scope.input_select2.__repr__(),
            get_cmd=self._scope.input_select2,
            set_cmd=self._scope.input_select2,
            label="Select Input Signal for Scope Channel 2",
        )
        self.add_parameter(
            "input_select3",
            docstring=self._scope.input_select3.__repr__(),
            get_cmd=self._scope.input_select3,
            set_cmd=self._scope.input_select3,
            label="Select Input Signal for Scope Channel 3",
        )
        self.add_parameter(
            "input_select4",
            docstring=self._scope.input_select4.__repr__(),
            get_cmd=self._scope.input_select4,
            set_cmd=self._scope.input_select4,
            label="Select Input Signal for Scope Channel 4",
        )
        self.add_parameter(
            "wave1",
            docstring=self._scope.wave1.__repr__(),
            get_cmd=self._scope.wave1,
            set_cmd=self._scope.wave1,
            label="Scope Channel 1 Acquired Wave Data",
        )
        self.add_parameter(
            "wave2",
            docstring=self._scope.wave2.__repr__(),
            get_cmd=self._scope.wave2,
            set_cmd=self._scope.wave2,
            label="Scope Channel 2 Acquired Wave Data",
        )
        self.add_parameter(
            "wave3",
            docstring=self._scope.wave3.__repr__(),
            get_cmd=self._scope.wave3,
            set_cmd=self._scope.wave3,
            label="Scope Channel 3 Acquired Wave Data",
        )
        self.add_parameter(
            "wave4",
            docstring=self._scope.wave4.__repr__(),
            get_cmd=self._scope.wave4,
            set_cmd=self._scope.wave4,
            label="Scope Channel 4 Acquired Wave Data",
        )
        self.add_parameter(
            "trigger_source",
            docstring=self._scope.trigger_source.__repr__(),
            get_cmd=self._scope.trigger_source,
            set_cmd=self._scope.trigger_source,
            label="Scope Trigger Source",
        )
        self.add_parameter(
            "trigger_delay",
            unit=self._scope.trigger_delay._unit,
            docstring=self._scope.trigger_delay.__repr__(),
            get_cmd=self._scope.trigger_delay,
            set_cmd=self._scope.trigger_delay,
            label="Scope Trigger Delay",
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
            "time",
            unit=self._scope.time._unit,
            docstring=self._scope.time.__repr__(),
            get_cmd=self._scope.time,
            set_cmd=self._scope.time,
            label="Time Base of the Scope",
        )
        self.add_parameter(
            "segments_enable",
            unit=self._scope.segments_enable._unit,
            docstring=self._scope.segments_enable.__repr__(),
            get_cmd=self._scope.segments_enable,
            set_cmd=self._scope.segments_enable,
            label="Enable Segmented Scope Recording",
        )
        self.add_parameter(
            "segments_count",
            unit=self._scope.segments_count._unit,
            docstring=self._scope.segments_count.__repr__(),
            get_cmd=self._scope.segments_count,
            set_cmd=self._scope.segments_count,
            label="Number of Segments to Record",
        )
        self.add_parameter(
            "averaging_enable",
            unit=self._scope.averaging_enable._unit,
            docstring=self._scope.averaging_enable.__repr__(),
            get_cmd=self._scope.averaging_enable,
            set_cmd=self._scope.averaging_enable,
            label="Enable Averaged Scope Recording",
        )
        self.add_parameter(
            "averaging_count",
            unit=self._scope.averaging_count._unit,
            docstring=self._scope.averaging_count.__repr__(),
            get_cmd=self._scope.averaging_count,
            set_cmd=self._scope.averaging_count,
            label="Number of Averages",
        )

    def run(self) -> None:
        """Runs the scope recording."""
        self._scope.run()

    def stop(self) -> None:
        """Stops the scope recording."""
        self._scope.stop()

    def read(self, channel=None):
        """Read out the recorded data from the specified channel of the scope.

        Arguments:
            channel (int): The scope channel to read the data from. If
                no channel is specified, the method will return the data
                for all channels.

        Returns:
            A dictionary showing the recorded data and scope time.
        """
        return self._scope.read(channel)

    def channels(self, value=None):
        """Set all Scope channels simultaneously.

        Keyword Arguments:
            value (tuple): Tuple of values {'on', 'off'} for channel 1,
            2, 3 and 4 (default: None).

        Returns:
            A tuple with the states {'on', 'off'} for all input channels.

        """
        return self._scope.channels(value)

    def input_select(self, value=None):
        """Set all Scope input signals simultaneously.

        Keyword Arguments:
            value (tuple): Tuple of values for input signal 1,
            2, 3 and 4. The accepted values can be found in SHFQA
            user manual (default: None).

        Returns:
            A tuple with the selected input signal sources for all
            input channels.

        """
        return self._scope.input_select(value)

    def segments(self, enable=None, count=None):
        """Configure segmented Scope recording options.

        Keyword Arguments:
            enable (bool): a flag that specifies whether segmented Scope
                recording is enabled (default: None).
            count (int): number of segments in device memory (default: None)

        Returns:
            A dictionary showing the enable state and segment count
        """
        return self._scope.segments(enable, count)

    def averaging(self, enable=None, count=None):
        """Configure averaging options of Scope measurements.

        Keyword Arguments:
            enable (bool): a flag that specifies whether averaging of
                Scope measurements is enabled (default: None).
            count (int): number of Scope measurements to average
                (default: None)

        Returns:
            A dictionary showing the enable state and averaging count
        """
        return self._scope.averaging(enable, count)


class SHFQA(ZIBaseInstrument):
    """QCoDeS driver for the *Zurich Instruments SHFQA*"""

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
        super().__init__(name, "shfqa", serial, interface, host, port, api, **kwargs)
        submodules = self.nodetree_dict.keys()
        blacklist = [
            "qachannels",
            "scopes",
        ]
        [self._init_submodule(key) for key in submodules if key not in blacklist]

    def _connect(self) -> None:
        """Connects the device to the data server.

        Instantiates the device controller from :mod:`zhinst-toolkit`, sets up
        the data server and connects the device the data server. This method is
        called from `__init__` of the :class:`BaseInstrument` class.

        """
        self._controller = tk.SHFQA(
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
        self._init_channels()
        self._init_scope()
        self._add_qcodes_params()

    def _init_channels(self):
        # init submodules for Channels
        num_channels = self._controller._num_channels()
        channel_list = ChannelList(self, "channels", Channel)
        for i in range(num_channels):
            channel_list.append(Channel(f"ch-{i}", i, self, self._controller))
        channel_list.lock()
        self.add_submodule("channels", channel_list)

    def _init_scope(self):
        # init submodule AWG
        self.add_submodule("scope", Scope("scope", self, self._controller))

    def _add_qcodes_params(self):
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "ref_clock",
            unit=self._controller.ref_clock._unit,
            docstring=self._controller.ref_clock.__repr__(),
            get_cmd=self._controller.ref_clock,
            set_cmd=self._controller.ref_clock,
            label="Intended Reference Clock Source",
        )
        self.add_parameter(
            "ref_clock_actual",
            unit=self._controller.ref_clock_actual._unit,
            docstring=self._controller.ref_clock_actual.__repr__(),
            get_cmd=self._controller.ref_clock_actual,
            set_cmd=self._controller.ref_clock_actual,
            label="Actual Reference Clock Source",
        )
        self.add_parameter(
            "ref_clock_status",
            unit=self._controller.ref_clock_status._unit,
            docstring=self._controller.ref_clock_status.__repr__(),
            get_cmd=self._controller.ref_clock_status,
            set_cmd=self._controller.ref_clock_status,
            label="Status Reference Clock",
        )
        self.add_parameter(
            "timebase",
            unit=self._controller.timebase._unit,
            docstring=self._controller.timebase.__repr__(),
            get_cmd=self._controller.timebase,
            set_cmd=self._controller.timebase,
            label="Minimal Time Difference Between Two Timestamps.",
        )

    def factory_reset(self) -> None:
        """Load the factory default settings."""
        self._controller.factory_reset()

    def set_trigger_loopback(self):
        """Start a trigger pulse using the internal loopback.

        Start a 1kHz continuous trigger pulse from marker 1 A using the
        internal loopback to trigger in 1 A.

        """
        self._controller.set_trigger_loopback()

    def check_ref_clock(self, blocking=True, timeout=30) -> None:
        """Check if reference clock is locked succesfully.

        Keyword Arguments:
            blocking (bool): A flag that specifies if the program should
                be blocked until the reference clock is 'locked'.
                (default: True)
            timeout (int): Maximum time in seconds the program waits
                when `blocking` is set to `True`. (default: 30)

        """
        self._controller.check_ref_clock(blocking=blocking, timeout=timeout)
