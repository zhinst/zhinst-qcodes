from .base import ZIBaseInstrument
from .uhfqa import AWG
from qcodes.instrument.channel import InstrumentChannel

import zhinst.toolkit as tk
from zhinst.toolkit.control.drivers.uhfli import DAQModule, SweeperModule


class DAQ(InstrumentChannel):
    """
    Data Acquisition Module for UHFLI. Inherits from InstrumentChanne and wraps 
    around a UHFLI DAQModule from zhinst-toolkit.

    Arguments:
        name (str): name of the submodule
        parent_instr: qcodes parent instrument of InstrumentChannel
        parent_contr: zhinst-toolkit device of the parent isntrument, used for 
            get and set

    Properties:
        signals (list)
        results (dict)

    """

    def __init__(self, name, parent_instr, parent_contr):
        super().__init__(parent_instr, name)
        self._daq_module = DAQModule(parent_contr)
        self._daq_module._setup()
        for k, param in self._daq_module.__dict__.items():
            if not k.startswith("_"):
                val_mapping = None
                if param._map:
                    # invert the value map in case there is one
                    val_mapping = dict(map(reversed, param._map.items()))
                    param._map = None
                self.add_parameter(
                    k,
                    get_cmd=param,
                    set_cmd=param,
                    docstring=param._description,
                    unit=param._unit,
                    val_mapping=val_mapping,
                )

    def trigger(self, *args):
        """
        Set the trigger signal of the DAQ module. Specified by the trigger 
        source (e.g. 'demod1') and the type (e.g. 'trigin1').
        
        Arguments:
            trigger_source (str)
            trigger_type (str)

        """
        self._daq_module.trigger(*args)

    def signals_add(
        self,
        signal_source,
        signal_type="",
        operation="avg",
        fft=False,
        complex_selector="abs",
    ):
        """
        Add a singal to measure with the DAQ module. The specified signal is added 
        to the property 'signals' list. On 'measure()' the DAQ module subscribes to
        all the signal nodes in the list. 
        
        Arguments:
            signal_source (str): specifies the signal source, e.g. 'demod1'
            signal_type (str): specifies the type of the signal, e.g. "x" or "r"
            operation (str): the operation performed on the signal, e.g. "avg" 
                or "std" (default: "avg")
            fft (bool): selects the fourier transform of the signal (default: False)
            complex_selector (str): only used with FFT, selects the operation on the 
                complex value, e.g. "abs" or "real" (default: {"abs"})
        
        Returns:
            a string with the exact signal node, to be used as a key in the 
            results dictionary, e.g.
                
                > signal = uhfli.daq.signal_add("demod1", "r")
                > uhfli.daq.measure()
                > result = uhfli.daq.results[signal]

        """
        return self._daq_module.signals_add(
            signal_source, signal_type, operation, fft, complex_selector
        )

    def signals_list(self):
        """
        Returns a list of the available signals.
        
        """
        return self._daq_module.signals_list()

    def signals_clear(self):
        """
        Clears the signals list.

        """
        self._daq_module.signals_clear()

    def measure(self, verbose=True, timeout=20):
        """
        Performs a measurement and stores the result in 'daq.results'. This 
        method subscribes to all the paths previously added to 'daq.signals', 
        then starts the measurement, waits until the measurement in finished 
        and eventually reads the result. 
        
        Keyword Arguments:
            verbose (bool): flag to select a verbose print output (default: True)
            timeout (int): a maximum time after which the measurement stops (default: 20)

        """
        self._daq_module.measure(verbose, timeout)

    def _set(self, *args):
        """
        Sets a given node of the module to a given value.

        """
        self._daq_module._set(*args)

    def _get(self, *args, valueonly=True):
        """
        Gets the value of a given node of the module.
        
        """
        return self._daq_module._get(*args)

    @property
    def signals(self):
        return self._daq_module.signals

    @property
    def results(self):
        return self._daq_module.results


class Sweeper(InstrumentChannel):
    """
    Sweeper module for UHFLI. Inherits from InstrumentChannel and wraps around 
    a UHFLI SweeperModule from zhinst-toolkit.

    Arguments:
        name (str): name of the submodule
        parent_instr: qcodes parent instrument of InstrumentChannel
        parent_contr: zhinst-toolkit device of the parent isntrument, used for 
            get and set
    
    Properties:
        signals (list)
        results (dict)
    
    """

    def __init__(self, name, parent_instr, parent_contr):
        super().__init__(parent_instr, name)
        self._sweeper_module = SweeperModule(parent_contr)
        self._sweeper_module._setup()
        for k, param in self._sweeper_module.__dict__.items():
            if not k.startswith("_"):
                val_mapping = None
                if param._map:
                    val_mapping = dict(map(reversed, param._map.items()))
                    param._map = None
                self.add_parameter(
                    k,
                    get_cmd=param,
                    set_cmd=param,
                    docstring=param._description,
                    unit=param._unit,
                    val_mapping=val_mapping,
                )

    def signals_add(self, signal_source):
        """
        Add a singal to measure with the DAQ module. The specified signal is added 
        to the property 'signals' list. On 'measure()' the DAQ module subscribes to
        all the signal nodes in the list. In contrast to the DAQ module, the 
        sweeper records all data from the given node.
        
        Arguments:
            signal_source (str): specifies the signal source, e.g. 'demod1'
        
        Returns:
            a string with the exact signal node, to be used as a key in the 
            results dictionary, e.g.
                
                > signal = uhfli.sweeper.signal_add("demod1")
                > uhfli.sweeper.measure()
                > result = uhfli.sweeper.results[signal]

        """
        return self._sweeper_module.signals_add(signal_source)

    def signals_clear(self):
        """
        Clears the signals list.

        """
        self._sweeper_module.signals_clear()

    def signals_list(self):
        """
        Returns a list of the available signals.
        
        """
        return self._sweeper_module.signals_list()

    def sweep_parameter_list(self):
        """
        Lists available parameters that support sweeping.

        """
        return self._sweeper_module.sweep_parameter_list()

    def sweep_parameter(self, param):
        """
        Selects a parameter to sweep. The parameter is specified as a string 
        that has to match the avaliable parameters that support sweeping. See 
        available parameters with 'sweeper.sweep_parameter_list()'.
        
        Arguments:
            param (str)

        """
        self._sweeper_module.sweep_parameter(param)

    def measure(self, verbose=True, timeout=20):
        """
        Performs a measurement and stores the result in 'sweeper.results'. This 
        method subscribes to all the paths previously added to 'daq.signals', 
        then starts the measurement, waits until the measurement in finished 
        and eventually reads the result. 
        
        Keyword Arguments:
            verbose (bool): flag to select a verbose print output (default: True)
            timeout (int): a maximum time after which the measurement stops (default: 20)

        """
        self._sweeper_module.measure(verbose, timeout)

    def application(self, application):
        """
        Selects an application specific preset.
        
        Arguments:
            application (str)

        """
        self._sweeper_module.application(application)

    def _set(self, *args):
        """
        Sets a given node of the module to a given value.

        """
        self._sweeper_module._set(*args)

    def _get(self, *args, valueonly=True):
        """
        Gets the value of a given node of the module.
        
        """
        return self._sweeper_module._get(*args)

    @property
    def signals(self):
        return self._sweeper_module.signals

    @property
    def results(self):
        return self._sweeper_module.results


class UHFLI(ZIBaseInstrument):
    """
    QCoDeS driver for ZI UHFLI.

    Inherits from ZIBaseInstrument. Initializes submodules 
    from the nodetree and a DAQ and Sweeper submodule. If the AWG option is 
    installed it will also have an AWG submodule.

    Arguments:
        name (str): The internal QCoDeS name of the instrument
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
        serial: str,
        interface="1gbe",
        host="localhost",
        port=8004,
        api=6,
        **kwargs,
    ) -> None:
        super().__init__(name, "uhfli", serial, interface, host, port, api, **kwargs)
        submodules = self.nodetree_dict.keys()
        # initialize submodules from nodetree with blacklist
        blacklist = [
            "awgs",
            "scopes",
        ]
        [self._init_submodule(key) for key in submodules if key not in blacklist]

    def _connect(self):
        """
        Instantiate the device controller from zhinst-toolkit, set up the data 
        server and connect the device the data server. This method is called 
        from __init__ of the base instruemnt class.
        
        """
        self._controller = tk.UHFLI(
            self._name, self._serial, interface=self._interface, host=self._host
        )
        self._controller.setup()
        self._controller.connect_device(nodetree=False)
        self.connect_message()
        self._get_nodetree_dict()
        # initialize AWG, DAQ and Sweeper submodules
        if "AWG" in self._controller.options:
            self.add_submodule("awg", AWG("awg", self, self._controller))
        self.add_submodule("daq", DAQ("daq", self, self._controller))
        self.add_submodule("sweeper", Sweeper("sweeper", self, self._controller))
