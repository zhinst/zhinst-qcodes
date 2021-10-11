from functools import partial
import re

from qcodes.instrument.base import Instrument
from qcodes.instrument.channel import ChannelList, InstrumentChannel
from qcodes.utils.validators import ComplexNumbers
import zhinst.toolkit as tk
from typing import List, Dict


class ZIQcodesException(Exception):
    pass


class ZINode(InstrumentChannel):
    """Implements a node in the instrument nodetree as a
    :class:`InstrumentChannel`.

    :class:`ZINode` class collects *submodules* (which may again be *ZINodes*)
    and *parameters* to represent the hirarchy of the Zurich Instruments node
    tree in *QCoDeS*. It inherits from :class:`InstrumentChannel` and overrides
    the snapshot method.

    """

    def print_readable_snapshot(
        self, update: bool = False, max_chars: int = 80
    ) -> None:
        if self.parameters:
            super().print_readable_snapshot(update=update, max_chars=max_chars)
        else:
            print(self.name + ":")
            print("{0:<{1}}".format("\tparameter ", max_chars) + "value")
            print("-" * max_chars)
            print("no parameters")
            for submodule in self.submodules.values():
                submodule.print_readable_snapshot(update=update, max_chars=max_chars)


class ZIBaseInstrument(Instrument):
    """Base class for all Zurich Instruments QCoDeS drivers.

    Implements basic wrapper around :mod:`zhinst-toolkit` deice drivers and
    translates the nodetree to a hirarchy of *QCoDeS submodules*
    (:class:`ZINodes`) and *parameters*.

    Arguments:
        name (str): The *QCoDeS* name of the instrument
        device_type (str): The device type, e.g. *'mfli'*.
        serial (str): The device serial number.

    Keyword Arguments:
        interface (str): The interface used to connect to the
            device (default: *'1GbE'*).
        host (str): Address of the data server. (default: 'localhost')
        port (int): Port used to connect to the data server. (default: 8004)
        api (int): Api level used. (default: 6)

    """

    def __init__(
        self,
        name: str,
        device_type: str,
        serial: str,
        interface: str = "1gbe",
        host: str = "localhost",
        port: int = 8004,
        api: int = 6,
        **kwargs,
    ) -> None:
        super().__init__(name, **kwargs)
        self._type = device_type
        self._serial = serial
        self._interface = interface
        self._host = host
        self._port = port
        self._api = api
        self.zi_submodules = {}
        supported_types = ["hdawg", "uhfqa", "uhfli", "mfli", "shfqa", "shfsg", "pqsc"]
        if device_type not in supported_types:
            raise ZIQcodesException(
                f"Device type {device_type} is currently not supported in ziQCoDeS. Supported types are {supported_types}"
            )
        self._connect()

    def _connect(self) -> None:
        """
        Instantiates the device controller from zhinst-toolkit, sets up the data
        server and connects the device the data server. This method is called
        from __init__ of the base instrument class.

        """
        # use zhinst.toolkit.tools.BaseController() to interface the device
        self._controller = tk.BaseInstrument(
            self._name,
            self._type,
            self._serial,
            interface=self._interface,
            host=self._host,
            port=self._port,
            api=self._api,
        )
        self._controller.setup()
        self._controller.connect_device()
        self.connect_message()
        self.nodetree_dict = self._controller.nodetree._nodetree_dict
        self._add_qcodes_params()

    def _add_qcodes_params(self):
        # add custom parameters as QCoDeS parameters
        self.add_parameter(
            "data_server_version",
            unit=self._controller.data_server_version._unit,
            docstring=self._controller.data_server_version.__repr__(),
            get_cmd=self._controller.data_server_version,
            set_cmd=self._controller.data_server_version,
            label="Zurich Instruments Data Server Version",
        )
        self.add_parameter(
            "firmware_version",
            unit=self._controller.firmware_version._unit,
            docstring=self._controller.firmware_version.__repr__(),
            get_cmd=self._controller.firmware_version,
            set_cmd=self._controller.firmware_version,
            label="Revision of Device Internal Controller Software",
        )
        self.add_parameter(
            "fpga_version",
            unit=self._controller.fpga_version._unit,
            docstring=self._controller.fpga_version.__repr__(),
            get_cmd=self._controller.fpga_version,
            set_cmd=self._controller.fpga_version,
            label="HDL Firmware Revision",
        )

    def sync(self):
        """Perform a global synchronisation between the device and the
        data server.

        Eventually wraps around the daq.sync() of the API.

        Raises:
            ToolkitError: If called and the device in not yet connected
                to the data server.

        """
        self._controller.sync()

    def _init_submodule(self, key: str) -> None:
        """
        Recursively initialize submodules from highest layer keys in nodetree
        dictionary.For e.g. 'dev8030/sigouts/...' one would call this method
        with 'sigouts'.

        Arguments:
            key (str): dictionary key in the highest layer of nodetree dictionary

        """
        if key in self.nodetree_dict.keys():
            self._add_submodules_recursively(self, {key: self.nodetree_dict[key]})
        else:
            print(f"Key {key} not in nodetree: {list(self.nodetree_dict.keys())}")

    def _add_submodules_recursively(self, parent, treedict: Dict) -> None:
        """
        Recursively add submodules (ZINodes) for each node in the ZI node tree.
        At the leaves create a parameter. Create a ChannelList as submodules
        whenever a node is enumerated, e.g. 'dev8030/sigouts/*/on'.

        Arguments:
            parent (InstrumentChannel): parent QCoDeS object, either
                Instrument(-Channel) or ZINode
            treedict (dict): dictionary specifying the (sub-)tree of the ZI
                node hirarchy

        """
        for key, value in treedict.items():
            if all(isinstance(k, int) for k in value.keys()):
                # if enumerated node
                if "Node" in list(value.values())[0].keys():
                    # if at leave, don't create ChannelList but parameter with "{key}{i}"
                    for k in value.keys():
                        self._add_parameter_from_dict(parent, f"{key}{k}", value[k])
                else:
                    # else, create ChannelList to hold all enumerated ZINodes
                    channel_list = ChannelList(parent, key, ZINode)
                    for k in value.keys():
                        ch_name = f"{key}{k}"
                        ch = ZINode(parent, ch_name)
                        channel_list.append(ch)
                        self._add_submodules_recursively(ch, treedict[key][k])
                    channel_list.lock()
                    parent.add_submodule(key, channel_list)
            else:
                # if not enumerated ZINode
                if "Node" in value.keys():
                    # if at leave add a parameter to the node
                    self._add_parameter_from_dict(parent, key, value)
                else:
                    # if not at leave, create ZINode as submodule
                    module = ZINode(parent, key)
                    parent.add_submodule(key, module)
                    self._add_submodules_recursively(module, treedict[key])

    def _add_parameter_from_dict(self, instr, name: str, params: Dict) -> None:
        """
        Add a QCoDeS parameter associated to a ZI node from a dict describing
        the parameter with e.g. 'Node', 'Properties', 'Description', 'Options'
        etc.

        Arguments:
            instr: instrument/submodule the parameter is associated with
            name (str): parameter name
            params (dict): dictionary describing the parameter, innermost layer of nodetree dictionary

        """
        node = params["Node"].lower().replace(f"/{self._serial}/", "")
        demod_sample = re.compile("demods/./sample")
        if "Read" in params["Properties"]:
            # use controller.get("device name", "node") as getter
            getter = partial(self._controller._get, node)
        else:
            getter = None
        if "Write" in params["Properties"]:
            # use controller.set("device name", "node", value) as setter
            setter = partial(self._controller._set, node)
        else:
            setter = False
        if "Setting" in params["Properties"]:
            snapshot_exclude = False
        else:
            snapshot_exclude = True

        instr.add_parameter(
            name=name,
            docstring=_dict_to_doc(params),
            unit=params["Unit"] if params["Unit"] != "None" else None,
            get_cmd=getter,
            set_cmd=setter,
            vals=ComplexNumbers() if re.match(demod_sample, node) else None,
            snapshot_exclude=snapshot_exclude,
        )

    def get_idn(self) -> Dict:
        return dict(
            vendor="Zurich Instruments",
            model=self._type.upper(),
            serial=self._serial,
            firmware=self._controller._get("system/fwrevision"),
        )


"""
Helper functions used to process the nodetree dictionary in ZIBaseInstrument.

"""


def _dict_to_doc(d: Dict) -> str:
    """
    Turn dictionary into pretty doc string.

    Arguments:
        d (dict)

    Returns:
        s (str): A pretty string that lists the key/value pairs of the given
            dictionary for documentation.

    """
    s = ""
    for k, v in d.items():
        s += f"- '{k}'': {v}\n"
    return s
