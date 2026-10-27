"""Configuration for zhinst QCoDes driver generation."""

from pathlib import Path

PKG_ROOT = Path(__file__).parent
TEMPLATE_PATH = PKG_ROOT / "templates"

# Device drivers
OUTPUT_DIR_DEVICES_DRIVER = PKG_ROOT.parent / "src/zhinst/qcodes/driver/devices/"

# devices API
DEVICE_DRIVERS = ["SHFQA", "SHFSG", "SHFQC", "HDAWG", "PQSC", "UHFLI", "UHFQA"]
TOOLKIT_DEVICE_MODULE = "zhinst.toolkit.driver.devices"

# Module drivers
OUTPUT_DIR_MODULE_DRIVER = PKG_ROOT.parent / "src/zhinst/qcodes/driver/modules/"

# module API
MODULE_DRIVERS = [
    "BaseModule",
    "DAQModule",
    "DataStreamingModule",
    "DeviceSettingsModule",
    "ImpedanceModule",
    "PIDAdvisorModule",
    "PrecompensationAdvisorModule",
    "ScopeModule",
    "SweeperModule",
    "TimelineModule",
]
TOOLKIT_MODULE_MODULE = "zhinst.toolkit.driver.modules"

# Devices with generated type stubs for their node tree
# (node documentation in generator/nodedocs, see nodedoc_scraper.py)
STUB_DEVICES = ["MFLI"]
STUB_MODULE = "zhinst.qcodes.driver.devices._stubs"

# Typing
# Weird typing infos that can be replaced with the right term
TYPE_HINT_REPLACEMENTS = {
    "<built-in function array>": "np.ndarray",
    "~Numpy2DArray": "np.ndarray",
}
