from .base import ZIBaseInstrument
import zhinst.toolkit as tk


class HDAWG(ZIBaseInstrument):
    """
    QCoDeS driver for ZI HDAWG.

    Inherits from ZIBaseInstrument. Initializes some submodules 
    from the nodetree and a ChannelList of 'sequencers' for high 
    level control of the AWG sequence program.
    """

    def __init__(self, name: str, serial: str, interface="1gbe", **kwargs) -> None:
        super().__init__(name, "hdawg", serial, interface)
        submodules = [
            "system",
            "oscs",
            "sines",
            "triggers",
            "dios",
            "sigouts",
            # "awgs",
            "clockbase",
            "cnts",
        ]
        # init submodules recursively from nodetree
        [self._init_submodule(key) for key in submodules]
        # init custom ZI submodules
        [self.add_submodule(f"awgs[{i}]", self.awgs[i]) for i in range(4)]

    def connect(self):
        # use zhinst.toolkit.tools.BaseController() to interface the device
        self._controller = tk.HDAWG(self._name, self._serial, interface=self._interface)
        self._controller.setup()
        self._controller.connect_device(nodetree=False)
        self.connect_message()
        # get the nodetree from the device as a nested dict
        self._get_nodetree_dict()

    @property
    def awgs(self):
        # add this as ChannelList ?
        return self._controller.awgs

