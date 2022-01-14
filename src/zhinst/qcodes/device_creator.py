"""Helper class to directly create device instances

The classes can be used withoutr creating as session to a data server first.
The device classes only implement the __new__ magic function and return the
created Instrument class object.
"""
from zhinst.qcodes.session import ZISession


class ZIDevice:
    """Zurich Instruments device driver.

    This device driver works with all devices for Zurich Instrument.
    Depending on the device type qcodes may offer special functionality. For
    more information please take a look at the documentation.

    Info:
        Although we provide device specific classes for most of our devices the
        underlying logic is exactly the same. Meaning the device specific
        classes are just for visual purposes. The reason is that the object
        creation, and mapping to the right device class happens inside the
        data server session. For more information refer to the docuemtation.

    Args:
        serial: Serial number of the device, e.g. *'dev12000'*.
            The serial number can be found on the back panel of the instrument.
        server_host: Host address of the data server (e.g. localhost)
        server_port: Port number of the data server. If not specified the session
            uses the default port 8004. (default = None)
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
                Creating a new session should be done cearfully and reusing
                the created sesison is not possible. Consider instantiating a
                new session directly.
    """

    def __new__(
        self,
        serial: str,
        host: str,
        port: int = 8004,
        *,
        interface: str = None,
        name=None,
        raw=None,
        new_session: bool = False
    ):
        session = ZISession(host, port, hf2=False, new_session=new_session)
        return session.connect_device(serial, interface=interface, name=name, raw=raw)


class ZIDeviceHF2:
    """Zurich Instruments HF2 device driver.

    This device driver works with all HF2 devices for Zurich Instrument.
    Depending on the device type qcodes may offer special functionality. For
    more information please take a look at the documentation.

    Info:
        Although we provide device specific classes for most of our devices the
        underlying logic is exactly the same. Meaning the device specific
        classes are just for visual purposes. The reason is that the object
        creation, and mapping to the right device class happens inside the
        data server session. For more information refer to the docuemtation.

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
                Creating a new session should be done cearfully and reusing
                the created sesison is not possible. Consider instantiating a
                new session directly.
    """

    def __new__(
        self,
        serial: str,
        host: str,
        port: int = 8005,
        *,
        interface: str = None,
        name=None,
        raw=None,
        new_session: bool = False
    ):
        session = ZISession(host, port, hf2=True, new_session=new_session)
        return session.connect_device(serial, interface=interface, name=name, raw=raw)
