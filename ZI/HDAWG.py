from .ZIBaseInstrument import ZIBaseInstrument, ZIAWG
from qcodes.instrument.channel import ChannelList



class HDAWG(ZIBaseInstrument):
    def __init__(self, name: str, serial: str, **kwargs) -> None:
        super().__init__(name, "hdawg", serial, interface=kwargs.get("interface", "1gbe"))

        # init submodules recursively from nodetree
        submodules = [
            "oscs", 
            "triggers", 
            "dios", 
            "sigouts", 
            "awgs", 
            "clockbase", 
        ]
        for key in submodules:
            self.init_submodule(key)
        
        # init sequencer ChannelList
        channel_list = ChannelList(self, "sequencers", ZIAWG)
        for i in self.nodetree_dict["awgs"].keys():
            module = ZIAWG(self, i)
            channel_list.append(module)
        channel_list.lock()
        self.add_submodule("sequencers", channel_list)
