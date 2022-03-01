"""Connection Manager for the ziPython API"""
from collections.abc import MutableMapping
import typing as t

from zhinst.toolkit.session import Devices as TKDevices
from zhinst.toolkit.session import PollFlags
from zhinst.toolkit.session import Session as TKSession
from zhinst.toolkit.session import ModuleHandler as TKModuleHandler
from zhinst.toolkit.nodetree.helper import lazy_property
from zhinst.ziPython import ziDAQServer

import zhinst.qcodes.driver.devices as ZIDevices
import zhinst.qcodes.driver.modules as ZIModules
from zhinst.qcodes.qcodes_adaptions import (
    init_nodetree,
    tk_node_to_parameter,
    ZIParameter,
    ZIInstrument,
)


class Devices(MutableMapping):
    """Mapping class for the connected devices.

    Mapps the connected devices from data server to lazy device objects.
    On every access the connected devices are read from the data server. This
    ensures that even if devices get connected/disconnected through another
    session the list will be up to date.

    Args:
        session: active session to the data server.
        tk_devices: toolkit devices object.
    """

    def __init__(self, session: "Session", tk_devices: TKDevices):
        self._tk_devices = tk_devices
        self._session = session
        self._devices = {}
        self._default_properties = {}

    def __getitem__(self, key) -> ZIDevices.DeviceType:
        key = key.lower()
        if key in self.connected():
            if key not in self._devices:
                tk_device = self._tk_devices[key]
                name, raw = self._default_properties.get(key, (None, False))
                self._devices[key] = ZIDevices.DEVICE_CLASS_BY_MODEL.get(
                    tk_device.__class__.__name__, ZIDevices.ZIBaseInstrument
                )(tk_device, self._session, name=name, raw=raw)
            return self._devices[key]
        raise KeyError(key)

    def __setitem__(self, *_):
        raise LookupError(
            "Illegal operation. Devices must be connected through the session."
        )

    def __delitem__(self, key):
        self._devices.pop(key, None)

    def __iter__(self):
        return iter(self.connected())

    def __len__(self):
        return len(self.connected())

    def update_device_properties(self, serial: str, name: str, raw: bool) -> None:
        """ """
        if serial in self._devices:
            raise RuntimeError(
                f"The Qcodes Instance of {serial} already exists.\n"
                "The device properties can therfor no longer be changed"
            )
        self._default_properties[serial.lower()] = (name, raw)

    def connected(self) -> t.List[str]:
        """Get a list of devices connected to the data server.

        Returns:
            list[str]: List of all connected devices.
        """
        return self._tk_devices.connected()

    def visible(self) -> t.List[str]:
        """Get a list of devices visible to the data server.

        Returns:
            list[str]: List of all connected devices.
        """
        return self._tk_devices.visible()


class ModuleHandler:
    def __init__(self, session: "Session", tk_modules: TKModuleHandler):
        self._session = session
        self._tk_modules = tk_modules

    def create_awg_module(self) -> ZIModules.ZIBaseModule:
        """Create a QCodes instance of the AWGModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `awg_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_awg_module()
        return ZIModules.ZIBaseModule(module, self._session, name="awgmodule")

    def create_daq_module(self) -> ZIModules.ZIBaseModule:
        """Create a QCodes instance of the DAQModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `awg_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_daq_module()
        return ZIModules.ZIBaseModule(module, self._session, name="daqmodule")

    def create_device_settings_module(self) -> ZIModules.ZIBaseModule:
        """Create a QCodes instance of the DeviceSettingsModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `awg_module`.

        Returns:
            DeviceSettingsModule: created module
        """
        module = self._tk_modules.create_device_settings_module()
        return ZIModules.ZIBaseModule(
            module, self._session, name="devicesettingsmodule"
        )

    def create_impedance_module(self) -> ZIModules.ZIBaseModule:
        """Create a QCodes instance of the ImpedanceModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `impedance_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_device_settings_module()
        return ZIModules.ZIBaseModule(module, self._session, name="impedancemodule")

    def create_mds_module(self) -> ZIModules.ZIBaseModule:
        """Create a QCodes instance of the PIDAdvisorModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `multi_device_sync_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_mds_module()
        return ZIModules.ZIBaseModule(module, self._session, name="mdsmodule")

    def create_pid_advisor_module(self) -> ZIModules.ZIBaseModule:
        """Create a QCodes instance of the PIDAdvisorModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `pid_advisor_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_pid_advisor_module()
        return ZIModules.ZIBaseModule(module, self._session, name="pidadvisormodule")

    def create_precompensation_advisor_module(self) -> ZIModules.ZIBaseModule:
        """Create a QCodes instance of the PrecompensationAdvisorModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `precompensation_advisor_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_precompensation_advisor_module()
        return ZIModules.ZIBaseModule(
            module, self._session, name="precompensationadvisormodule"
        )

    def create_qa_module(self) -> ZIModules.ZIBaseModule:
        """Create a QCodes instance of the AwgModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `qa_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_qa_module()
        return ZIModules.ZIBaseModule(module, self._session, name="qamodule")

    def create_scope_module(self) -> ZIModules.ZIBaseModule:
        """Create a QCodes instance of the AwgModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `scope_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_scope_module()
        return ZIModules.ZIBaseModule(module, self._session, name="scopemodule")

    def create_sweeper_module(self) -> ZIModules.ZISweeperModule:
        """Create a QCodes instance of the SweeperModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `sweeper_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_sweeper_module()
        return ZIModules.ZISweeperModule(module, self._session)

    def create_shfqa_sweeper(self) -> ZIModules.ZISHFQASweeper:
        """Create an instance of the SHFQASweeper.

        For now the general sweeper module does not support the SHFQA. However a
        python based implementation called ``SHFSweeper`` does already provide
        this functionality. The ``SHFSweeper`` is part of the ``zhinst`` module
        and can be found in the utils.

        Toolkit wraps around the ``SHFSweeper`` and exposes a interface that is
        similar to the LabOne modules, meaning the parameters are exposed in a
        node tree like structure.

        In addition a new session is created. This has the benefit that the
        sweeper implementation does not interfer with the the commands and
        setups from the user.

        Returns:
            created object
        """
        module = self._tk_modules.create_shfqa_sweeper()
        return ZIModules.ZISHFQASweeper(module, self._session)

    @lazy_property
    def awg(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the ziPython.AwgModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        ressources.
        """
        return self.create_awg_module()

    @lazy_property
    def daq(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the ziPython.DataAcquisitionModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        ressources.
        """
        return self.create_daq_module()

    @lazy_property
    def device_settings(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the ziPython.DeviceSettingsModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        ressources.
        """
        return self.create_device_settings_module()

    @lazy_property
    def impedance(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the ziPython.ImpedanceModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        ressources.
        """
        return self.create_impedance_module()

    @lazy_property
    def mds(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the ziPython.MultiDeviceSyncModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        ressources.
        """
        return self.create_mds_module()

    @lazy_property
    def pid_advisor(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the ziPython.PidAdvisorModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        ressources.
        """
        return self.create_pid_advisor_module()

    @lazy_property
    def precompensation_advisor(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the ziPython.PrecompensationAdvisorModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        ressources.
        """
        return self.create_precompensation_advisor_module()

    @lazy_property
    def qa(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the ziPython.QuantumAnalyzerModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        ressources.
        """
        return self.create_qa_module()

    @lazy_property
    def scope(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the ziPython.ScopeModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        ressources.
        """
        return self.create_scope_module()

    @lazy_property
    def sweeper(self) -> ZIModules.ZISweeperModule:
        """Managed instance of the ziPython.SweeperModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        ressources.
        """
        return self.create_sweeper_module()

    @lazy_property
    def shfqa_sweeper(self) -> ZIModules.ZISHFQASweeper:
        """Managed instance of the ziPython.SweeperModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        ressources.
        """
        return self.create_shfqa_sweeper()


class ZISession:
    """Session to a data server.

    Zurich Instruments devices use a server-based connectivity methodology.
    Server-based means that all communication between the user and the
    instrument takes place via a computer program called a server, the data
    sever. The data sever recognizes available instruments and manages all
    communication between the instrument and the host computer on one side, and
    communication to all the connected clients on the other side. (For more
    information on the architecture please refer to the user manual
    http://docs.zhinst.com/labone_programming_manual/introduction.html)

    The entry point into any connection is therfor a client session to a
    existing data sever. This class represents a single client session to a
    data server. The session enables the user to connect to one or multiple
    instruments (also creates the deticated objects for each device), access
    the LabOne modules and poll data.

    Since QCoDeS normally instanciate the device specific objects directly
    this driver also exposes helper classes for that directly. These helper
    classes create a session and connect the specified device to it. To avoid
    that each device has a own session by default ``ZISession`` only creates one
    session to a single data server and reuses that.

    Info:
        Except for the HF2 a single session can be used to connect to all
        devices from Zurich Instruments. Since the HF2 is historically based on
        another data server called the hf2 data server it is not possible to
        connect HF2 devices a "normal" data server and also not possible to
        connect devices apart from HF2 to the hf2 data server.

    Args:
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port 8004 (8005 for HF2 if specified).
            (default = None)
        hf2: Flag if the session should be established with an HF2 data sever or
            the "normal" one for all other devices. If not specified the session
            will detect the type of the data server based on the port.
            (default = None)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the Flag will create a new session.

            Warning:

                Creating a new session should be done cearfully since it
                requires more ressources and can create unwanted side effects.

        connection: Existing daq server object. If specified the session will
            not create a new session to the data server but reuse the passed
            one. (default = None)
    """

    def __new__(
        cls,
        server_host: str,
        server_port: int = None,
        *,
        hf2: bool = None,
        new_session=False,
        connection: ziDAQServer = None,
    ):
        if not new_session:
            for instance in Session.instances():
                if instance.server_host == server_host and (
                    instance.is_hf2_server == hf2
                    or server_port is None
                    or instance.server_port == server_port
                ):
                    return instance
        return Session(server_host, server_port, hf2=hf2, connection=connection)


class Session(ZIInstrument):
    """Session to a data server.

    Zurich Instruments devices use a server-based connectivity methodology.
    Server-based means that all communication between the user and the
    instrument takes place via a computer program called a server, the data
    sever. The data sever recognizes available instruments and manages all
    communication between the instrument and the host computer on one side, and
    communication to all the connected clients on the other side. (For more
    information on the architecture please refer to the user manual
    http://docs.zhinst.com/labone_programming_manual/introduction.html)

    The entry point into for any connection is therfor a client session to a
    existing data sever. This class represents a single client session to a
    data server. The session enables the user to connect to one or multiple
    instruments (also creates the deticated objects for each device), access
    the LabOne modules and poll data. In short it is the only object the user
    need to create by himself.

    Info:
        Except for the HF2 a single session can be used to connect to all
        devices from Zurich Instruments. Since the HF2 is historically based on
        another data server called the hf2 data server it is not possible to
        connect HF2 devices a "normal" data server and also not possible to
        connect devices apart from HF2 to the hf2 data server.

    Args:
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port 8004 (8005 for HF2 if specified).
            (default = None)
        hf2: Flag if the session should be established with an HF2 data sever or
            the "normal" one for all other devices. If not specified the session
            will detect the type of the data server based on the port.
            (default = None)
        connection: Existing daq server object. If specified the session will
            not create a new session to the data server but reuse the passed
            one. (default = None)
    """

    def __init__(
        self,
        server_host: str,
        server_port: int = None,
        *,
        hf2: bool = None,
        connection: ziDAQServer = None,
    ):
        self._tk_object = TKSession(
            server_host, server_port, connection=connection, hf2=hf2
        )
        super().__init__(f"zi_session_{len(self.instances())}", self._tk_object.root)
        self._devices = Devices(self, self._tk_object.devices)
        self._modules = ModuleHandler(self, self._tk_object.modules)
        init_nodetree(self, self._tk_object.root, self._snapshot_cache)

    def connect_device(
        self, serial: str, *, interface: str = None, name: str = None, raw: bool = None
    ) -> ZIDevices.DeviceType:
        """Establish a connection to a device.

        Info:
            It is allowed to call this function for an already connected device.
            In that case the function simply returns the device object of the
            already connected device.

        Args:
            serial: Serial number of the device, e.g. *'dev12000'*.
                The serial number can be found on the back panel of the
                instrument.
            interface: Device interface (e.g. = "1GbE"). If not specified
                the default interface from the discover is used.
            name: Name of the instrument in qcodes.
                (default = "zi_{dev_type}_{serial}")
            raw: Flag if qcodes instance should only created with the nodes and
                not forwarding the toolkit functions. (default = False)

        Returns:
            Device object
        """
        if name or raw is not None:
            self._devices.update_device_properties(serial, name, raw)
        self._tk_object.connect_device(serial, interface=interface)
        return self._devices[serial]

    def disconnect_device(self, serial: str) -> None:
        """Disconnect a device.

        Warning:
            This function will return immediately. The disconnection of the
            device may not yet finished.

        Args:
            serial (str): Serial number of the device, e.g. *'dev12000'*.
                The serial number can be found on the back panel of the instrument.
        """
        self._devices.pop(serial, None)
        self._tk_object.disconnect_device(serial)

    def sync(self) -> None:
        """Synchronize all connected devices.

        Synchronization in this case means creating a defined state.

        The following steps are performed:
            * Ensures that all set commands have been flushed to the device
            * Ensures that get and poll commands only return data which was
              recorded after the sync command. (ALL poll buffers are cleared!)
            * Blocks until all devices have cleared their bussy flag.

        Warning:
            The sync is performed for all devices connected to the daq server

        Warning:
            This command is a blocking command that can take a substential
            amount of time.

        Raises:
            RuntimeError: ZIAPIServerException: Timeout during sync of device
        """
        self._tk_object.sync()

    def poll(
        self,
        recording_time: float = 0.1,
        timeout: float = 0.5,
        flags: PollFlags = PollFlags.DEFAULT,
    ) -> t.Dict[ZIParameter, t.Dict[str, t.Any]]:
        """Polls all subsribed data

        Poll the value changes in all subscribed nodes since either subscribing
        or the last poll (assuming no buffer overflow has occurred on the Data
        Server).

        Args:
            recording_time: defines the duration of the poll. (Note that not
                only the newly recorder values are polled but all vaules since
                either subscribing or the last pill). Needs to be larger than
                zero. (default = 0.1)
            timeout: Adds an additional timeout in seconds on top of
                `recording_time`. Only relevant when communicating in a slow
                network. In this case it may be set to a value larger than the
                expected round-trip time in the network. (default = 0.5)
            flags: Flags for the polling (see :class `PollFlags`:)

        Returns:
            Polled data in a dictionary. The key is a `Node` object and the
            value is a dictionary with the raw data from the device
        """
        polled_data_tk = self._tk_object.poll(
            recording_time=recording_time, timeout=timeout, flags=flags
        )
        polled_data = {}
        for tk_node, data in polled_data_tk.items():
            device = self.devices[tk_node.root.prefix_hide]
            parameter = tk_node_to_parameter(device, tk_node)
            polled_data[parameter] = data
        return polled_data

    @property
    def devices(self) -> Devices:
        """Mapping for the connected devices."""
        return self._devices

    @property
    def modules(self) -> ModuleHandler:
        """LabOne modules"""
        return self._modules

    @property
    def is_hf2_server(self) -> bool:
        """Flag if the data server is a HF2 Data Server"""
        return self._tk_object.is_hf2_server

    @property
    def daq_server(self) -> ziDAQServer:
        """Managed instance of the zi.ziDAQServer."""
        return self._tk_object.daq_server

    @property
    def server_host(self) -> str:
        """Server host"""
        return self._tk_object.server_host

    @property
    def server_port(self) -> int:
        """Server port"""
        return self._tk_object.server_port
