"""Base modules for the Zurich Instrument specific QCoDeS driver."""

import re
from datetime import datetime
import typing as t
from contextlib import contextmanager, nullcontext
from collections.abc import Mapping

import numpy as np
from qcodes.instrument.base import Instrument
from qcodes.instrument.channel import ChannelList, InstrumentChannel
from qcodes.instrument.parameter import Parameter
from qcodes.utils.validators import ComplexNumbers
from zhinst.toolkit.nodetree import Node, NodeTree
from zhinst.toolkit.nodetree.helper import NodeDict as TKNodeDict
from zhinst.toolkit.nodetree.node import NodeInfo


class ZISnapshotHelper:
    """Helper class for the snapshot with Zurich Instrument devices.

    Instead of getting each node with a single get command this class bundles
    the get into a single command and stores the returned values into a
    temporary dictionary.
    """

    def __init__(self, nodetree: NodeTree, is_module: bool = False):
        self._is_running = False
        self._value_dict: t.Dict[str, t.Any] = {}
        self._start = datetime.now()
        self._nodetree = nodetree
        self._is_module = is_module

    @contextmanager
    def snapshot(self, name: t.Optional[str] = None):
        """Context manager for a optimized snapshot with ZI devices."""
        is_owner = not self._is_running
        if is_owner:
            self._start_snapshot(name)
        try:
            yield
        finally:
            if is_owner:
                self._stop_snapshot()

    def _start_snapshot(self, name: t.Optional[str] = None) -> bool:
        """Start a snapshot and make a single get to the device.

        Args:
            name: Name of the subnode which the snapshot should
                be taken. If not specified a snapshot of all nodes will be taken.
                (default = None)

        Returns:
            bool: Flag if a new snapshot was started.
        """
        if not self._nodetree or self._is_running:
            return False
        self._is_running = True
        if not self._is_module:
            kwargs = {
                "excludestreaming": True,
                "settingsonly": False,
                "excludevectors": True,
                "flat": True,
            }
        else:
            kwargs = {"flat": True}
        prefix = self._nodetree.prefix_hide
        if not name:
            name = prefix if prefix else ""
        else:
            name = "/" + prefix + "/" + name
        self._value_dict = self._nodetree.connection.get(f"{name}/*", **kwargs)
        self._start = datetime.now()
        return True

    def _stop_snapshot(self) -> None:
        """Stop a snapshot to prevent use of outdate data by accident."""
        self._is_running = False
        self._value_dict = {}

    def get(self, parameter: Parameter, fallback_get: t.Callable) -> t.Any:
        """Get the value for a specific QCoDeS Parameter.

        Tries to mimic the behavior of a normal get (e.g. update cache).
        If the value is not found in the dictionary the fallback get is called.
        The fallback get should get the value from the device.

        Args:
            parameter: QCoDeS Parameter object
            fallback_get: fallback function to get the value from the device
        Returns:
            Value for the Node
        """
        value = self._value_dict.get(parameter.zi_node.lower())
        if value is not None:
            try:
                value = value["value"][0]
            except (IndexError, TypeError):
                # HF2 has no timestamp -> no dict
                value = value[0]
            # convert numpy types to standart types
            value = value.item() if hasattr(value, "item") else value
            # convert complex into string
            value = str(value) if isinstance(value, complex) else value
            parameter.cache._update_with(
                value=value, raw_value=value, timestamp=self._start
            )
        else:  # fallback is normal get
            value = fallback_get()
        return value

    @staticmethod
    def print_readable_snapshot(
        qcodes_object: Instrument, update: bool = False, max_chars: int = 80
    ) -> None:
        """Prints a readable version of the snapshot.

        The readable snapshot includes the name, value and unit of each
        parameter.
        A convenience function to quickly get an overview of the
        status of an instrument.

        Args:
            qcodes_object (object): Object for which the snapshot should be printed.
            update (bool): Flag if the state should be queried from the
                           instrument.
            max_chars (int): The maximum number of characters per line. The
                readable snapshot will be cropped if this value is exceeded.
                Defaults to 80 to be consistent with default terminal width.
        """
        floating_types = (float, np.integer, np.floating)
        snapshot = qcodes_object.snapshot(update=update)
        snapshot_parameters = snapshot.get("parameters")

        if snapshot_parameters:
            # Min of 50 is to prevent a super long parameter name to break this
            # function
            par_lengths = [len(p) for p in snapshot_parameters]
            par_field_len = min(max(par_lengths) + 1, 50) if par_lengths else 0

            print(qcodes_object.name + ":")
            print(f"\t{'parameter':<{par_field_len}}: value")
            print("\t" + "-" * (max_chars - 8))
            for parameter in sorted(snapshot_parameters):
                parameter = snapshot_parameters[parameter]
                name = parameter["name"]
                msg = f"\t{name:<{par_field_len}}:"

                # in case of e.g. ArrayParameters, that usually have
                # snapshot_value == False, the parameter may not have
                # a value in the snapshot
                val = parameter.get("value", "Not available")

                unit = parameter.get("unit", None)
                if unit is None:
                    # this may be a multi parameter
                    unit = parameter.get("units", None)
                if isinstance(val, floating_types):
                    msg += f"\t{val:.5g} "
                    # numpy float and int types format like builtins
                else:
                    msg += f"\t{val} "
                if unit != "":  # corresponds to no unit
                    msg += f"({unit})"
                # Truncate the message if it is longer than max length
                if len(msg) > max_chars and max_chars != -1:
                    msg = msg[0 : max_chars - 3] + "..."  # noqa: E203
                print(msg)

        for submodule in qcodes_object.submodules.values():
            submodule.print_readable_snapshot(update=update, max_chars=max_chars)

    @property
    def is_running(self) -> bool:
        """Flag if a snapshot is in progress."""
        return self._is_running


class ZIParameter(Parameter):
    """Zurich Instrument specific QCoDeS Parameter.

    Overwrite the snapshot functionality to use the ZISnapshotHelper.
    Forwards all args and kwargs to the QCoDeS Parameter class.

    Args:
        snapshot_cache (ZISnapshotHelper): ZI specific SnapshotHelper object
        zi_node (Node): ZI specific node object of the nodetree
    """

    def __init__(
        self,
        *args,
        snapshot_cache: ZISnapshotHelper,
        zi_node: str,
        tk_node: Node,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.get_raw = kwargs["get_cmd"]
        self.set_raw = kwargs["set_cmd"]
        self.get = self._wrap_get(self.get_raw)
        self.set = self._set_zi
        self._snapshot_cache = snapshot_cache
        self._zi_node = zi_node
        self._tk_node = tk_node

    def __call__(self, *args, **kwargs):
        """Call operator that either gets (empty) or gets the value of a node.

        Args:
            value: Optional value that should be set to the node. If not
                specified the operator will return the value of the node
                instead.
            deep: Flag if the operation should block until the device has
                acknowledged the operation. The operation returns the value
                acknowledged by the device. This takes significantly longer
                than a normal operation and should be used carefully.
            enum: Flag if enumerated values should return the enum value as
                string or return the raw number.
            parse: Flag if the GetParser or SetParser, if present, should be
                applied or not.

        Returns:
            Value of the node for a get operation. If the deep flag is set the
            acknowledged value from the device is returned (applies also for
            the set operation).

        Raises:
            AttributeError: If the connection does not support the necessary
                function to get/set the value.
            RuntimeError: If self.node_info.type if one of the following:
                [ZIPWAWave, ZITriggerSample, ZICntSample, ZIImpedanceSample,
                ZIScopeWave, ZIAuxInSample]. The reason is that these nodes can
                only be polled.
            TypeError: if the deep command is not available for this node
                (e.g. sample nodes)
        """
        if len(args) == 0:
            if self.gettable:
                return self.get(**kwargs)
            raise NotImplementedError("no get cmd found in" + f" Parameter {self.name}")
        if self.settable:
            return self.set(*args, **kwargs)
        raise NotImplementedError("no set cmd found in" + f" Parameter {self.name}")

    def _set_zi(self, *args, **kwargs):
        """ZI specific set that supports returning values.

        QCoDeS does not provide a way to return a value for the set command.
        However a `deep` command in LabOne does return the acknowledged value
        by the device. This function in combination with the custom `__call__`
        method bypasses this problem.

        This function simply wraps around the QCoDeS specific set functionality
        (_wrap_set) stores the returned value by zhinst-toolkit and calls the
        get functionality with the returned value. Thus is acts as a set and
        get within on single command without overwriting the QCoDeS specific
        implementation.
        """
        set_return = None

        def set_wrapper(*args, **kwargs) -> None:
            nonlocal set_return
            set_return = self.set_raw(*args, **kwargs)

        self._wrap_set(set_wrapper)(*args, **kwargs)
        return self._wrap_get(lambda: set_return)() if set_return is not None else None

    def snapshot_base(
        self, update: bool = True, params_to_skip_update: t.List[str] = None
    ) -> dict:
        """State of the parameter as a JSON-compatible dict.

        (everything that the custom JSON encoder class
        :class:`qcodes.utils.helpers.NumpyJSONEncoder` supports)

        If the parameter has been initiated with ``snapshot_value=False``,
        the snapshot will NOT include the ``value`` and ``raw_value`` of the
        parameter.

        Overwrite base class function to use the snapshot_cache.

        Args:
            update: If True, update the state by calling ``parameter.get()``
                unless ``snapshot_get`` of the parameter is ``False``.
                If ``update`` is ``None``, use the current value from the
                ``cache`` unless the cache is invalid. If ``False``, never call
                ``parameter.get()``.
            params_to_skip_update: No effect but may be passed from base class

        Returns:
            base snapshot
        """
        get = self.__dict__["get"]
        try:
            self.get = lambda: self._snapshot_cache.get(self, get)
            return super().snapshot_base(
                update=update, params_to_skip_update=params_to_skip_update
            )
        finally:
            self.get = get

    def subscribe(self) -> None:
        """Subscribe to nodes. Fetch data with the poll command.

        In order to avoid fetching old data that is still in the buffer execute
        a flush command before subscribing to data streams.
        """
        self._tk_node.subscribe()

    def unsubscribe(self) -> None:
        """Unsubscribe data stream.

        Use this command after recording to avoid buffer overflows that may
        increase the latency of other command.
        """
        self._tk_node.unsubscribe()

    def get_as_event(self) -> None:
        """Trigger an event.

        The node data is returned by a subsequent poll command.
        """
        self._tk_node.get_as_event()

    def wait_for_state_change(
        self,
        value: t.Union[int, str],
        *,
        invert: bool = False,
        timeout: float = 2,
        sleep_time: float = 0.005,
    ) -> None:
        """Waits until the node has the expected state/value.

        WARNING: Only supports integer values as reference.

        Args:
            value: expected value of the node.
            invert: Instead of waiting for the value, the function will wait for
                any value except the passed value instead. (default = False)

                Useful when waiting for value to change from existing one.
            timeout: max wait time. (default = 2)
            sleep_time: sleep interval in seconds. (default = 0.006)
        """
        self._tk_node.wait_for_state_change(
            value, invert=invert, timeout=timeout, sleep_time=sleep_time
        )

    @property
    def node_info(self) -> NodeInfo:
        """Zurich Instrument node representation of the Parameter."""
        return self._tk_node.node_info

    @property
    def zi_node(self) -> Node:
        """Zurich Instrument node representation of the Parameter."""
        return self._zi_node

    @property
    def tk_node(self) -> Node:
        """Toolkit node of the Parameter."""
        return self._tk_node


class ZINode(InstrumentChannel):
    """Zurich Instrument specific QCoDeS InstrumentChannel.

    Overwrite the snapshot functionality to use the ZISnapshotHelper.
    Forwards all args and kwargs to the QCoDeS InstrumentChannel class.

    Args:
        snapshot_cache (ZISnapshotHelper): ZI specific SnapshotHelper object
        zi_node (Node): ZI specific node object of the nodetree
    """

    def __init__(
        self,
        *args,
        snapshot_cache: ZISnapshotHelper,
        zi_node: Node = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._snapshot_cache = snapshot_cache
        self._zi_node = zi_node

    def snapshot(self, update: bool = True) -> dict:
        """Decorate a snapshot dictionary with metadata.

        Override base method to make update default True and use the
        ZISnapshotHelper.

        Args:
            update: Passed to snapshot_base. (default = True)

        Returns:
            dict: Base snapshot.
        """
        with self._snapshot_cache.snapshot(self._zi_node) if update else nullcontext():
            return super().snapshot(update)

    def print_readable_snapshot(self, update: bool = True, max_chars: int = 80) -> None:
        """Prints a readable version of the snapshot.

        The readable snapshot includes the name, value and unit of each
        parameter.
        A convenience function to quickly get an overview of the
        status of an instrument.

        Args:
            update: If ``True``, update the state by querying the
                instrument. If ``False``, just use the latest values in memory.
                This argument gets passed to the snapshot function.
            max_chars: the maximum number of characters per line. The
                readable snapshot will be cropped if this value is exceeded.
                Defaults to 80 to be consistent with default terminal width.
        """
        with self._snapshot_cache.snapshot(self._zi_node) if update else nullcontext():
            return super().print_readable_snapshot(update, max_chars)


class ZIChannelList(ChannelList):
    """Zurich Instrument specific QCoDeS InstrumentChannel.

    Overwrite the snapshot functionality to use the ZISnapshotHelper.
    Forwards all args and kwargs to the QCoDeS InstrumentChannel class.

    Args:
        snapshot_cache (ZISnapshotHelper): ZI specific SnapshotHelper object
        zi_node (Node): ZI specific node object of the nodetree
    """

    def __init__(self, *args, snapshot_cache=None, zi_node=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._snapshot_cache = snapshot_cache
        self._zi_node = zi_node

    def snapshot(self, update: bool = True) -> dict:
        """Decorate a snapshot dictionary with metadata.

        Override base method to make update default True and use the
        ZISnapshotHelper.

        Args:
            update: Passed to snapshot_base. (default = True)

        Returns:
            dict: Base snapshot.
        """
        with self._snapshot_cache.snapshot(self._zi_node) if update else nullcontext():
            return super().snapshot(update)

    def print_readable_snapshot(self, update: bool = True, max_chars: int = 80) -> None:
        """Prints a readable version of the snapshot.

        The readable snapshot includes the name, value and unit of each
        parameter.
        A convenience function to quickly get an overview of the
        status of an instrument.

        Args:
            update: If ``True``, update the state by querying the
                instrument. If ``False``, just use the latest values in memory.
                This argument gets passed to the snapshot function.
            max_chars: the maximum number of characters per line. The
                readable snapshot will be cropped if this value is exceeded.
                Defaults to 80 to be consistent with default terminal width.
        """
        with self._snapshot_cache.snapshot(self._zi_node) if update else nullcontext():
            return super().print_readable_snapshot(update, max_chars)


class ZIInstrument(Instrument):
    """Zurich Instrument specific Qcodes Instrument.

    Overwrite the snapshot functionality to use the ZISnapshotHelper.

    Args:
        name: Name of
        snapshot_cache (ZISnapshotHelper): ZI specific SnapshotHelper object
        zi_node (Node): ZI specific node object of the nodetree
    """

    def __init__(self, name, nodetree: NodeTree, is_module=False):
        super().__init__(name)
        self._snapshot_cache = ZISnapshotHelper(nodetree, is_module=is_module)

    def snapshot(self, update: bool = True) -> dict:
        """Decorate a snapshot dictionary with metadata.

        Override base method to make update default True and use the
        ZISnapshotHelper.

        Args:
            update: Passed to snapshot_base.

        Returns:
            dict: Base snapshot.
        """
        with self._snapshot_cache.snapshot() if update else nullcontext():
            return super().snapshot(update)

    def print_readable_snapshot(self, update: bool = True, max_chars: int = 80) -> None:
        """Prints a readable version of the snapshot.

        The readable snapshot includes the name, value and unit of each
        parameter.
        A convenience function to quickly get an overview of the
        status of an instrument.

        Args:
            update: If ``True``, update the state by querying the
                instrument. If ``False``, just use the latest values in memory.
                This argument gets passed to the snapshot function.
            max_chars: the maximum number of characters per line. The
                readable snapshot will be cropped if this value is exceeded.
                Defaults to 80 to be consistent with default terminal width.
        """
        with self._snapshot_cache.snapshot() if update else nullcontext():
            return super().print_readable_snapshot(update, max_chars)


class NodeDict(Mapping):
    """Mapping of dictionary structure results.

    The mapping allows to access data with both the string and the qcodes
    parameter objects.
    """

    def __init__(self, tk_result: t.Union[t.Dict[str, t.Any], TKNodeDict]):
        if not isinstance(tk_result, TKNodeDict):
            self._result = TKNodeDict(tk_result)
        else:
            self._result = tk_result

    def __repr__(self):
        return repr(self._result)

    def __getitem__(self, key: t.Union[str, ZIParameter]):
        if isinstance(key, ZIParameter):
            return self._result[key.zi_node.lower()]
        return self._result[key]

    def __iter__(self):
        return iter(self._result)

    def __len__(self):
        return len(self._result)

    def to_dict(self) -> t.Dict[str, t.Any]:
        """Convert the WildcardResult to a dictionary.

        After conversion, :class:`Node` objects cannot be used to get items.
        """
        return self._result.to_dict()


def tk_node_to_qcodes_list(tk_node: Node) -> t.List[str]:
    """Convert a toolkit node to a list of elements that form a QCoDeS object.

    Args:
        tk_node: Toolkit node to convert.

    Return:
        List of strings that form a QCoDeS object.
    """
    if tk_node.raw_tree[-1].isdigit():
        parents = tk_node.raw_tree
        name = "value"
    else:
        parents = tk_node.raw_tree[:-1]
        name = tk_node.raw_tree[-1]
        # Attributes are not allowed to start with a number (#31)
        name = "_" + name if name[0].isdigit() else name
    parents = list(parents)
    numbers = [subnode for subnode in parents if subnode.isdigit()]
    while numbers:
        number = numbers.pop()
        index = parents.index(number)
        parents[index - 1] = parents[index - 1] + number
        parents.pop(index)
        if not numbers:
            numbers = [subnode for subnode in parents if subnode.isdigit()]
    parents.append(name)
    return parents


def tk_node_to_parameter(root: t.Any, tk_node: Node) -> t.Any:
    """Convert a Toolkit node into a QCoDeS Parameter.

    Args:
        root: Root from which the node should be derived.
        tk_node: Toolkit node to convert.

    Returns:
        QCoDeS Parameter that matches the given tk node.
    """
    qcodes_list = list(tk_node.raw_tree)
    if qcodes_list[-1].isdigit():
        qcodes_list.append("value")
    current_layer = root
    for element in qcodes_list[:-1]:
        qcodes_list = tk_node_to_qcodes_list(tk_node)
        if element.isdigit():
            current_layer = current_layer[int(element)]
        else:
            current_layer = current_layer.submodules[element]
    return current_layer.parameters[qcodes_list[-1]]


def _get_submodule(
    layer, parents: t.List[str], snapshot_cache: ZISnapshotHelper
) -> ZINode:
    """Get the nested parent element for a node.

    Reuse existing subnodes and automatically create them if they don`t
    exist.

    Args:
        parents: Nested parents of a node as str.
        snapshot_cache: Object of the snapshot cache.

    Returns:
        ZINode: direct parent of the node
    """
    weird_nodes = ["tamp0", "tamp1"]
    current_layer = layer
    for i, node in enumerate(parents):
        if node[-1].isdigit() and node not in weird_nodes:
            offset = 0
            for char in reversed(node):
                if char.isdigit():
                    offset += 1
                else:
                    break
            number = int(node[-offset:])
            name = node[:-offset]
            if not current_layer.submodules or name not in current_layer.submodules:
                # create channel_list
                channel_list = ZIChannelList(
                    current_layer,
                    name,
                    ZINode,
                    zi_node="/".join(parents[:i] + [name]),
                    snapshot_cache=snapshot_cache,
                )
                current_layer.add_submodule(name, channel_list)
            if len(current_layer.submodules[name]) <= number:
                # Add new items to list until the required length is reached. (#31)
                current_length = len(current_layer.submodules[name])
                for item in range(number - current_length + 1):
                    module = ZINode(
                        current_layer,
                        name + str(current_length + item),
                        zi_node="/".join(
                            parents[:i] + [name, str(current_length + item)]
                        ),
                        snapshot_cache=snapshot_cache,
                    )
                    current_layer.submodules[name].append(module)
            current_layer = current_layer.submodules[name][number]
        elif node not in current_layer.submodules:
            module = ZINode(
                current_layer,
                node,
                zi_node="/".join(parents[: i + 1]),
                snapshot_cache=snapshot_cache,
            )
            current_layer.add_submodule(node, module)
            current_layer = module
        else:
            current_layer = current_layer.submodules.get(node)
    return current_layer


def init_nodetree(
    layer,
    nodetree: NodeTree,
    snapshot_cache: ZISnapshotHelper,
    blacklist: tuple = tuple(),
) -> None:
    """Generate nested qcodes parameter from the device nodetree.

    Args:
        layer: current layer in the nodetree.
        nodetree: underlying toolkit node tree.
        snapshot_cache: Instance of the SnapshotHelper.
        blacklist: nodes to be blacklisted.
    """
    snapshot_blacklist = ["fwlog", "values"]

    is_complex = re.compile("demods/./sample")

    for node, info in nodetree:
        if info.get("Node", "") in blacklist:
            continue
        try:
            qcodes_list = tk_node_to_qcodes_list(node)
            name = qcodes_list[-1]
            parent = _get_submodule(layer, qcodes_list[:-1], snapshot_cache)
            do_snapshot = (
                "Stream" not in info.get("Properties")
                and "ZIVector" not in info.get("Type")
                and "Read" in info.get("Properties")
                and not any(x in node.raw_tree for x in snapshot_blacklist)
            )
            name = name + "_" if hasattr(parent, name) else name
            parent.add_parameter(
                parameter_class=ZIParameter,
                name=name,
                docstring=info.get("Description"),
                unit=(
                    info.get("Unit")
                    if info.get("Unit") not in ["None", "Dependent"]
                    else None
                ),
                get_cmd=node._get,
                set_cmd=node._set,
                vals=(
                    ComplexNumbers()
                    if re.match(is_complex, info.get("Node").lower())
                    else None
                ),
                snapshot_value=do_snapshot,
                snapshot_get=do_snapshot,
                zi_node=info.get("Node"),
                tk_node=node,
                snapshot_cache=snapshot_cache,
            )
        except ValueError as e:
            print(f"Node {info.get('Node')} could not be added as parameter\n", e)
