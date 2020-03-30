from functools import partial

from qcodes.instrument.base import Instrument
from qcodes.instrument.channel import ChannelList, InstrumentChannel
import zhinst.toolkit as tk


class ZIQcodesException(Exception):
    pass


class ZINode(InstrumentChannel):
    """
    ZINode class collects submodules (which can be again ZINodes) 
    and parameters to represent the hirarchy of the ZI node tree in QCoDeS. 
    It inherits from InstrumentChannel and overrides the __repr__ and snapshot methods

    """

    def print_readable_snapshot(
        self, update: bool = False, max_chars: int = 80
    ) -> None:
        if self.parameters:
            super().print_readable_snapshot(update=update, max_chars=max_chars)
        else:
            print(self.name + ":")
            print("{0:<{1}}".format("\tparameter ", 50) + "value")
            print("-" * max_chars)
            print("no parameters")
            for submodule in self.submodules.values():
                submodule.print_readable_snapshot(update=update, max_chars=max_chars)


class ZIBaseInstrument(Instrument):
    """
    Base class for all ZI Instruments. Implements basic wrapper 
    around ziDrivers.Controller() and translates the ZI node tree 
    to a QCoDeS hirarchy of ZINodes

    Arguments:
        name (str): The internal QCoDeS name of the instrument
        device_type (str): The device type, e.g. 'mfli'
        serial (str): The device name as listed in the web server
        interface (str): The interface used to connect to the 
            device (default: '1gbe')
        host (str): Address of the data server (default: 'localhost')
        port (int): Port used to connect to the data server (default: 8004)
        api (int): Api level used (default: 6)

    """

    def __init__(
        self,
        name: str,
        device_type: str,
        serial: str,
        interface="1gbe",
        host="localhost",
        port=8004,
        api=6,
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
        supported_types = ["hdawg", "uhfqa", "uhfli", "mfli"]
        if device_type not in supported_types:
            raise ZIQcodesException(
                f"Device type {device_type} is currently not supported in ziQCoDeS. Supported types are {supported_types}"
            )
        self._connect()

    def connect(self):
        """
        Instantiates the device controller from zhinst-toolkit, sets up the data 
        server and connects the device the data server. This method is called 
        from __init__ of the base instruemnt class.
        
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
        self._controller.connect_device(nodetree=False)
        self.connect_message()
        # get the nodetree from the device as a nested dict
        self._get_nodetree_dict()

    def _init_submodule(self, key):
        """
        Recursively initialize submodules from highest layer keys in nodetree 
        dictionary.For e.g. 'dev8030/sigouts/...' one would call this method 
        with 'sigouts'.
        
        Arguments:
            key (str): dictionary key in the highest layer of nodetree_dict

        """
        if key in self.nodetree_dict.keys():
            self._add_submodules_recursively(self, {key: self.nodetree_dict[key]})
        else:
            print(f"Key {key} not in nodetree: {list(self.nodetree_dict.keys())}")

    def _get_nodetree_dict(self):
        """
        Retrieve the nodetree from the device as a nested dict and process it accordingly.

        """
        tree = self._controller._get_nodetree(f"{self._serial}/*")
        self.nodetree_dict = dict()
        for key, value in tree.items():
            key = key.replace(f"/{self._serial.upper()}/", "")
            hirarchy = key.split("/")
            dictify(self.nodetree_dict, hirarchy, value)

    def _add_submodules_recursively(self, parent, treedict: dict):
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

    def _add_parameter_from_dict(self, instr, name, params):
        """
        Add a QCoDeS parameter associated to a ZI noe from a dict describing 
        the parameter with e.g. 'Node', 'Properties', 'Description', 'Options' etc.
        
        Arguments:
            instr: instrument/submodule the parameter is associated with
            name (str): parameter name
            params (dict): dictionary describing the parameter, innermost layer of nodetree_dict

        """
        node = params["Node"].lower().replace(f"/{self._serial}/", "")
        if "Read" in params["Properties"]:
            # use controller.get("device name", "node") as getter
            getter = partial(self._controller._get, node)
        else:
            getter = None
        if "Write" in params["Properties"]:
            # use controller.set("device name", "node", value) as setter
            setter = partial(self._controller._set, node)
        else:
            setter = None
        instr.add_parameter(
            name=name,
            docstring=dict_to_doc(params),
            unit=params["Unit"] if params["Unit"] != "None" else None,
            get_cmd=getter,
            set_cmd=setter,
        )

    def get_idn(self):
        return dict(
            vendor="Zurich Instruments",
            model=self._type.upper(),
            serial=self._serial,
            firmware=self._controller._get("system/fwrevision"),
        )


"""
Helper functions used to process the nodetree dictionary in ZIBaseInstrument.

"""


def dictify(data, keys, val):
    """
    Helper function to generate nested dictionary from list of keys and value. 
    Calls itself recursively.
    
    Arguments:
        data (dict): dictionary to add value to with keys
        keys (list): list of keys to traverse along tree and place value
        val (dict): value for innermost layer of nested dict

    """
    key = keys[0]
    key = int(key) if key.isdecimal() else key.lower()
    if len(keys) == 1:
        data[key] = val
    else:
        if key in data.keys():
            data[key] = dictify(data[key], keys[1:], val)
        else:
            data[key] = dictify({}, keys[1:], val)
    return data


def dict_to_doc(d):
    """
    Turn dictionary into pretty doc string.

    Arguments:
        d (dict)

    """
    s = ""
    for k, v in d.items():
        s += f"* {k}:\n\t{v}\n\n"
    return s
