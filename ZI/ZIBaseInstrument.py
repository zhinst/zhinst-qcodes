from ziDrivers import Controller
from functools import partial

from qcodes.instrument.base import Instrument
from qcodes.instrument.channel import InstrumentChannel, ChannelList
from qcodes.utils import validators as validators



class ZINode(InstrumentChannel):
    """
    ZINode class collects submodules (which can be again ZINodes) 
    and parameters to represent the hirarchy of the ZI node tree in QCoDeS. 
    It inherits from InstrumentChannel and overrides the __repr__ and snapshot methods
    """
    def print_readable_snapshot(self, update: bool = False, max_chars: int = 80) -> None:
        if self.parameters:
            super().print_readable_snapshot(update=update, max_chars=max_chars)
        else:
            print(self.name + ":")
            print("{0:<{1}}".format("\tparameter ", 50) + "value")
            print("-"*max_chars)
            print("no parameters")
            for submodule in self.submodules.values():
                submodule.print_readable_snapshot(update=update, max_chars=max_chars)

    def __repr__(self):
        s = f"ZINode: \n"
        s += f"     submodules: \n"
        for m in self.submodules.keys():
            s += f"         * {m}\n"
        s += f"     parameters: \n"
        for p in self.parameters.keys():
            s += f"         * {p}\n"  
        return s
 



class ZIBaseInstrument(Instrument):
    """
    Base class for all ZI Instruments. Implements basic wrapper 
    around ziDrivers.Controller() and translates the ZI node tree 
    to a QCoDeS hirarchy of ZINodes
    """
    def __init__(self, name: str, type: str, serial: str, interface="1gbe", **kwargs) -> None:
        """
        Create an instance of the instrument.

        Args:
            name: The internal QCoDeS name of the instrument
            device_ID: The device name as listed in the web server.
        """
        super().__init__(name, **kwargs)
        self._serial = serial
        self._type = type
        if type not in ["hdawg", "uhfqa"]:
            raise Exception()
        self._dev = f"{type}0"

        self._controller = Controller()        
        self._controller.setup(f"connection-{type}.json")
        self._controller.connect_device(self._dev, serial, interface)
        self.connect_message()
        self.__get_nodetree_dict()

    def _init_submodule(self, key):
        """
        Recursively initialize submodules from highest layer keys in nodetree dictionary.
        For e.g. 'dev8030/sigouts/...' one would call this method with 'sigouts'.
        
        Arguments:
            key  -- dictionary key in the highest layer of nodetree_dict
        """
        if key in self.nodetree_dict.keys():
            self.__add_submodules_recursively(self, {key: self.nodetree_dict[key]})
        else:
            print(f"Key {key} not in nodetree: {list(self.nodetree_dict.keys())}")

    
    def __get_nodetree_dict(self):
        """
        Retrieve the nodetree from the device as a nested dict and process it accordingly.
        """
        tree = self._controller.get_nodetree(f"{self._serial}/*")
        self.nodetree_dict = dict()
        for key, value in tree.items():
            key = key.replace(f"/{self._serial.upper()}/", "")
            hirarchy = key.split("/") #join_enumeration(key.split("/"))
            dictify(self.nodetree_dict, hirarchy, value)
    
    def __add_submodules_recursively(self, parent, treedict: dict):
        """
        Recursively add submodules (ZINodes) for each node in the ZI node tree.
        At the leaves create a parameter. Create a ChannelList as submodules
        whenever a node is enumerated, e.g. 'dev8030/sigouts/*/on'.
        
        Arguments:
            parent   -- parent QCoDeS object, either Instrument(-Channel) or ZINode
            treedict -- dictionary specifying the (sub-)tree of the ZI node hirarchy
        """
        for key, value in treedict.items():
            if all(isinstance(k, int) for k in value.keys()):
                # if enumerated node
                if "Node" in value[0].keys():
                    # if at leave, don't create ChannelList     
                    for k in value.keys(): 
                        self.__add_parameter_from_dict(parent, f"{key}{k}", value[k])
                else:
                    # else, create ChannelList
                    channel_list = ChannelList(parent, key, ZINode)
                    for k in value.keys():
                        ch_name = f"{key}{k}"
                        ch = ZINode(parent, ch_name)
                        channel_list.append(ch)
                        # parent.add_submodule(ch_name, ch)
                        self.__add_submodules_recursively(ch, treedict[key][k])
                    channel_list.lock()
                    parent.add_submodule(key, channel_list)
            else:
                # if not enumerated node
                if "Node" in value.keys():
                    # if at leave create parameter
                    self.__add_parameter_from_dict(parent, key, value)
                else:
                    # if not at leave, create node
                    module = ZINode(parent, key)
                    parent.add_submodule(key, module)
                    self.__add_submodules_recursively(module, treedict[key])
            

    def __add_parameter_from_dict(self, instr, name, params):
        """
        Add a QCoDeS parameter associated to a ZI noe from a dict describing 
        the parameter with e.g. 'Node', 'Properties', 'Description', 'Options' etc.
        
        Arguments:
            instr  -- instrument/submodule the parameter is associated with
            name   -- parameter name
            params -- dictionary describing the parameter, innermost layer of nodetree_dict
        """
        node = params["Node"].lower().replace(f"/{self._serial}/" ,"")
        if "Read" in params["Properties"]:
            getter = partial(
                self._controller.get,
                self._dev,
                node             
            )
        else:
            getter = None
        if "Write" in params["Properties"]:
            setter = partial(
                self._controller.set,
                self._dev,
                node             
            )
        else:
            setter = None
        instr.add_parameter(
            name=name,
            docstring=dict_to_doc(params),
            unit=params["Unit"] if params["Unit"] != "None" else None,
            get_cmd=getter,
            set_cmd=setter
        )
    
    def __repr__(self):
        s = super().__repr__()
        s += f"\n     submodules: \n"
        for m in self.submodules.keys():
            s += f"         * {m}\n"
        s += f"     parameters: \n"
        for p in self.parameters.keys():
            s += f"         * {p}\n"  
        return s

    def get_idn(self):
        return dict(
            vendor="Zurich Instruments",
            model=self._type.upper(),
            serial=self._serial,
            firmware=self._controller.get(self._dev, "system/fwrevision")
        )
        


        

"""
Helper functions used to process the nodetree dictionary in ZIBaseInstrument.
"""
def dictify(data, keys, val):
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

def join_enumeration(lst):
    for i, l in enumerate(lst):
        if any([str(j) in l for j in range(10)]):
            lst[i-1:i+1] = ["".join(lst[i-1:i+1])]
    return lst

def dict_to_doc(d):
    s = ""
    for k, v in d.items():
        s += f"* {k}:\n\t{v}\n\n"
    return s