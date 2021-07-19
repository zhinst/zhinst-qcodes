from .base import ZIBaseInstrument
from qcodes.instrument.channel import ChannelList, InstrumentChannel

import zhinst.toolkit as tk
from zhinst.toolkit.control.drivers.shfqa import (
    QAChannel as SHFQA_QAChannel,
    Generator as SHFQA_Generator,
    Readout as SHFQA_Readout,
    Integration as SHFQA_Integration,
    Sweeper as SHFQA_Sweeper,
    Scope as SHFQA_Scope,
)
from typing import List, Dict, Union
import numpy as np


class QAChannel(InstrumentChannel):
    """Device-specific *QAChannel* for the *SHFQA*."""

    def __init__(self, name: str, index: int, parent_instr, parent_contr) -> None:
        super().__init__(parent_instr, name)
        self._qachannel = SHFQA_QAChannel(parent_contr, index)
        self._qachannel._init_qachannel_params()
        self._add_qcodes_qachannel_params()
        self._init_generator()
        self._init_readout()
        self._init_sweeper()

    def _add_qcodes_qachannel_params(self):
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "input",
            docstring=self._qachannel.input.__repr__(),
            get_cmd=self._qachannel.input,
            set_cmd=self._qachannel.input,
            label="Enable Signal Input",
        )
        self.add_parameter(
            "input_range",
            unit=self._qachannel.input_range._unit,
            docstring=self._qachannel.input_range.__repr__(),
            get_cmd=self._qachannel.input_range,
            set_cmd=self._qachannel.input_range,
            label="Maximal Range of the Signal Input Power",
        )
        self.add_parameter(
            "output",
            docstring=self._qachannel.output.__repr__(),
            get_cmd=self._qachannel.output,
            set_cmd=self._qachannel.output,
            label="Enable Signal Output",
        )
        self.add_parameter(
            "output_range",
            unit=self._qachannel.output_range._unit,
            docstring=self._qachannel.output_range.__repr__(),
            get_cmd=self._qachannel.output_range,
            set_cmd=self._qachannel.output_range,
            label="Maximal Range of the Signal Output Power",
        )
        self.add_parameter(
            "center_freq",
            unit=self._qachannel.center_freq._unit,
            docstring=self._qachannel.center_freq.__repr__(),
            get_cmd=self._qachannel.center_freq,
            set_cmd=self._qachannel.center_freq,
            label="Center Frequency of the Analysis Band",
        )
        self.add_parameter(
            "mode",
            docstring=self._qachannel.mode.__repr__(),
            get_cmd=self._qachannel.mode,
            set_cmd=self._qachannel.mode,
            label="Spectroscopy or Qubit Readout Mode Selection",
        )

    def _init_generator(self):
        # init submodule for Generator
        self.add_submodule("generator", Generator("generator", self, self._qachannel))

    def _init_readout(self):
        # init submodule for Readout module
        self.add_submodule("readout", Readout("readout", self, self._qachannel))

    def _init_sweeper(self):
        # init submodule for Sweeper
        self.add_submodule("sweeper", Sweeper("sweeper", self, self._qachannel))


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
            "playback_delay",
            docstring=self._generator.playback_delay.__repr__(),
            get_cmd=self._generator.playback_delay,
            set_cmd=self._generator.playback_delay,
            label="Delay for the Start of Playback",
        )
        self.add_parameter(
            "single",
            docstring=self._generator.single.__repr__(),
            get_cmd=self._generator.single,
            set_cmd=self._generator.single,
            label="Single Run",
        )

    def run(self, sync=True) -> None:
        """Run the generator.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after enabling the generator (default: True).

        """
        self._generator.run(sync=sync)

    def stop(self, sync=True) -> None:
        """Stop the generator.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after disabling the generator (default: True).

        """
        self._generator.stop(sync=sync)

    def wait_done(self, timeout: float = 10, sleep_time: float = 0.005) -> None:
        """Wait until the generator is finished.

        Arguments:
            timeout (float): The maximum waiting time in seconds for the
                generator (default: 10).
            sleep_time (float): Time in seconds to wait between
                requesting generator state

        Raises:
            ToolkitError: If the generator is running in continuous
                mode.
            TimeoutError: If the generator is not finished before the
                timeout.

        """
        self._generator.wait_done(timeout=timeout, sleep_time=sleep_time)

    def compile(self) -> None:
        """Compile the current SequenceProgram and load it to sequencer.

        Raises:
            ToolkitConnectionError: If the AWG Core has not been set up
                yet
            ToolkitError: if the compilation has failed or the ELF
                upload is not successful.
            TimeoutError: if the program upload is not completed before
                timeout.

        """
        return self._generator.compile()

    def reset_queue(self) -> None:
        """Resets the waveform queue to an empty list."""
        self._generator.reset_queue()

    def queue_waveform(self, wave: Union[List, np.array], delay: float = 0) -> None:
        """Add a new waveform to the queue.

        Arguments:
            wave (array): The waveform to be queued as a 1D numpy array.
            delay (int): An individual delay in seconds for this waveform
                w.r.t. the time origin of the sequence. (default: 0)

        Raises:
            ToolkitError: If the sequence is not of type *'Custom'*.

        """
        self._generator.queue_waveform(wave, delay=delay)

    def replace_waveform(
        self,
        wave: Union[List, np.array],
        i: int = 0,
        delay: float = 0,
    ) -> None:
        """Replace a waveform in the queue at a given index.

        Arguments:
            wave (array): Waveform to replace current wave
            i (int): The index of the waveform in the queue to be
                replaced.
            delay (int): An individual delay in seconds for this
                waveform w.r.t. the time origin of the sequence. (default: 0)

        Raises:
            ValueError: If the given index is out of range.

        """
        self._generator.replace_waveform(wave, i=i, delay=delay)

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

            >>> shfqa.qachannels[0].generator.set_sequence_params(
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


class Readout(InstrumentChannel):
    """Device-specific *Readout* module for the *SHFQA*."""

    def __init__(self, name: str, parent_instr, parent_contr) -> None:
        super().__init__(parent_instr, name)
        self._readout = SHFQA_Readout(parent_contr)
        self._readout._init_readout_params()
        self._add_qcodes_readout_params()
        self._init_integrations()

    def _add_qcodes_readout_params(self):
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "integration_length",
            docstring=self._readout.integration_length.__repr__(),
            get_cmd=self._readout.integration_length,
            set_cmd=self._readout.integration_length,
            label="Integration Length",
        )
        self.add_parameter(
            "integration_delay",
            docstring=self._readout.integration_delay.__repr__(),
            get_cmd=self._readout.integration_delay,
            set_cmd=self._readout.integration_delay,
            label="Integration Delay",
        )
        self.add_parameter(
            "result_source",
            docstring=self._readout.result_source.__repr__(),
            get_cmd=self._readout.result_source,
            set_cmd=self._readout.result_source,
            label="Result Source",
        )

    def _init_integrations(self):
        # init submodules for Integration Units
        num_integrations = self._readout.device.num_integrations_per_qachannel()
        channel_list = ChannelList(self, "integrations", Integration)
        for i in range(num_integrations):
            channel_list.append(Integration(f"integration-{i}", i, self, self._readout))
        channel_list.lock()
        self.add_submodule("integrations", channel_list)
        self._readout._init_integrations()

    @property
    def is_running(self):
        return self._readout.is_running

    def arm(self, sync=True, length: int = None, averages: int = None) -> None:
        """Prepare SHF device for readout and result acquisition.

        This method enables the QA Results Acquisition and resets the
        acquired points. Optionally, the *result length* and
        *result averages* can be set when specified as keyword
        arguments. If they are not specified, they are not changed.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after stopping the SHF device and clearing the
                register bank (default: True).
            length (int): If specified, the length of the result vector
                will be set before arming the readout.
                (default: None)
            averages (int): If specified, the result averages will be
                set before arming the readout. (default: None)

        """
        self._readout.arm(sync=sync, length=length, averages=averages)

    def run(self, sync=True) -> None:
        """Start the result logger.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after starting the result logger (default: True).

        Raises:
            ToolkitError: If `sync=True` and the result logger cannot
                be started

        """
        self._readout.run(sync=sync)

    def stop(self, sync=True) -> None:
        """Stop the result logger.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after stopping the result logger (default: True).

        Raises:
            ToolkitError: If `sync=True` and the result logger cannot
                be stopped

        """
        self._readout.stop(sync=sync)

    def wait_done(self, timeout: float = 10, sleep_time: float = 0.005) -> None:
        """Wait until readout is finished.

        Arguments:
            timeout (float): The maximum waiting time in seconds for the
                Readout (default: 10).
            sleep_time (float): Time in seconds to wait between
                requesting Readout state

        Raises:
            TimeoutError: if the readout recording is not completed
                before timeout.

        """
        self._readout.wait_done(timeout=timeout, sleep_time=sleep_time)

    def read(
        self,
        integrations: list = [],
        blocking: bool = True,
        timeout: float = 10,
        sleep_time: float = 0.005,
    ):
        """Read out the measured data from the result logger.

        Arguments:
            integrations (list): The list of integrations to return the
                data for. If no integration is specified, the method
                will return the data for all integrations
                (default: []).
            blocking (bool): A flag that specifies if the program
                should be blocked until the result logger finished
                recording (default: True).
            timeout (float): The maximum waiting time in seconds for the
                Readout (default: 10).
            sleep_time (float): Time in seconds to wait between
                requesting Readout state

        Returns:
            An array containing the result logger data.

        Raises:
            TimeoutError: if the readout recording is not completed
                before timeout.

        """
        return self._readout.read(
            integrations=integrations,
            blocking=blocking,
            timeout=timeout,
            sleep_time=sleep_time,
        )


class Integration(InstrumentChannel):
    """Device-specific *Integration* for the *SHFQA*."""

    def __init__(self, name: str, index: int, parent_instr, parent_contr) -> None:
        super().__init__(parent_instr, name)
        self._integration = SHFQA_Integration(parent_contr, index)
        self._integration._init_integration_params()
        self._add_qcodes_integration_params()

    def _add_qcodes_integration_params(self):
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "threshold",
            unit=self._integration.threshold._unit,
            docstring=self._integration.threshold.__repr__(),
            get_cmd=self._integration.threshold,
            set_cmd=self._integration.threshold,
            label="Signal Threshold for State Discrimination",
        )
        self.add_parameter(
            "result",
            unit=self._integration.result._unit,
            docstring=self._integration.result.__repr__(),
            get_cmd=self._integration.result,
            set_cmd=self._integration.result,
            label="Result Vector Data",
        )
        self.add_parameter(
            "weights",
            unit=self._integration.weights._unit,
            docstring=self._integration.weights.__repr__(),
            get_cmd=self._integration.weights,
            set_cmd=self._integration.weights,
            label="Complex-valued Waveform of the Integration Weights",
        )

    def set_int_weights(self, weights):
        return self._integration.set_int_weights(weights)


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
            "oscillator_freq",
            unit=self._sweeper.oscillator_freq._unit,
            docstring=self._sweeper.oscillator_freq.__repr__(),
            get_cmd=self._sweeper.oscillator_freq,
            set_cmd=self._sweeper.oscillator_freq,
            label="Frequency of Digital Oscillator",
        )
        self.add_parameter(
            "integration_time",
            unit=self._sweeper.integration_time._unit,
            docstring=self._sweeper.integration_time.__repr__(),
            get_cmd=self._sweeper.integration_time,
            set_cmd=self._sweeper.integration_time,
            label="Spectroscopy Integration Time",
        )
        self.add_parameter(
            "integration_length",
            unit=self._sweeper.integration_length._unit,
            docstring=self._sweeper.integration_length.__repr__(),
            get_cmd=self._sweeper.integration_length,
            set_cmd=self._sweeper.integration_length,
            label="Spectroscopy Integration Length",
        )
        self.add_parameter(
            "integration_delay",
            unit=self._sweeper.integration_delay._unit,
            docstring=self._sweeper.integration_delay.__repr__(),
            get_cmd=self._sweeper.integration_delay,
            set_cmd=self._sweeper.integration_delay,
            label="Spectroscopy Integration Delay",
        )
        self.add_parameter(
            "trigger_source",
            unit=self._sweeper.trigger_source._unit,
            docstring=self._sweeper.trigger_source.__repr__(),
            get_cmd=self._sweeper.trigger_source,
            set_cmd=self._sweeper.trigger_source,
            label="Trigger Source for the Sweeper",
        )

    def trigger_level(self, level=None):
        """Set or get the trigger level for the sweeper.

        Arguments:
            level (float): Trigger level of the sweeper
                (default: None).

        """
        return self._sweeper.trigger_level(level=level)

    def trigger_imp50(self, imp50=None):
        """Set or get the trigger input impedance setting for the sweeper.

        Arguments:
            imp50 (bool): Trigger input impedance selection for the
                sweeper. When set to True, the trigger input impedance is
                50 Ohm. When set to False, it is 1 kOhm (default: None).

        """
        return self._sweeper.trigger_imp50(imp50=imp50)

    def start_frequency(self, freq=None):
        """Set or get the start frequency for the sweeper.

        Arguments:
            freq (float): Start frequency in Hz of the sweeper
                (default: None).

        """
        return self._sweeper.start_frequency(freq=freq)

    def stop_frequency(self, freq=None):
        """Set or get the stop frequency for the sweeper.

        Arguments:
            freq (float): Stop frequency in Hz of the sweeper
                (default: None).

        """
        return self._sweeper.stop_frequency(freq=freq)

    def output_freq(self):
        """Get the output frequency.

        Returns:
            The carrier frequency in Hz of the microwave signal at the
            Out connector. This frequency corresponds to the sum of the
            Center Frequency and the Offset Frequency.

        """
        return self._sweeper.output_freq()

    def num_points(self, num=None):
        """Set or get the number of points for the sweeper.

        Arguments:
            num (int): Number of frequency points to sweep between
                start and stop frequency values (default: None).

        """
        return self._sweeper.num_points(num=num)

    def mapping(self, map=None):
        """Set or get the mapping configuration for the sweeper.

        Arguments:
            map (str): Mapping that specifies the distances between
                frequency points of the sweeper. Can be either "linear"
                or "log" (default: None).

        """
        return self._sweeper.mapping(map=map)

    def num_averages(self, num=None):
        """Set or get the number of averages for the sweeper.

        Number of averages specifies how many times a frequency point
        will be measured and averaged.

        Arguments:
            num (int): Number of times the sweeper measures one
                frequency point (default: None).

        """
        return self._sweeper.num_averages(num=num)

    def averaging_mode(self, mode=None):
        """Set or get the averaging mode for the sweeper.

        Arguments:
            mode (str): Averaging mode for the sweeper. Can be either
                "sequential" or "cyclic" (default: None).\n
                "sequential": A frequency point is measured the number
                of times specified by the number of averages setting.
                In other words, the same frequency point is measured
                repeatedly until the number of averages is reached
                and the sweeper then moves to the next frequency
                point.\n
                "cyclic": All frequency points are measured once from
                start frequency to stop frequency. The sweeper then
                moves back to start frequency and repeats the sweep
                the number of times specified by the number of
                averages setting.

        """
        return self._sweeper.averaging_mode(mode=mode)

    def run(self):
        """Perform a sweep with the specified settings.

        This method eventually wraps around the `run` method of
        `zhinst.utils.shf_sweeper`
        """
        return self._sweeper.run()

    def read(self):
        """Get the measurement data of the last sweep.

        This method eventually wraps around the `get_result` method of
        `zhinst.utils.shf_sweeper`

        Returns:
             A dictionary with measurement data of the last sweep

        """
        return self._sweeper.read()

    def plot(self):
        """Plot power over frequency for last sweep.

        This method eventually wraps around the `plot` method of
        `zhinst.utils.shf_sweeper`
        """
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

    def run(self, sync=True) -> None:
        """Run the scope recording.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after starting the scope recording
                (default: True).

        """
        self._scope.run(sync=sync)

    def stop(self, sync=True) -> None:
        """Stop the scope recording.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after stopping scope recording
                (default: True).

        """
        self._scope.stop(sync=sync)

    def wait_done(self, timeout: float = 10, sleep_time: float = 0.005) -> None:
        """Wait until the Scope recording is finished.

        Arguments:
            timeout (int): The maximum waiting time in seconds for the
                Scope (default: 10).
            sleep_time (float): Time in seconds to wait between
                requesting the progress and records values

        Raises:
            ToolkitError: If the Scope recording is not done before the
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
                for all channels.
            blocking (bool): A flag that specifies if the program
                should be blocked until the scope has finished
                recording (default: True).
            timeout (float): The maximum waiting time in seconds for the
                Scope (default: 10).
            sleep_time (float): Time in seconds to wait between
                requesting the progress and records values

        Returns:
            A dictionary showing the recorded data and scope time.

        Raises:
            TimeoutError: if the scope recording is not completed before
                timeout.

        """
        return self._scope.read(
            channel=channel, blocking=blocking, timeout=timeout, sleep_time=sleep_time
        )

    def channels(self, value=None):
        """Set all Scope channels simultaneously.

        Arguments:
            value (tuple): Tuple of values {'on', 'off'} for channel 1,
                2, 3 and 4 (default: None).

        Returns:
            A tuple with the states {'on', 'off'} for all input channels.

        """
        return self._scope.channels(value=value)

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
        return self._scope.input_select(value=value)

    def segments(self, enable=None, count=None):
        """Configure segmented Scope recording options.

        Keyword Arguments:
            enable (bool): a flag that specifies whether segmented Scope
                recording is enabled (default: None).
            count (int): number of segments in device memory (default: None)

        Returns:
            A dictionary showing the enable state and segment count

        """
        return self._scope.segments(enable=enable, count=count)

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
        return self._scope.averaging(enable=enable, count=count)

    @property
    def is_running(self):
        return self._scope.is_running


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
        self._init_qachannels()
        self._init_scope()
        self._add_qcodes_params()

    def _init_qachannels(self):
        # init submodules for QAChannels
        num_qachannels = self._controller.num_qachannels()
        channel_list = ChannelList(self, "qachannels", QAChannel)
        for i in range(num_qachannels):
            channel_list.append(QAChannel(f"qachannel-{i}", i, self, self._controller))
        channel_list.lock()
        self.add_submodule("qachannels", channel_list)

    def _init_scope(self):
        # init submodule Scope
        self.add_submodule("scope", Scope("scope", self, self._controller))

    def _add_qcodes_params(self):
        # add custom parameters as QCoDeS parameters
        super()._add_qcodes_params()
        self.add_parameter(
            "sw_trigger",
            unit=self._controller.sw_trigger._unit,
            docstring=self._controller.sw_trigger.__repr__(),
            get_cmd=self._controller.sw_trigger,
            set_cmd=self._controller.sw_trigger,
            label="Issue a Single Software Trigger Event",
        )
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

    def factory_reset(self, sync=True) -> None:
        """Load the factory default settings.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after loading the factory preset (default: True).

        """
        self._controller.factory_reset(sync=sync)

    def set_trigger_loopback(self):
        """Start a trigger pulse using the internal loopback.

        A 1kHz continuous trigger pulse from marker 1 A using the
        internal loopback to trigger in 1 A.
        """
        self._controller.set_trigger_loopback()

    def clear_trigger_loopback(self):
        """Stop the the internal loopback trigger pulse."""
        self._controller.clear_trigger_loopback()

    def check_ref_clock(
        self, blocking: bool = True, timeout: int = 30, sleep_time: int = 1
    ) -> None:
        """Check if reference clock is locked successfully.

        Arguments:
            blocking (bool): A flag that specifies if the program should
                be blocked until the reference clock is 'locked'.
                (default: True)
            timeout (int): Maximum time in seconds the program waits
                when `blocking` is set to `True` (default: 30).
            sleep_time (int): Time in seconds to wait between
                requesting the reference clock status (default: 1)

        Raises:
            ToolkitError: If the device fails to lock on the reference
                clock.

        """
        self._controller.check_ref_clock(
            blocking=blocking, timeout=timeout, sleep_time=sleep_time
        )

    @property
    def allowed_sequences(self):
        return self._controller.allowed_sequences

    @property
    def allowed_trigger_modes(self):
        return self._controller.allowed_trigger_modes
