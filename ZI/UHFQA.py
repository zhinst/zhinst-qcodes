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
                "Custom",
            ]
            if t not in allowed_sequences:
                raise Exception(
                    f"Sequence type {t} must be one of {allowed_sequences}!"
                )

            # apply settings dependent on sequence type
            if t == "CW Spectroscopy":
                self._controller.set(self._dev, "sigouts/0/enables/0", 1)
                self._controller.set(self._dev, "sigouts/1/enables/1", 1)
                self._controller.set(self._dev, "sigouts/0/amplitudes/0", 1)
                self._controller.set(self._dev, "sigouts/1/amplitudes/1", 1)
                self._controller.set(self._dev, "qas/0/integration/mode", 1)
            if t == "Pulsed Spectroscopy":
                self._controller.set(self._dev, "sigouts/*/enables/*", 0)
                self._controller.set(self._dev, "sigouts/*/amplitudes/*", 0)
                self._controller.set(self._dev, "awgs/0/outputs/*/mode", 1)
                self._controller.set(self._dev, "qas/0/integration/mode", 1)
            if t == "Readout":
                self._controller.set(self._dev, "sigouts/*/enables/*", 0)
                self._controller.set(self._dev, "awgs/0/outputs/*/mode", 0)
                self._controller.set(self._dev, "qas/0/integration/mode", 0)
        
        # apply settings dependent on trigger type
        if "trigger_mode" in kwargs.keys():
            if kwargs["trigger_mode"] == "External Trigger":
                self._controller.set(self._dev, "/awgs/0/auxtriggers/*/channel", 0)
                self._controller.set(self._dev, "/awgs/0/auxtriggers/*/slope", 1)
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
            "qas",
        ]
        for key in submodules:
            self._init_submodule(key)

        # init sequencer submodule
        module = AWG(self, 0)
        self.add_submodule("sequencer", module)
