"""Base modules for the Zurich Instrument specific QCoDeS driver."""
import typing as t

from zhinst.toolkit.driver.devices import DeviceType

from zhinst.qcodes.qcodes_adaptions import init_nodetree, ZIInstrument

if t.TYPE_CHECKING:
    from zhinst.qcodes.session import ZISession, Session
    from qcodes.instrument.base import Instrument


class ZIBaseInstrument(ZIInstrument):
    """Generic QCoDeS driver for a Zurich Instrument device.

    All device specific class are derived from this class.
    It implements common functions valid for all
    devices.
    It also can be used directly, e.g. for instrument types that have no special
    class in QCoDeS.

    Args:
        tk_object: Instance of the toolkit base instrument
        name: Name of the instrument in qcodes. (default = "zi_{dev_type}_{serial}")
        raw: Flag if qcodes instance should only created with the nodes and not
            forwarding the toolkit functions. (default = False)
    """

    def __init__(
        self,
        tk_object: DeviceType,
        session: t.Union["ZISession", "Session", "Instrument"],
        name: t.Optional[str] = None,
        raw: bool = False,
    ):
        self._tk_object = tk_object
        self._session = session
        if not name:
            name = (
                f"zi_{tk_object.__class__.__name__.lower()}_{tk_object.serial.lower()}"
            )
        super().__init__(name, self._tk_object.root)

        if not raw:
            self._init_additional_nodes()
        init_nodetree(self, self._tk_object.root, self._snapshot_cache)

    def get_idn(self) -> t.Dict[str, t.Optional[str]]:
        """Fake a standard VISA ``*IDN?`` response."""
        return {
            "vendor": "Zurich Instruments",
            "model": self.device_type,
            "serial": self.serial,
            "firmware": self.system.fwrevision(),
        }

    def _init_additional_nodes(self) -> None:
        """Init additional qcodes parameter."""

    def factory_reset(self, deep: bool = True) -> None:
        """Load the factory default settings.

        Arguments:
            deep (bool): A flag that specifies if a synchronization
                should be performed between the device and the data
                server after loading the factory preset (default: True).
        """
        return self._tk_object.factory_reset(deep=deep)

    def check_compatibility(self) -> None:
        """Check if the software stack is compatible.

        Only if all versions and revisions of the software stack match stability
        can be ensured. The following criteria are checked:

        * minimum required zhinst-utils package is installed
        * minimum required zhinst-core package is installed
        * zhinst package matches the LabOne Data Server version
        * firmware revision matches the LabOne Data Server version

        Raises:
            ConnectionError: If the device is currently updating
            RuntimeError: If one of the above mentioned criteria is not
                fulfilled
        """
        self._tk_object.check_compatibility

    def get_streamingnodes(self) -> list:
        """Create a dictionary with all streaming nodes available."""
        return self._tk_object.get_streamingnodes()

    def set_transaction(self):
        """Context manager for a transactional set.

        Can be used as a context in a with statement and bundles all node set
        commands into a single transaction. This reduces the network overhead
        and often increases the speed.

        Within the with block a set commands to a node will be buffered
        and bundled into a single command at the end automatically.
        (All other operations, e.g. getting the value of a node, will not be
        affected)

        Warning:
            The set is always performed as deep set if called on device nodes.

        Examples:
            >>> with device.set_transaction():
                    device.test[0].a(1)
                    device.test[1].a(2)
        """
        return self._tk_object.set_transaction()

    @property
    def serial(self) -> str:
        """Instrument specific serial."""
        return self._tk_object.serial

    @property
    def device_type(self) -> str:
        """Type of the instrument (e.g. MFLI)."""
        return self._tk_object.device_type

    def device_options(self) -> str:
        """Enabled options of the instrument."""
        return self._tk_object.device_options

    @property
    def session(self) -> "Session":
        """Underlying session the device is connected through."""
        return self._session
