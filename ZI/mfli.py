from .base import ZIBaseInstrument
import zhinst.toolkit as tk


class MFLI(ZIBaseInstrument):
    """
    QCoDeS driver for ZI MFLI.

    Inherits from ZIBaseInstrument.
    """

    def __init__(self, name: str, serial: str, interface="1gbe", **kwargs) -> None:
        super().__init__(name, "mfli", serial, interface)
        submodules = self.nodetree_dict.keys()
        blacklist = ["scopes"]
        [self._init_submodule(key) for key in submodules if key not in blacklist]

    def connect(self):
        # use zhinst.toolkit.tools.BaseController() to interface the device
        self._controller = tk.MFLI(self._name, self._serial, interface=self._interface)
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

