"""Sweeper Module."""

import typing as t
from zhinst.toolkit.driver.modules.sweeper_module import (
    SweeperModule as TKSweeperModule,
)

from zhinst.qcodes.driver.modules.base_module import ZIBaseModule
from zhinst.qcodes.qcodes_adaptions import ZIParameter, tk_node_to_parameter

if t.TYPE_CHECKING:
    from zhinst.qcodes.session import Session


class ZISweeperModule(ZIBaseModule):
    """Implements a base Sweeper Module for Lock-In instruments.

    The Sweeper Module allows for simple and efficient parameter sweeps while
    acquiring data streams from mutiple different signal sources. The module
    supports well defined sweeps of various parameters as well as application
    specific measurement presets. For more information on how to use the Sweeper
    Module, have a look at the LabOne Programming Manual.

    For a complete documentation see the LabOne user manual
    https://docs.zhinst.com/labone_programming_manual/sweeper_module.html

    Args:
        tk_object: Instance of the toolkit sweeper module.
        session: Session to the Data Server.
    """

    def __init__(self, tk_object: TKSweeperModule, session: "Session"):
        super().__init__(tk_object, session, "sweeper_module")
        self._tk_object.root.update_nodes(
            {
                "/gridnode": {
                    "GetParser": lambda value: self._get_node(value),
                    "SetParser": lambda value: self._set_node(value),
                }
            }
        )

    def execute(self) -> None:
        """Start the sweeper.

        Subscription or unsubscription is not possible until the sweep is finished."""
        self._tk_object.execute()

    def read(self) -> t.Dict[ZIParameter, t.List]:
        """Read the aquired data from the module.

        The Data is split into bursts.

        Returns:
            Result of the burst grouped by the signals.
        """
        tk_result = self._tk_object.read()
        results = {}
        for tk_node, data in tk_result.items():
            if tk_node.raw_tree == ("device",):
                results["device"] = data
            else:
                if tk_node.root.prefix_hide:
                    device = self._session.devices[tk_node.root.prefix_hide]
                else:
                    device = self
                parameter = tk_node_to_parameter(device, tk_node)
                results[parameter] = data
        return results
