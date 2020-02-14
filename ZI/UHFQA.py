from .ZIBaseInstrument import ZIBaseInstrument
from .ZIAWG import ZIAWG



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
        module = ZIAWG(self, 0)
        self.add_submodule("sequencer", module)