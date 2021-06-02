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
        self._controller.connect_device(nodetree=False)
        self.connect_message()
        self._get_nodetree_dict()
        self._add_qcodes_params()

    def _add_qcodes_params(self):
        # add custom parameters as QCoDeS parameters
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
            "progress",
            unit=self._controller.progress._unit,
            docstring=self._controller.progress.__repr__(),
            get_cmd=self._controller.progress,
            set_cmd=self._controller.progress,
            label="Fraction of Triggers Generated",
        )

    def factory_reset(self) -> None:
        """Load the factory default settings."""
        self._controller.factory_reset()

    def arm(self, repetitions=None, holdoff=None) -> None:
        """Prepare PQSC for triggering the instruments.

        This method configures the execution engine of the PQSC and
        clears the register bank. Optionally, the *number of triggers*
        and *hold-off time* can be set when specified as keyword
        arguments. If they are not specified, they are not changed.

        Note that the PQSC is disabled at the end of the hold-off time
        after sending out the last trigger. Therefore, the hold-off time
        should be long enough such that the PQSC is still enabled when
        the feedback arrives. Otherwise, the feedback cannot be processed.

        Keyword Arguments:
            repetitions (int): If specified, the number of triggers sent
                over ZSync ports will be set. (default: None)
            holdoff (double): If specified, the time between repeated
                triggers sent over ZSync ports will be set. It has a
                minimum value and a granularity of 100 ns. (default: None)

        """
        self._controller.arm(repetitions=repetitions, holdoff=holdoff)

    def check_ref_clock(self, blocking=True, timeout=30) -> None:
        """Check if reference clock is locked succesfully.

        Keyword Arguments:
            blocking (bool): A flag that specifies if the program should
                be blocked until the reference clock is 'locked'.
                (default: True)
            timeout (int): Maximum time in seconds the program waits
                when `blocking` is set to `True`. (default: 30)

        """
        self._controller.check_ref_clock(blocking=blocking, timeout=timeout)
