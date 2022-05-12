"""Helper class to directly create device instances

The classes can be used without creating as session to a data server first.
"""
import typing as t

from zhinst.qcodes.session import ZISession

from zhinst.qcodes.driver.devices.base import ZIBaseInstrument
from zhinst.qcodes.driver.devices.hdawg import HDAWG as HDAWGDriver
from zhinst.qcodes.driver.devices.pqsc import PQSC as PQSCDriver
from zhinst.qcodes.driver.devices.shfqa import SHFQA as SHFQADriver
from zhinst.qcodes.driver.devices.shfqc import SHFQC as SHFQCDriver
from zhinst.qcodes.driver.devices.shfsg import SHFSG as SHFSGDriver
from zhinst.qcodes.driver.devices.uhfli import UHFLI as UHFLIDriver
from zhinst.qcodes.driver.devices.uhfqa import UHFQA as UHFQADriver


def zi_device(cls):
    docstring = getattr(cls, "__doc__")
    generic_docstring = f"""QCodes driver for the Zurich Instruments {cls.__name__}
    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port 8005. (default = None)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the Flag will create a new session.

            Warning:
                Creating a new session should be done carefully and reusing
                the created session is not possible. Consider instantiating a
                new session directly.
    """
    cls.__doc__ = docstring if docstring else generic_docstring
    orig_init = cls.__init__

    def init(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: t.Optional[str] = None,
        name=None,
        raw=None,
        new_session: bool = False,
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        orig_init(self, tk_device, session, name=name, raw=raw)

    cls.__init__ = init
    return cls


@zi_device
class ZIDevice(ZIBaseInstrument):
    pass


@zi_device
class HDAWG(HDAWGDriver):
    pass


@zi_device
class MFLI(ZIBaseInstrument):
    pass


@zi_device
class MFIA(ZIBaseInstrument):
    pass


@zi_device
class PQSC(PQSCDriver):
    pass


@zi_device
class SHFQA(SHFQADriver):
    pass


@zi_device
class SHFQC(SHFQCDriver):
    pass


@zi_device
class SHFSG(SHFSGDriver):
    pass


@zi_device
class UHFLI(UHFLIDriver):
    pass


@zi_device
class UHFQA(UHFQADriver):
    pass


class HF2(ZIBaseInstrument):
    """QCoDeS driver for the *Zurich Instruments HF2*

    This device driver works with all HF2 devices for Zurich Instrument.
    Depending on the device type qcodes may offer special functionality. For
    more information please take a look at the documentation.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port 8005. (default = None)
        interface: Device interface (e.g. = "1GbE"). If not specified
            the default interface from the discover is used.
        name: Name of the instrument in qcodes.
            (default = "zi_{dev_type}_{serial}")
        raw: Flag if qcodes instance should only created with the nodes and
            not forwarding the toolkit functions. (default = False)
        new_session: By default zhinst-qcodes reuses already existing data
            server session (within itself only), meaning only one session to a
            data server exists. Setting the Flag will create a new session.

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
        raw=None,
        new_session: bool = False,
    ):
        session = ZISession(host, port, hf2=True, new_session=new_session)
        tk_device = session.toolkit_session.connect_device(serial, interface=interface)
        super().__init__(tk_device, session, name, raw)
