"""Toolkit adaption for the zhinst.utils.SHFSweeper."""
import typing as t

from zhinst.toolkit.driver.modules.shfqa_sweeper import SHFQASweeper as TKSHFQASweeper

from zhinst.qcodes.qcodes_adaptions import init_nodetree, ZIInstrument

if t.TYPE_CHECKING:
    from zhinst.qcodes.driver.devices import DeviceType
    from zhinst.qcodes.session import Session


class ZISHFQASweeper(ZIInstrument):
    """QCoDeS adaption for the zhinst.utils.SHFSweeper.

    For now the general sweeper module does not support the SHFQA. However a
    python based implementation called ``SHFSweeper`` does already provide
    this functionality. The ``SHFSweeper`` is part of the ``zhinst`` module
    and can be found in the utils.

    Toolkit wraps around the ``SHFSweeper`` and exposes a interface that is
    similar to the LabOne modules, meaning the parameters are exposed in a
    node tree like structure.

    All parameters can be accessed through their corresponding node:
    * device: Device to run the sweeper with
    * sweep: Frequency range settings for a sweep
    * rf: RF in- and output settings for a sweep
    * average: Averaging settings for a sweep
    * trigger: Settings for the trigger
    * envelope: Settings for defining a complex envelope for pulsed spectroscopy

    The underlying module is updated with the parameter changes automatically.
    Every functions from the underlying SHFSweeper module is exposed and can be
    used in the same way.

    Args:
        tk_object: Instance of the toolkit shfqa sweeper.
        session: Session to the Data Server.
    """

    def __init__(self, tk_object: TKSHFQASweeper, session: "Session"):
        super().__init__(
            f"zi_shfqasweeper_{len(self.instances())}", tk_object.root, is_module=True
        )
        self._tk_object = tk_object
        self._session = session
        init_nodetree(self, self._tk_object, self._snapshot_cache)
        self._tk_object.root.update_nodes(
            {"/device": {"GetParser": lambda value: self._get_device(value)}}
        )

    def _get_device(self, serial: str) -> t.Union["DeviceType", str]:
        """Convert a device serial into a QCoDeS device object.

        Args:
            serial: Serial of the device

        Returns:
            QCoDeS device object. If the serial does not
                match to a connected device the serial is returned instead.
        """
        try:
            return self._session.devices[serial]
        except (RuntimeError, KeyError):
            return serial

    def run(self) -> dict:
        """Perform a sweep with the specified settings.

        This method eventually wraps around the `run` method of
        `zhinst.utils.shf_sweeper`

        Returns:
             A dictionary with measurement data of the last sweep.
        """
        return self._tk_object.run()

    def get_result(self) -> dict:
        """Get the measurement data of the last sweep.

        This method eventually wraps around the `get_result` method of
        `zhinst.utils.shf_sweeper`

        Returns:
             A dictionary with measurement data of the last sweep.

        """
        return self._tk_object.get_result()

    def plot(self) -> None:
        """Plot power over frequency for last sweep.

        This method eventually wraps around the `plot` method of
        `zhinst.utils.shf_sweeper`
        """
        return self._tk_object.plot()

    def get_offset_freq_vector(self) -> t.Any:
        """Get vector of frequency points.

        This method wraps around the `get_offset_freq_vector` method of
        `zhinst.utils.shf_sweeper`

        Returns:
            Vector of frequency points.
        """
        return self._tk_object.get_offset_freq_vector()
