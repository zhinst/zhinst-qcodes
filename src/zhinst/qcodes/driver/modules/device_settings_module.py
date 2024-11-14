"""Autogenerated module for the DeviceSettingsModule QCoDeS driver."""
import typing as t
from typing import Union
from pathlib import Path
from zhinst.toolkit.driver.modules.device_settings_module import (
    DeviceSettingsModule as TKDeviceSettingsModule,
)

from zhinst.qcodes.driver.modules.base_module import ZIBaseModule

from zhinst.qcodes.qcodes_adaptions import (
    NodeDict,
)

if t.TYPE_CHECKING:
    from zhinst.qcodes.driver.devices import DeviceType
    from zhinst.qcodes.session import Session


class ZIDeviceSettingsModule(ZIBaseModule):
    """Implements the device settings module for storing and loading settings.

    The Device Settings Module provides functionality for saving and loading
    device settings to and from file. The file is saved in XML format.

    For simple save and load two helper functions exist `save_to_file` and
    `load_from_file`.

    Note: It is not recommend to use this function to read the
        device settings. Instead one can use the zhinst-toolkit functionality
        to read all settings from a device/subtree from the device directly by
        calling it.

    For a complete documentation see the LabOne user manual
    https://docs.zhinst.com/labone_programming_manual/device_settings_module.html


    Args:
        tk_object: Underlying zhinst-toolkit object.
        session: Session to the Data Server.
        name: Name of the module in QCoDeS.
    """

    def __init__(
        self,
        tk_object: TKDeviceSettingsModule,
        session: "Session",
        name: str = "device_settings_module",
    ):
        super().__init__(tk_object, session, name)

    def load_from_file(
        self,
        filename: Union[str, Path],
        device: Union["DeviceType", str],
        timeout: float = 30,
    ) -> None:
        """Load a LabOne settings file to a device.

        This function creates an new module instance to avoid misconfiguration.
        It is also synchronous, meaning it will block until loading the
        settings has finished.

        Args:
            filename: The path to the settings file.
            device: The device to load the settings to.
            timeout: Max time to wait for the loading to finish.

        Raises:
            TimeoutError: If the loading of the settings timed out.
        """
        return self._tk_object.load_from_file(
            filename=filename, device=device, timeout=timeout
        )

    def save_to_file(
        self,
        filename: Union[str, Path],
        device: Union["DeviceType", str],
        timeout: int = 30,
    ) -> None:
        """Save the device settings to a LabOne settings file.

        This function creates an new module instance to avoid misconfiguration.
        It is also synchronous, meaning it will block until save operation has
        finished.

        Args:
            filename: The path to the settings file.
            device: The device which settings should be saved.
            timeout: Max time to wait for the loading to finish.

        Raises:
            TimeoutError: If the loading of the settings timed out.
        """
        return self._tk_object.save_to_file(
            filename=filename, device=device, timeout=timeout
        )

    def read(self) -> NodeDict:
        """Read device settings.

        Note: It is not recommend to use this function to read the
        device settings. Instead one can use the zhinst-toolkit functionality
        to read all settings from a device/subtree from the device directly by
        calling it.

        >>> device = session.connect_device()
        >>> ...
        >>> device()
        <all device settings>
        >>> device.demods()
        <all demodulator settings>

        Returns:
            Device settings.
        """
        return NodeDict(self._tk_object.read())