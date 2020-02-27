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
        for key in submodules:
            self._init_submodule(key)

    def connect(self):
        # use zhinst.toolkit.tools.BaseController() to interface the device
        self._controller = tk.UHFLI(self._name)
        self._controller.setup()
        self._controller.connect_device(self._serial, self._interface)
        self.connect_message()
        # get the nodetree from the device as a nested dict
        self._get_nodetree_dict()

    def get_idn(self):
        return dict(
            vendor="Zurich Instruments",
            model=self._type.upper(),
            serial=self._serial,
            firmware=self._controller.get("system/fwrevision"),
        )

    @property
    def awg(self):
        # add this as InstrumentChannel ?
        return self._controller.awg

    @property
    def channels(self):
        # add this as ChannelList ?
        return self._controller.channels
