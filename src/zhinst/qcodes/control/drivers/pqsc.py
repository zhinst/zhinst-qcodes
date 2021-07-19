from .base import ZIBaseInstrument
from qcodes.instrument.channel import ChannelList, InstrumentChannel
import qcodes.utils.validators as vals

import zhinst.toolkit as tk
from typing import List, Dict, Union
import numpy as np


class PQSC(ZIBaseInstrument):
    """QCoDeS driver for the *Zurich Instruments PQSC*"""

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
        super().__init__(name, "pqsc", serial, interface, host, port, api, **kwargs)
        submodules = self.nodetree_dict.keys()
        blacklist = []
        [self._init_submodule(key) for key in submodules if key not in blacklist]

    def _connect(self) -> None:
        """Connects the device to the data server.

        Instantiates the device controller from :mod:`zhinst-toolkit`, sets up
        the data server and connects the device the data server. This method is
        called from `__init__` of the :class:`BaseInstrument` class.

        """
        self._controller = tk.PQSC(
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
        self._add_qcodes_params()

    def _add_qcodes_params(self):
        # add custom parameters as QCoDeS parameters
        super()._add_qcodes_params()
        self.add_parameter(
            "ref_clock",
            unit=self._controller.ref_clock._unit,
            docstring=self._controller.ref_clock.__repr__(),
            get_cmd=self._controller.ref_clock,
            set_cmd=self._controller.ref_clock,
            label="Intended Reference Clock Source",
        )
        self.add_parameter(
            "ref_clock_actual",
            unit=self._controller.ref_clock_actual._unit,
            docstring=self._controller.ref_clock_actual.__repr__(),
            get_cmd=self._controller.ref_clock_actual,
            set_cmd=self._controller.ref_clock_actual,
            label="Actual Reference Clock Source",
        )
        self.add_parameter(
            "ref_clock_status",
            unit=self._controller.ref_clock_status._unit,
            docstring=self._controller.ref_clock_status.__repr__(),
            get_cmd=self._controller.ref_clock_status,
            set_cmd=self._controller.ref_clock_status,
            label="Status Reference Clock",
        )
        self.add_parameter(
            "repetitions",
            unit=self._controller.repetitions._unit,
            docstring=self._controller.repetitions.__repr__(),
            get_cmd=self._controller.repetitions,
            set_cmd=self._controller.repetitions,
            label="Repetitions (Number of Triggers)",
        )
        self.add_parameter(
            "holdoff",
            unit=self._controller.holdoff._unit,
            docstring=self._controller.holdoff.__repr__(),
            get_cmd=self._controller.holdoff,
            set_cmd=self._controller.holdoff,
            label="Hold-off Time Between Triggers",
        )
        self.add_parameter(
            "progress",
            unit=self._controller.progress._unit,
            docstring=self._controller.progress.__repr__(),
            get_cmd=self._controller.progress,
            set_cmd=self._controller.progress,
            label="Fraction of Triggers Generated",
        )

    def factory_reset(self, sync=True) -> None:
        """Load the factory default settings.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after loading the factory preset (default: True).
        """
        self._controller.factory_reset(sync=sync)

    def arm(self, sync=True, repetitions: int = None, holdoff: float = None) -> None:
        """Prepare PQSC for triggering the instruments.

        This method configures the execution engine of the PQSC and
        clears the register bank. Optionally, the *number of triggers*
        and *hold-off time* can be set when specified as keyword
        arguments. If they are not specified, they are not changed.

        Note that the PQSC is disabled at the end of the hold-off time
        after sending out the last trigger. Therefore, the hold-off time
        should be long enough such that the PQSC is still enabled when
        the feedback arrives. Otherwise, the feedback cannot be processed.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after stopping the PQSC and clearing the
                register bank (default: True).
            repetitions (int): If specified, the number of triggers sent
                over ZSync ports will be set (default: None).
            holdoff (double): If specified, the time between repeated
                triggers sent over ZSync ports will be set. It has a
                minimum value and a granularity of 100 ns
                (default: None).

        """
        self._controller.arm(sync=sync, repetitions=repetitions, holdoff=holdoff)

    def run(self, sync=True) -> None:
        """Start sending out triggers.

        This method activates the trigger generation to trigger all
        connected instruments over ZSync ports.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after enabling the PQSC (default: True).

        """
        self._controller.run(sync=sync)

    def arm_and_run(self, repetitions: int = None, holdoff: float = None) -> None:
        """Arm the PQSC and start sending out triggers.

        Simply combines the methods arm and run. A synchronisation
        is performed between the device and the data server after
        arming and running the PQSC.

        Arguments:
            repetitions (int): If specified, the number of triggers sent
                over ZSync ports will be set (default: None).
            holdoff (double): If specified, the time between repeated
                triggers sent over ZSync ports will be set. It has a
                minimum value and a granularity of 100 ns
                (default: None).

        """
        self._controller.arm_and_run(repetitions=repetitions, holdoff=holdoff)

    def stop(self, sync=True) -> None:
        """Stop the trigger generation.

        Arguments:
            sync (bool): A flag that specifies if a synchronisation
                should be performed between the device and the data
                server after disabling the PQSC (default: True).

        """
        self._controller.stop(sync=sync)

    def wait_done(self, timeout: float = 10, sleep_time: float = 0.005) -> None:
        """Wait until trigger generation and feedback processing is done.

        Arguments:
            timeout (float): The maximum waiting time in seconds for the
                PQSC (default: 10).
            sleep_time (float): Time in seconds to wait between
                requesting PQSC state

        Raises:
            TimeoutError: If the PQSC is not done sending out all
                triggers and processing feedback before the timeout.

        """
        self._controller.wait_done(timeout=timeout, sleep_time=sleep_time)

    def check_ref_clock(
        self, blocking: bool = True, timeout: int = 30, sleep_time: int = 1
    ) -> None:
        """Check if reference clock is locked successfully.

        Keyword Arguments:
            blocking (bool): A flag that specifies if the program should
                be blocked until the reference clock is 'locked'.
                (default: True)
            timeout (int): Maximum time in seconds the program waits
                when `blocking` is set to `True` (default: 30).
            sleep_time (int): Time in seconds to wait between
                requesting the reference clock status (default: 1)

        Raises:
            ToolkitError: If the device fails to lock on the reference
                clock.

        """
        self._controller.check_ref_clock(
            blocking=blocking, timeout=timeout, sleep_time=sleep_time
        )

    def check_zsync_connection(self, ports=0, blocking=True, timeout=30) -> None:
        """Check if the ZSync connection on the given port is successful.

        This function checks the current status of the instrument
        connected to the given port.

        Arguments:
            ports (list) or (int): The port numbers to check the ZSync
                connection for. It can either be a single port number given
                as integer or a list of several port numbers. (default: 0)
            blocking (bool): A flag that specifies if the program should
                be blocked until the status is 'connected'.
                (default: False)
            timeout (int): Maximum time in seconds the program waits
                when `blocking` is set to `True`. (default: 30)

        Raises:
            ToolkitError: If ZSync connection to the instruments on the
                specified ports is not established.

        """
        self._controller.check_zsync_connection(
            ports=ports, blocking=blocking, timeout=timeout
        )

    @property
    def is_running(self):
        return self._controller.is_running
