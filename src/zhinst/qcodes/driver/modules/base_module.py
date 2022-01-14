"""Base Module Driver

Nativly works with all module types and provides the basic functionality like
the module specific nodetree.
"""
import typing as t

from zhinst.toolkit.driver.modules.base_module import BaseModule as TKBaseModule

from zhinst.qcodes.driver.devices.base import ZIBaseInstrument
from zhinst.qcodes.qcodes_adaptions import (
    ZIInstrument,
    ZIParameter,
    init_nodetree,
    tk_node_to_parameter,
)

if t.TYPE_CHECKING:
    from zhinst.qcodes.session import Session


class ZIBaseModule(ZIInstrument):
    """Generic QCodes driver for the Zurich Instrument LabOne modules.

    All module specific class are derived from this class.
    It exposes the nodetree and also implements common functions valid for all
    modules.
    It also can be used directly, e.g. for modules that have no special class
    in toolkit.

    Args:
        tk_object: Instance of the toolkit base module.
        session: Session to the Data Server.
        name: Name of the Module
    """

    def __init__(self, tk_object: TKBaseModule, session: "Session", name: "str"):
        super().__init__(
            f"zi_{name}_{len(self.instances())}", tk_object.root, is_module=True
        )
        self._tk_object = tk_object
        self._session = session
        init_nodetree(
            self, self._tk_object, self._snapshot_cache, blacklist=("/device",)
        )

    def _get_node(self, node: str) -> t.Union[ZIParameter, str]:
        """Convert a raw node string into a qcodes node.

        Args:
            node (str): raw node string

        Returns:
            Node: qcodes node. (if the node can not be converted the raw node
                string is returned)
        """
        tk_node = self._tk_object._get_node(node)
        if isinstance(tk_node, str):
            return tk_node
        device = self._session.devices[tk_node.root.prefix_hide]
        return tk_node_to_parameter(device, tk_node)

    @staticmethod
    def _set_node(signal: t.Union[ZIParameter, str]) -> str:
        """Convert a toolkit node into a raw node string.

        Args:
            signal (Union[Node,str]): node

        Returns:
            str: raw string node
        """
        try:
            node = signal.zi_node
        except AttributeError:
            node = signal
        return node

    def device(self, device: t.Union[t.Type[ZIBaseInstrument], str] = None):
        if device is None:
            serial = self._tk_object.device(parse=False)
            try:
                return self._session.devices[serial]
            except (RuntimeError, KeyError):
                return serial
        self._tk_object.device(device)

    def subscribe(self, signal: ZIParameter):
        """Subscribe to a node.

        The node can either be a node of this module or of a connected device.

        Args:
            signal (Node): node that should be subcribed.
        """
        self._tk_object.subscribe(signal.tk_node)

    def unsubscribe(self, signal: ZIParameter):
        """Unsubscribe from a node.

        The node can either be a node of this module or of a connected device.

        Args:
            signal (Node): node that should be unsubscribe.
        """
        self._tk_object.unsubscribe(signal.tk_node)

    def wait_done(self, timeout: float = 20.0, sleep_time: float = 0.5) -> None:
        """Waits until the module is finished.

        Warning: Only usable for modules that make use of the `/finished` node.

        Args:
            timeout (float): The maximum waiting time in seconds for the
                measurment (default: 20).
            sleep_time (int): Time in seconds to wait between
                requesting sweeper state. (default: 0.5)
        Raises:
            TimeoutError: if the measurement is not completed before
                timeout.
        """
        return self._tk_object.wait_done(timeout=timeout, sleep_time=sleep_time)

    @property
    def raw_module(self) -> t.Any:
        return self._tk_object.raw_module
