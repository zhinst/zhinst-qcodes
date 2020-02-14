from qcodes.instrument.channel import InstrumentChannel


class ZIAWG(InstrumentChannel):
    """
    ZIAWG class that represents on AWG sequencer. It wraps around the 
    functionality of ziDrivers.Controller() for a high level control of 
    the AWG sequence program.

    Possible sequence types are:
        
        (for HDAWG and UHFQA):
        - Simple     : queue, upload and replace arbitrary waveforms
        - Rabi       : Rabi sequence
        - T1         : T1 sequence
        - T2*        : T2 Ramsey sequence
        
        (only for UHFQA):
        - Readout    : Sequence for multiplexed readout 
        - Pulsed Spectroscopy
        - CW Spectroscopy

    Most important sequence parameters:
        - sequence_type
        - period
        - trigger_mode
        - repetitions
 
    """
    def __init__(self, parent, index, **kwargs) -> None: 
        self.index = index
        self._controller = parent._controller
        self._dev = parent._dev
        name = f"awg{index}"
        super().__init__(parent, name, **kwargs)

    def __repr__(self):
        params = self.sequence_params["sequence_parameters"]
        s = f"ZIAWG: {self.name}\n"
        s += f"    parent  : {self._parent}\n"
        s += f"    index   : {self.index}\n"
        s += f"    sequence: \n"
        s += f"           type: {self.sequence_params['sequence_type']}\n"
        for i in params.items():
            s += f"            {i}\n"
        return s
    
    def print_readable_snapshot(self, update: bool = False, max_chars: int = 80) -> None:
        print(f"{self}")
    
    def run(self):
        self._controller.awg_run(self._dev, self.index)

    def stop(self):
        self._controller.awg_stop(self._dev, self.index)

    def compile(self):
        self._controller.awg_compile(self._dev, self.index)
    
    def reset_queue(self):
        self._controller.awg_reset_queue(self._dev, self.index)

    def queue_waveform(self, wave1, wave2):
        self._controller.awg_queue_waveform(
            self._dev,
            self.index,
            data=(wave1, wave2)
        )

    def replace_waveform(self, wave1, wave2, i=0):
        self._controller.awg_replace_waveform(
            self._dev,
            self.index,
            data=(wave1, wave2),
            index=i
        )

    def upload_waveforms(self):
        self._controller.awg_upload_waveforms(
            self._dev,
            self.index
        )

    def compile_and_upload_waveforms(self):
        self._controller.awg_compile_and_upload_waveforms(
            self._dev,
            self.index
        )

    def set_sequence_params(self, **kwargs):
        self._controller.awg_set_sequence_params(
            self._dev,
            self.index,
            **kwargs
        )
    
    @property
    def is_running(self):
        return self._controller.awg_is_running(
            self._dev, 
            self.index
        )

    @property
    def sequence_params(self):
        return self._controller.awg_list_params(
            self._dev,
            self.index
        )