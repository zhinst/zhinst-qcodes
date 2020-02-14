from .ZIBaseInstrument import ZIBaseInstrument
from .ZIAWG import ZIAWG



class AWG(ZIAWG):
    def set_sequence_params(self, **kwargs):
        if "sequence_type" in kwargs.keys():
            t = kwargs["sequence_type"]
            allowed_sequences = [
                "Simple", 
                "Rabi", 
                "T1", 
                "T2*", 
                "Readout", 
                "CW Spectroscopy", 
                "Pulsed Spectroscopy", 
                "Custom"
            ]
            if t not in allowed_sequences:
                raise Exception(f"Sequence type {t} must be one of {allowed_sequences}!")
            if t == "CW Spectroscopy":
                self._parent.sigouts[0].enables0(1)
                self._parent.sigouts[1].enables1(1)
                self._parent.sigouts[0].amplitudes0(1)
                self._parent.sigouts[1].amplitudes1(1)
                self._parent.qas[0].integration.mode(1)
            if t == "Pulsed Spectroscopy":
                self._parent.sigouts[0].enables0(0)
                self._parent.sigouts[0].enables1(0)
                self._parent.sigouts[1].enables0(0)
                self._parent.sigouts[1].enables1(0)
                self._parent.sigouts[0].amplitudes0(0)
                self._parent.sigouts[0].amplitudes1(0)
                self._parent.sigouts[1].amplitudes0(0)
                self._parent.sigouts[1].amplitudes1(0)
                self._parent.awgs[0].outputs[0].mode(1)
                self._parent.awgs[0].outputs[1].mode(1)
                self._parent.qas[0].integration.mode(1)
            if t == "Readout":
                self._parent.sigouts[0].enables0(0)
                self._parent.sigouts[0].enables1(0)
                self._parent.sigouts[1].enables0(0)
                self._parent.sigouts[1].enables1(0)
                self._parent.awgs[0].outputs[0].mode(0)
                self._parent.awgs[0].outputs[1].mode(0)
                self._parent.qas[0].integration.mode(0)
        if "trigger_mode" in kwargs.keys():
            if kwargs["trigger_mode"] == "External Trigger":
                self._parent.awgs[0].auxtriggers[0].channel(0)
                self._parent.awgs[0].auxtriggers[1].channel(0)
                self._parent.awgs[0].auxtriggers[0].slope(1)
                self._parent.awgs[0].auxtriggers[1].slope(1)            
        super().set_sequence_params(**kwargs)




class UHFQA(ZIBaseInstrument):
    """
    QCoDeS driver for ZI UHFQA.

    Inherits from ZIBaseInstrument. Initializes some submodules 
    from the nodetree and a 'sequencer' submodule for high level 
    control of the AWG sequence program.
    """
    def __init__(self, name: str, serial: str, **kwargs) -> None:
        super().__init__(name, "uhfqa", serial)

        # init submodules recursively from nodetree
        submodules = [
            "system",
            "oscs", 
            "triggers", 
            "dios", 
            "sigins", 
            "sigouts", 
            "awgs", 
            "clockbase", 
            "qas"
        ]
        for key in submodules:
            self._init_submodule(key)
        
        # init sequencer submodule
        module = AWG(self, 0)
        self.add_submodule("sequencer", module)