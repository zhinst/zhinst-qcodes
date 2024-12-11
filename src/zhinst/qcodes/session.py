"""Connection Manager for the LabOne Python API."""

from collections.abc import MutableMapping
from functools import cached_property
import typing as t

from zhinst.toolkit.session import Devices as TKDevices
from zhinst.toolkit.session import PollFlags
from zhinst.toolkit.session import Session as TKSession
from zhinst.toolkit.session import ModuleHandler as TKModuleHandler
from zhinst.core import ziDAQServer

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

    Maps the connected devices from data server to lazy device objects.
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
        self._devices: t.Dict[str, ZIDevices.DeviceType] = {}
        self._default_properties: t.Dict[
            str, t.Tuple[t.Optional[str], t.Optional[bool]]
        ] = {}

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

    def __setitem__(self, key: str, device: ZIDevices.DeviceType) -> None:
        if device.serial not in self.connected():
            raise LookupError(
                "Illegal operation. Devices must be connected through the session."
            )
        self._devices[key] = device

    def __delitem__(self, key):
        self._devices.pop(key, None)

    def __iter__(self):
        return iter(self.connected())

    def __len__(self):
        return len(self.connected())

    def update_device_properties(
        self, serial: str, name: t.Optional[str], raw: t.Optional[bool]
    ) -> None:
        """Update the properties for a device.

        The device options are used when the QCoDeS option of a new device
        is created.

        Args:
            serial: Serial of the device (e.g. dev1234)
            name: Optional name of the QCoDeS device object
            raw: Flag if qcodes instance should only created with the nodes and
                not forwarding the toolkit functions. (default = False)

        Raises:
            RuntimeError: If the device is already created
        """
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
    """Modules of LabOne.

    Handler for all additional so called modules by LabOne. A LabOne module is
    bound to a user session but creates a independent session to the Data Server.
    This has the advantage that they do not interfere with the user session. It
    also means that creating a session causes additional resources allocation,
    both at the client and the data server. New modules should therefore only be
    instantiated with care.

    Toolkit holds a lazy generated instance of all modules. This ensures that
    not more than one modules of each type gets created by accident and that the
    access to the modules is optimized.

    Of course there are many use cases where more than one module of a single
    type is required. This class therefore also exposes a ``create`` function for
    each LabOne module. These functions create a unmanaged instance of that
    module (unmanaged means toolkit does not hold an instance of that module).

    Args:
        session: Active user session
        tk_modules: Underlying toolkit module handler
    """

    def __init__(self, session: "Session", tk_modules: TKModuleHandler):
        self._session = session
        self._tk_modules = tk_modules

    def create_awg_module(self) -> ZIModules.ZIBaseModule:
        """Create a QCoDeS instance of the AWGModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `awg_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_awg_module()
        return ZIModules.ZIBaseModule(module, self._session, name="awg_module")

    def create_daq_module(self) -> ZIModules.ZIDAQModule:
        """Create a QCoDeS instance of the DAQModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `awg_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_daq_module()
        return ZIModules.ZIDAQModule(module, self._session)

    def create_device_settings_module(self) -> ZIModules.ZIDeviceSettingsModule:
        """Create a QCoDeS instance of the DeviceSettingsModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `awg_module`.

        Returns:
            DeviceSettingsModule: created module
        """
        module = self._tk_modules.create_device_settings_module()
        return ZIModules.ZIDeviceSettingsModule(module, self._session)

    def create_impedance_module(self) -> ZIModules.ZIImpedanceModule:
        """Create a QCoDeS instance of the ImpedanceModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `impedance_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_impedance_module()
        return ZIModules.ZIImpedanceModule(module, self._session)

    def create_mds_module(self) -> ZIModules.ZIBaseModule:
        """Create a QCoDeS instance of the PIDAdvisorModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `multi_device_sync_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_mds_module()
        return ZIModules.ZIBaseModule(module, self._session, name="mds_module")

    def create_pid_advisor_module(self) -> ZIModules.ZIPIDAdvisorModule:
        """Create a QCoDeS instance of the PIDAdvisorModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `pid_advisor_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_pid_advisor_module()
        return ZIModules.ZIPIDAdvisorModule(module, self._session)

    def create_precompensation_advisor_module(
        self,
    ) -> ZIModules.ZIPrecompensationAdvisorModule:
        """Create a QCoDeS instance of the PrecompensationAdvisorModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `precompensation_advisor_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_precompensation_advisor_module()
        return ZIModules.ZIPrecompensationAdvisorModule(module, self._session)

    def create_qa_module(self) -> ZIModules.ZIBaseModule:
        """Create a QCoDeS instance of the AwgModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `qa_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_qa_module()
        return ZIModules.ZIBaseModule(module, self._session, name="qa_module")

    def create_scope_module(self) -> ZIModules.ZIScopeModule:
        """Create a QCoDeS instance of the AwgModule.

        The new instance creates a new session to the DataServer.
        New instances should therefor be created carefully since they consume
        resources.

        The new module is not managed by toolkit. A managed instance is provided
        by the property `scope_module`.

        Returns:
            created module
        """
        module = self._tk_modules.create_scope_module()
        return ZIModules.ZIScopeModule(module, self._session)

    def create_sweeper_module(self) -> ZIModules.ZISweeperModule:
        """Create a QCoDeS instance of the SweeperModule.

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
        sweeper implementation does not interfere with the the commands and
        setups from the user.

        Returns:
            created object
        """
        module = self._tk_modules.create_shfqa_sweeper()
        return ZIModules.ZISHFQASweeper(module, self._session)

    @cached_property
    def awg(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the zhinst.core.AwgModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        resources.
        """
        return self.create_awg_module()

    @cached_property
    def daq(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the zhinst.core.DataAcquisitionModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        resources.
        """
        return self.create_daq_module()

    @cached_property
    def device_settings(self) -> ZIModules.ZIDeviceSettingsModule:
        """Managed instance of the zhinst.core.DeviceSettingsModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        resources.
        """
        return self.create_device_settings_module()

    @cached_property
    def impedance(self) -> ZIModules.ZIImpedanceModule:
        """Managed instance of the zhinst.core.ImpedanceModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        resources.
        """
        return self.create_impedance_module()

    @cached_property
    def mds(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the zhinst.core.MultiDeviceSyncModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        resources.
        """
        return self.create_mds_module()

    @cached_property
    def pid_advisor(self) -> ZIModules.ZIPIDAdvisorModule:
        """Managed instance of the zhinst.core.PidAdvisorModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        resources.
        """
        return self.create_pid_advisor_module()

    @cached_property
    def precompensation_advisor(self) -> ZIModules.ZIPrecompensationAdvisorModule:
        """Managed instance of the zhinst.core.PrecompensationAdvisorModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        resources.
        """
        return self.create_precompensation_advisor_module()

    @cached_property
    def qa(self) -> ZIModules.ZIBaseModule:
        """Managed instance of the zhinst.core.QuantumAnalyzerModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        resources.
        """
        return self.create_qa_module()

    @cached_property
    def scope(self) -> ZIModules.ZIScopeModule:
        """Managed instance of the zhinst.core.ScopeModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        resources.
        """
        return self.create_scope_module()

    @cached_property
    def sweeper(self) -> ZIModules.ZISweeperModule:
        """Managed instance of the zhinst.core.SweeperModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        resources.
        """
        return self.create_sweeper_module()

    @cached_property
    def shfqa_sweeper(self) -> ZIModules.ZISHFQASweeper:
        """Managed instance of the zhinst.core.SweeperModule.

        Managed in this sense means that only one instance is created
        and hold inside the connection Manager. This makes it easier to access
        the modules from with toolkit, since creating a module requires
        resources.
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
    https://docs.zhinst.com/labone_api_user_manual/description_and_guidelines/software_architecture.html)

    The entry point into any connection is therefor a client session to a
    existing data sever. This class represents a single client session to a
    data server. The session enables the user to connect to one or multiple
    instruments (also creates the dedicated objects for each device), access
    the LabOne modules and poll data.

    Since QCoDeS normally instantiate the device specific objects directly
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
            Warning: Creating a new session should be done carefully since it
            requires more resources and can create unwanted side effects.
        connection: Existing daq server object. If specified the session will
            not create a new session to the data server but reuse the passed
            one. (default = None)
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)
    """

    def __new__(
        cls,
        server_host: str,
        server_port: t.Optional[int] = None,
        *,
        hf2: t.Optional[bool] = None,
        new_session=False,
        connection: t.Optional[ziDAQServer] = None,
        allow_version_mismatch: bool = False,
    ):
        """Session creator."""
        if not new_session:
            for instance in Session.instances():
                if instance.server_host == server_host and (
                    (instance.is_hf2_server and hf2)
                    or server_port is None
                    or instance.server_port == server_port
                ):
                    return instance
        return Session(
            server_host,
            server_port,
            hf2=hf2,
            connection=connection,
            allow_version_mismatch=allow_version_mismatch,
        )


class Session(ZIInstrument):
    """Session to a data server.

    Zurich Instruments devices use a server-based connectivity methodology.
    Server-based means that all communication between the user and the
    instrument takes place via a computer program called a server, the data
    sever. The data sever recognizes available instruments and manages all
    communication between the instrument and the host computer on one side, and
    communication to all the connected clients on the other side. (For more
    information on the architecture please refer to the user manual
    https://docs.zhinst.com/labone_api_user_manual/description_and_guidelines/software_architecture.html)

    The entry point into for any connection is therefor a client session to a
    existing data sever. This class represents a single client session to a
    data server. The session enables the user to connect to one or multiple
    instruments (also creates the dedicated objects for each device), access
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
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)
    """

    def __init__(
        self,
        server_host: str,
        server_port: t.Optional[int] = None,
        *,
        hf2: t.Optional[bool] = None,
        connection: t.Optional[ziDAQServer] = None,
        allow_version_mismatch: bool = False,
    ):
        try:
            self._tk_object = TKSession(
                server_host,
                server_port,
                connection=connection,
                hf2=hf2,
                allow_version_mismatch=allow_version_mismatch,
            )
        except TypeError:
            self._tk_object = TKSession(
                server_host, server_port, connection=connection, hf2=hf2
            )
        super().__init__(f"zi_session_{len(self.instances())}", self._tk_object.root)
        self._devices = Devices(self, self._tk_object.devices)
        self._modules = ModuleHandler(self, self._tk_object.modules)
        init_nodetree(self, self._tk_object.root, self._snapshot_cache)

    def connect_device(
        self,
        serial: str,
        *,
        interface: t.Optional[str] = None,
        name: t.Optional[str] = None,
        raw: t.Optional[bool] = None,
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
            * Blocks until all devices have cleared their busy flag.

        Warning:
            The sync is performed for all devices connected to the daq server

        Warning:
            This command is a blocking command that can take a substantial
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
        """Polls all subscribed data.

        Poll the value changes in all subscribed nodes since either subscribing
        or the last poll (assuming no buffer overflow has occurred on the Data
        Server).

        Args:
            recording_time: defines the duration of the poll. (Note that not
                only the newly recorder values are polled but all values since
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
            tk_node = self._tk_object.raw_path_to_node(tk_node)
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
        """Modules of LabOne."""
        return self._modules

    @property
    def is_hf2_server(self) -> bool:
        """Flag if the data server is a HF2 Data Server."""
        return self._tk_object.is_hf2_server

    @property
    def daq_server(self) -> ziDAQServer:
        """Managed instance of the zi.ziDAQServer."""
        return self._tk_object.daq_server

    @property
    def server_host(self) -> str:
        """Server host."""
        return self._tk_object.server_host

    @property
    def server_port(self) -> int:
        """Server port."""
        return self._tk_object.server_port

    @property
    def toolkit_session(self) -> TKSession:
        """Underlying zhinst-toolkit session."""
        return self._tk_object
