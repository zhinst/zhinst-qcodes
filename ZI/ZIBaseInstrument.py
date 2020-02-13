from ziDrivers import Controller
from functools import partial


from qcodes.instrument.base import Instrument
from qcodes.instrument.channel import InstrumentChannel, ChannelList
from qcodes.utils import validators as validators



#######################
# some helper functions
#######################
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


#######################
# ZINode Class 
#######################
class ZINode(InstrumentChannel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

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


#######################
# ZIAWG Class 
#######################
class ZIAWG(InstrumentChannel):
    def __init__(self, parent, index, **kwargs) -> None: 
        self.index = index
        self._controller = parent._controller
        self._dev = parent._dev
        name = f"awg{index}"
        super().__init__(parent, name, **kwargs)

    def __repr__(self):
        params = self.sequence_params["sequence_parameters"]
        s = f"ZIAWG: {self.name}\n"
        s += f"    parent  : {self._parent}\n"
        s += f"    index   : {self.index}\n"
        s += f"    sequence: \n"
        s += f"           type: {self.sequence_params['sequence_type']}\n"
        for i in params.items():
            s += f"            {i}\n"
        return s
    
    def print_readable_snapshot(self, update: bool = False, max_chars: int = 80) -> None:
        print(f"{self}")
    
    def run(self):
        self._controller.awg_run(self._dev, self.index)

    def stop(self):
        self._controller.awg_stop(self._dev, self.index)

    def compile(self):
        self._controller.awg_compile(self._dev, self.index)
    
    def reset_queue(self):
        self._controller.awg_reset_queue(self._dev, self.index)

    def queue_waveform(self, wave1, wave2):
        self._controller.awg_queue_waveform(
            self._dev,
            self.index,
            data=(wave1, wave2)
        )

    def replace_waveform(self, wave1, wave2, i=0):
        self._controller.awg_replace_waveform(
            self._dev,
            self.index,
            data=(wave1, wave2),
            index=i
        )

    def upload_waveforms(self):
        self._controller.awg_upload_waveforms(
            self._dev,
            self.index
        )

    def compile_and_upload_waveforms(self):
        self._controller.awg_compile_and_upload_waveforms(
            self._dev,
            self.index
        )

    def set_sequence_params(self, **kwargs):
        self._controller.awg_set_sequence_params(
            self._dev,
            self.index,
            **kwargs
        )
    
    @property
    def is_running(self):
        return self._controller.awg_is_running(
            self._dev, 
            self.index
        )

    @property
    def sequence_params(self):
        return self._controller.awg_list_params(
            self._dev,
            self.index
        )

    




#######################
# ZIBaseInstrument class
#######################
class ZIBaseInstrument(Instrument):

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
        self.__get_nodetree_dict()

    def __get_nodetree_dict(self):
        tree = self._controller.get_nodetree(f"{self._serial}/*")
        self.nodetree_dict = dict()
        for key, value in tree.items():
            key = key.replace(f"/{self._serial.upper()}/", "")
            hirarchy = key.split("/") #join_enumeration(key.split("/"))
            dictify(self.nodetree_dict, hirarchy, value)
    
    def __add_submodules_recursively(self, parent, treedict: dict):
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
    
    def init_submodule(self, key):
        if key in self.nodetree_dict.keys():
            self.__add_submodules_recursively(self, {key: self.nodetree_dict[key]})
        else:
            print(f"Key {key} not in nodetree: {list(self.nodetree_dict.keys())}")


        
