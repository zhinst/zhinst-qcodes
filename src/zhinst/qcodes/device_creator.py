"""Device instance module.

The classes can be used without creating as session to a data server.
"""

import typing as t

from zhinst.qcodes.driver.devices.base import ZIBaseInstrument
from zhinst.qcodes.driver.devices.hdawg import HDAWG as HDAWGDriver
from zhinst.qcodes.driver.devices.pqsc import PQSC as PQSCDriver
from zhinst.qcodes.driver.devices.shfqa import SHFQA as SHFQADriver
from zhinst.qcodes.driver.devices.shfqc import SHFQC as SHFQCDriver
from zhinst.qcodes.driver.devices.shfsg import SHFSG as SHFSGDriver
from zhinst.qcodes.driver.devices.uhfli import UHFLI as UHFLIDriver
from zhinst.qcodes.driver.devices.uhfqa import UHFQA as UHFQADriver
from zhinst.qcodes.session import ZISession


class ZIDevice(ZIBaseInstrument):
    """QCoDeS driver for the Zurich Instruments ZIDevice.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8004)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(
            host,
            port,
            hf2=False,
            new_session=new_session,
            allow_version_mismatch=allow_version_mismatch,
        )
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self


class SHFQA(SHFQADriver):
    """QCoDeS driver for the Zurich Instruments SHFQA.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8004)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self


class SHFSG(SHFSGDriver):
    """QCoDeS driver for the Zurich Instruments SHFSG.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8004)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self


class HDAWG(HDAWGDriver):
    """QCoDeS driver for the Zurich Instruments HDAWG.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8004)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self


class PQSC(PQSCDriver):
    """QCoDeS driver for the Zurich Instruments PQSC.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8004)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self


class SHFQC(SHFQCDriver):
    """QCoDeS driver for the Zurich Instruments SHFQC.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8004)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self


class UHFLI(UHFLIDriver):
    """QCoDeS driver for the Zurich Instruments UHFLI.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8004)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self


class UHFQA(UHFQADriver):
    """QCoDeS driver for the Zurich Instruments UHFQA.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8004)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self


class SHFLI(ZIBaseInstrument):
    """QCoDeS driver for the Zurich Instruments SHFLI.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8004)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self


class GHFLI(ZIBaseInstrument):
    """QCoDeS driver for the Zurich Instruments GHFLI.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8004)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self


class MFLI(ZIBaseInstrument):
    """QCoDeS driver for the Zurich Instruments MFLI.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8004)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self


class MFIA(ZIBaseInstrument):
    """QCoDeS driver for the Zurich Instruments MFIA.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8004)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self


class HF2(ZIBaseInstrument):
    """QCoDeS driver for the Zurich Instruments HF2.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port. (default = 8005)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the flag will create a new session.
        allow_version_mismatch: if set to True, the connection to the data-server
            will succeed even if the data-server is on a different version of LabOne.
            If False, an exception will be raised if the data-server is on a
            different version. (default = False)

    Warning:
        Creating a new session should be done carefully and reusing
        the created session is not possible. Consider instantiating a
        new session directly.
    """

    def __init__(
        self,
        serial: str,
        host: str,
        port: int = 8005,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=False,
        new_session: bool = False,
        allow_version_mismatch: bool = False,
    ):
        session = ZISession(host, port, hf2=True, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name=name, raw=raw)
        session.devices[self.serial] = self
