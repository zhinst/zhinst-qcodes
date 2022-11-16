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
    "ScopeModule",
    "SweeperModule",
    "ImpedanceModule",
    "DeviceSettingsModule",
    "PIDAdvisorModule",
    "PrecompensationAdvisorModule",
]
TOOLKIT_MODULE_MODULE = "zhinst.toolkit.driver.modules"

# Typing
# Weird typing infos that can be replaced with the right term
TYPE_HINT_REPLACEMENTS = {
    "<built-in function array>": "np.array",
    "~Numpy2DArray": "np.ndarray",
}
