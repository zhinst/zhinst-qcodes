from .ZIBaseInstrument import ZIBaseInstrument
import zhinst.toolkit as tk


class UHFLI(ZIBaseInstrument):
    """
    QCoDeS driver for ZI UHFQA.

    Inherits from ZIBaseInstrument. Initializes some submodules 
    from the nodetree and a 'sequencer' submodule for high level 
    control of the AWG sequence program.
    """

    def __init__(self, name: str, serial: str, interface="1gbe", **kwargs) -> None:
        super().__init__(name, "uhfli", serial, interface)
        submodules = [
            "system",
            "oscs",
            "triggers",
            # "dios",
            "sigins",
            "sigouts",
            # "awgs",
            "clockbase",
            # "qas",
            "scopes",
        ]
        # init submodules recursively from nodetree
        [self._init_submodule(key) for key in submodules]
        # init custom ZI submodules
        self.add_submodule("awg", self.awg)

    def connect(self):
        # use zhinst.toolkit.tools.BaseController() to interface the device
        self._controller = tk.UHFLI(self._name, self._serial, interface=self._interface)
        self._controller.setup()
        self._controller.connect_device(nodetree=False)
        self.connect_message()
        self._get_nodetree_dict()

    def get_idn(self):
        return dict(
            vendor="Zurich Instruments",
            model=self._type.upper(),
            serial=self._serial,
            firmware=self._controller._get("system/fwrevision"),
        )

    @property
    def awg(self):
        return self._controller.awg
