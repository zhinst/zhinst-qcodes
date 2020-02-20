from .ZIBaseInstrument import ZIBaseInstrument
from .ZIAWG import ZIAWG
from qcodes.instrument.channel import ChannelList



class AWG(ZIAWG):
    """
    Subclass the ZIAWG to make sure only HDAWG sequences are allowed to be set.
    """
    def set_sequence_params(self, **kwargs):
        if "sequence_type" in kwargs.keys():
            t = kwargs["sequence_type"]
            allowed_sequences = ["Simple", "Rabi", "T1", "T2*", "Custom"]
            if t not in allowed_sequences:
                raise Exception(f"Sequence type {t} must be one of {allowed_sequences}!")
        super().set_sequence_params(**kwargs)



class HDAWG(ZIBaseInstrument):
    """
    QCoDeS driver for ZI HDAWG.

    Inherits from ZIBaseInstrument. Initializes some submodules 
    from the nodetree and a ChannelList of 'sequencers' for high 
    level control of the AWG sequence program.
    """
    def __init__(self, name: str, serial: str, **kwargs) -> None:
        super().__init__(name, "hdawg", serial, interface=kwargs.get("interface", "1gbe"))

        # init submodules recursively from nodetree
        submodules = [
            "system",
            "oscs", 
            "sines",
            "triggers", 
            "dios", 
            "sigouts", 
            "awgs", 
            "clockbase",
            "cnts"
        ]
        for key in submodules:
            self._init_submodule(key)
        
        # init sequencer ChannelList
        channel_list = ChannelList(self, "sequencers", AWG)
        for i in self.nodetree_dict["awgs"].keys():
            module = AWG(self, i)
            channel_list.append(module)
        channel_list.lock()
        self.add_submodule("sequencers", channel_list)
