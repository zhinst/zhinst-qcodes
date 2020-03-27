from .base import ZIBaseInstrument
import zhinst.toolkit as tk
from zhinst.toolkit.control.drivers.uhfqa import ReadoutChannel, AWG as UHFQA_AWG

from qcodes.instrument.channel import ChannelList, InstrumentChannel
import qcodes.utils.validators as vals


class AWG(InstrumentChannel):
    def __init__(self, name, parent_instr, parent_contr):
        super().__init__(self, parent_instr, name)
        self._awg = UHFQA_AWG(parent_contr, 0)
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "outputs",
            unit=None,
            docstring="Expects a tuple with 'on' and 'off' values for the two channels of the AWG, e.g. ('on', 'off').",
            get_cmd=self._awg.outputs,
            set_cmd=self._awg.outputs,
            label="Output Ch 1&2",
        )
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

    # documentation missing here!
    def run(self):
        self._awg.run()

    def stop(self):
        self._awg.stop()

    def wait_done(self, timeout=10):
        self._awg.wait_done(timeout=timeout)

    def compile(self):
        self._awg.compile()

    def reset_queue(self):
        self._awg.reset_queue()

    def queue_waveform(self, wave1, wave2, delay=0):
        self._awg.queue_waveform(wave1, wave2, delay=delay)

    def replace_waveform(self, wave1, wave2, i=0, delay=0):
        self._awg.replace_waveform(wave1, wave2, i=i, delay=delay)

    def upload_waveforms(self):
        self._awg.upload_waveforms()

    def compile_and_upload_waveforms(self):
        self._awg.compile_and_upload_waveforms()

    def set_sequence_params(self, **kwargs):
        self._awg.set_sequence_params(**kwargs)

    def sequence_params(self):
        return self._awg.sequence_params


class Channel(InstrumentChannel):
    def __init__(self, name, index, parent_instr, parent_contr):
        InstrumentChannel.__init__(self, parent_instr, name)
        self._channel = ReadoutChannel(parent_contr, 0)
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

    def enable(self):
        self._channel.enable()

    def disable(self):
        self._channel.disable()


class UHFQA(ZIBaseInstrument):
    """
    QCoDeS driver for ZI UHFQA.

    Inherits from ZIBaseInstrument. Initializes some submodules 
    from the nodetree and a 'sequencer' submodule for high level 
    control of the AWG sequence program.

    Arguments:
        name (str): The internal QCoDeS name of the instrument
        serial (str): The device name as listed in the web server
        interface (str): The interface used to connect to the 
            device (default: '1gbe')
        host (str): Address of the data server (default: 'localhost')
        port (int): Port used to connect to the data server (default: 8004)
        api (int): Api level used (default: 6)

    """

    def __init__(
        self,
        name: str,
        serial: str,
        interface="1gbe",
        host="localhost",
        port=8004,
        api=6,
        **kwargs,
    ) -> None:
        super().__init__(name, "uhfqa", serial, interface, host, port, api, **kwargs)
        submodules = self.nodetree_dict.keys()
        blacklist = [
            "awgs",
            "scopes",
        ]
        [self._init_submodule(key) for key in submodules if key not in blacklist]
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
            vals=vals.Number(0, 50e-6),
        )

    def connect(self):
        self._controller = tk.UHFQA(
            self._name, self._serial, interface=self._interface, host=self._host
        )
        self._controller.setup()
        self._controller.connect_device(nodetree=False)
        self.connect_message()
        self._get_nodetree_dict()
