from .ZIBaseInstrument import ZIBaseInstrument, ZIAWG



class UHFQA(ZIBaseInstrument):
    def __init__(self, name: str, serial: str, **kwargs) -> None:
        super().__init__(name, "uhfqa", serial)

        # init submodules recursively from nodetree
        submodules = [
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
            self.init_submodule(key)
        
        # init sequencer submodule
        module = ZIAWG(self, 0)
        self.add_submodule("sequencer", module)