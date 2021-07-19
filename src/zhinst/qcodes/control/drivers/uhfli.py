from .base import ZIBaseInstrument
from .uhfqa import AWG
from qcodes.instrument.channel import InstrumentChannel

import zhinst.toolkit as tk
from zhinst.toolkit.control.drivers.uhfli import DAQModule, SweeperModule
from typing import List, Dict


class DAQ(InstrumentChannel):
    """*Data Acquisition Module* for the *UHFLI* driver.

    Inherits from :class:`InstrumentChannel` and wraps around the
    :class:`DAQModule` class of a from the :mod:`zhinst-toolkit`.

    Arguments:
        name (str): The name of the `DAQ` submodule.
        parent_instr (:class:`qcodes.instrument.base.Instrument`): The QCoDeS
            parent instrument of the `InstrumentChannel`.
        parent_contr (:class:`zhinst.toolkit.BaseInstrument`): The `_controller`
            of the parent instrument that is used for getting and setting
            parameters.

    Attributes:
        signals (list): A list of node strings of signals that are added to the
            measurement and will be subscribed to before data acquisition.
        results (dict): A dictionary with signal strings as keys and
            :class:`zhinst.toolkit.control.drivers.base.daq.DAQResult` objects
            as values that hold all the data of the measurement result.

    """

    def __init__(self, name: str, parent_instr, parent_contr) -> None:
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

    def trigger(self, trigger_source: str, trigger_type: str) -> None:
        """Sets the trigger signal of the *DAQ Module*.

        This method can be used to specify the signal used to trigger the data
        acquisition. Use the method `trigger_list()` to see the available
        trigger signal sources and types.The trigger node can also be set
        directly using the module Parameter `triggernode`.

        Arguments:
            trigger_source (str): A string that specifies the source of the
                trigger signal, e.g. "demod0".
            trigger_trype (str): A string that specifies the type of the
                trigger signal, e.g. "trigin1".

        """
        self._daq_module.trigger(trigger_source, trigger_type)

    def trigger_list(self, source=None) -> List:
        """Returns a list of all the available signal sources for data acquisition.

        Keyword Arguments:
            source (str): specifies the signal source to return signal types
                (default: None)

        Returns:
            Returns all available signal sources by default. If the keyword is
            specified with one of the signal sources, all the available signal
            types for the signal source are returned.

        """
        return self._daq_module.trigger_list(source)

    def signals_add(
        self,
        signal_source: str,
        signal_type: str = "",
        operation: str = "avg",
        fft: bool = False,
        complex_selector: str = "abs",
    ) -> str:
        """Add a signal to the signals list to be subscribed to during measurement.

        The specified signal is added to the property *signals* list. On
        `measure()`, the *DAQ Module* subscribes to all the signal nodes in the
        list.

        Arguments:
            signal_source (str): The source of the signal, e.g. 'demod0'. See
                `signals_list()` for available signals.

        Keyword Arguments:
            signal_type (str): The type of the signal. Depends on the given
                source, e.g. for demod signals the types'X', 'Y', 'R', 'Theta',
                ... are available. See `signals_list({signal source})` for
                available signal types. (default: "")
            operation (str): The operation that is performed on the acquired
                signal, e.g. the average of data points ('avg'), the standard
                deviation of the signal ('std') or single points ('replace').
                (default: "avg")
            fft (bool): A flag to enable the fourier transform (FFT) of the
                acquired signal.  (default: False)
            complex_selector (str):  If the FFT is enabled, this selects the
                complex value of the result, e.g. 'abs', 'phase', 'real',
                'imag'. (default: "abs")

        Returns:
            A string with the exact node that will be subscribed to. Can be used
            as a key in the 'results' dict to retrieve the measurement result
            corresponding to this signal, e.g.

                >>> signal = uhfli.daq.signal_add("demod0", "r")
                /dev3337/demods/0/sample.r.avg
                >>> uhfli.daq.measure()
                >>> ...
                >>> result = uhfli.daq.results[signal]

        """
        return self._daq_module.signals_add(
            signal_source, signal_type, operation, fft, complex_selector
        )

    def signals_list(self, source=None) -> List:
        """Returns a list of all the available signal sources for data acquisition.

        Keyword Arguments:
            source (str): specifies the signal source to return signal types
                (default: None)

        Returns:
            Returns all available signal sources by default. If the keyword is
            specified with one of the signal sources, all the available signal
            types for the signal source are returned.

        """
        return self._daq_module.signals_list(source=source)

    def signals_clear(self) -> None:
        """Resets the `signal` list attribute to an empty list."""
        self._daq_module.signals_clear()

    def measure(self, verbose: bool = True, timeout: float = 20) -> None:
        """Performs the measurement.

        Starts a measurement and stores the result in `daq.results`. This
        method subscribes to all the paths previously added to `daq.signals`,
        then starts the measurement, waits until the measurement in finished
        and eventually reads the result.

        Keyword Arguments:
            verbose (bool): A flag to enable or disable console output during
                the measurement. (default: True)
            timeout (int): The measurement will be stopped after the timeout.
                The valiue is given in seconds. (default: 20)

        """
        self._daq_module.measure(verbose, timeout)

    def _set(self, *args) -> None:
        """Sets a given node of the module to a given value."""
        self._daq_module._set(*args)

    def _get(self, *args, valueonly: bool = True):
        """Gets the value of a given node of the module."""
        return self._daq_module._get(*args)

    @property
    def signals(self):
        return self._daq_module.signals

    @property
    def results(self):
        return self._daq_module.results


class Sweeper(InstrumentChannel):
    """*Sweeper Module* for the *UHFLI* driver.

    Inherits from :class:`InstrumentChannel` and wraps around the
    :class:`SweeperModule` class of a from the :mod:`zhinst-toolkit`.

    Arguments:
        name (str): The name of the `Sweeper` submodule.
        parent_instr (:class:`qcodes.instrument.base.Instrument`): The QCoDeS
            parent instrument of the `InstrumentChannel`.
        parent_contr (:class:`zhinst.toolkit.BaseInstrument`): The `_controller`
            of the parent instrument that is used for getting and setting
            parameters.

    Attributes:
        signals (list): A list of node strings of signals that are added to the
            measurement and will be subscribed to before data acquisition.
        results (dict): A dictionary with signal strings as keys and
            :class:`zhinst.toolkit.control.drivers.base.sweeper.SweeperResult`
            objects as values that hold all the data of the measurement result.

    """

    def __init__(self, name: str, parent_instr, parent_contr) -> None:
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

    def signals_add(self, signal_source: str) -> str:
        """Adds a signal to the measurement.

        The according signal node path will be generated and added to the
        module's `signal` list attribute. The signal node will be subscribed to
        before measurement and the :class:`SweeperResult` for this signal will
        be added as an item in the `results` attribute after measurement.
        Available signal sources can be listed using `signals_list()`.

        Arguments:
            signal_source (str): A keyword string that specifies the source of
                the signal, e.g. "demod0".

        Returns:
            The exact node string that will be subscribed to, can be used as a
            key in the results dict to get the measurement result to this signal.

                >>> signal = uhfli.sweeper.signal_add("demod0")
                /dev3337/demods/0/sample.r.avg
                >>> uhfli.sweeper.measure()
                >>> ...
                >>> result = uhfli.sweeper.results[signal]

        """
        return self._sweeper_module.signals_add(signal_source)

    def signals_clear(self) -> None:
        """Resets the `signal` list attribute to an empty list."""
        self._sweeper_module.signals_clear()

    def signals_list(self) -> List:
        """Lists the keywords for available signals that can be added to the
        measurement.

        Returns:
            A list of the available signals.

        """
        return self._sweeper_module.signals_list()

    def sweep_parameter_list(self) -> List:
        """Lists the keywords for available parameters that can be swept during
        the measurement.

        Returns:
            A list with keywords of the available sweep parameters.

        """
        return self._sweeper_module.sweep_parameter_list()

    def sweep_parameter(self, param) -> None:
        """Sets the sweep parameter.

        The parameter to sweep should be given by a keyword string. The
        available parameters can be listed with `sweep_parameter_list()`.

        Arguments:
            param (str): The string corresponding to the parameter to sweep
                during measurement.

        """
        self._sweeper_module.sweep_parameter(param)

    def measure(self, verbose: bool = True, timeout: float = 20) -> None:
        """Performs the measurement.

        Starts a measurement and stores the result in `sweeper.results`. This
        method subscribes to all the paths previously added to
        `sweeper.signals`, then starts the measurement, waits until the
        measurement in finished and eventually reads the result.

        Keyword Arguments:
            verbose (bool): A flag to enable or disable output on the console.
                (default: True)
            timeout (int): The measurement will stopped after timeout. The value
                is given in seconds. (default: 20)

        """
        self._sweeper_module.measure(verbose, timeout)

    def application_list(self) -> List:
        """Lists the availbale application presets.

        Returns:
            A list of keywprd strings with the available applications.

        """
        self._sweeper_module.application_list()

    def application(self, application: str):
        """Sets one of the available application rpesets.

        The applications are defined in the :mod:`zhinst-toolkit`. They include
        `parameter_sweep`, `noise_amplitude_sweep`,
        `frequency_response_analyzer` and more.

        Arguments:
            application (str): The keyword for the application. See available
                applications with `application_list()`.

        """
        self._sweeper_module.application(application)

    def _set(self, *args) -> None:
        """Sets a given node of the module to a given value."""
        self._sweeper_module._set(*args)

    def _get(self, *args, valueonly: bool = True) -> None:
        """Gets the value of a given node of the module."""
        return self._sweeper_module._get(*args)

    @property
    def signals(self):
        return self._sweeper_module.signals

    @property
    def results(self):
        return self._sweeper_module.results


class UHFLI(ZIBaseInstrument):
    """QCoDeS driver for the *Zurich Instruments UHFLI*.

    Inherits from :class:`ZIBaseInstrument`. Initializes some *submodules*
    from the device's nodetree, a *Sweeper Module* `Sweeper` and a
    *Data Acquisition Module* `DAQ`.

    Arguments:
        name (str): The internal QCoDeS name of the instrument.
        serial (str): The device serial number, e.g. *'dev1234'*.

    Keyword Arguments:
        interface (str): The interface used to connect to the
            device. (default: '1gbe')
        host (str): Address of the data server. (default: 'localhost')
        port (int): Port used to connect to the data server. (default: 8004)
        api (int): Api level used for the data server. (default: 6)

    Attributes:
        daq (:class:`DAQ`): A UHFLI-specific *Data Acquisition Module*.
        sweeper (:class:`Sweeper`): A UHFLI-specific *Sweeper Module*.
        awg (:class:`zhinst.qcodes.uhfqa.AWG`): *AWG Core* for the *UHFLI*,
            taken from the *UHFQA*.

    """

    def __init__(
        self,
        name: str,
        serial: str,
        interface: str = "1gbe",
        host: str = "localhost",
        port: int = 8004,
        api: int = 6,
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

    def _connect(self) -> None:
        """Connects the device to the data server.

        Instantiates the device controller from :mod:`zhinst-toolkit`, sets up
        the data server and connects the device the data server. This method is
        called from `__init__` of the :class:`BaseInstrument` class.

        """
        self._controller = tk.UHFLI(
            self._name,
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
        # initialize AWG, DAQ and Sweeper submodules
        if "AWG" in self._controller.options:
            self.add_submodule("awg", AWG("awg", self, self._controller))
        self.add_submodule("daq", DAQ("daq", self, self._controller))
        self.add_submodule("sweeper", Sweeper("sweeper", self, self._controller))

    def factory_reset(self, sync=True) -> None:
        """Load the factory default settings.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after loading the factory preset (default: True).

        """
        self._controller.factory_reset(sync=sync)

    @property
    def allowed_sequences(self):
        return self._controller.allowed_sequences

    @property
    def allowed_trigger_modes(self):
        return self._controller.allowed_trigger_modes
