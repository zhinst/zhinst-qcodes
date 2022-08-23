"""Configuration for zhinst QCoDes driver generation."""
from pathlib import Path


PKG_ROOT = Path(__file__).parent
TEMPLATE_PATH = PKG_ROOT / "templates"

# Device drivers
OUTPUT_DIR_DEVICES_DRIVER = PKG_ROOT.parent / "src/zhinst/qcodes/driver/devices/"

# devices API
DEVICE_DRIVERS = ["SHFQA", "SHFSG", "SHFQC", "HDAWG", "PQSC", "UHFLI", "UHFQA"]
TOOLKIT_DEVICE_MODULE = "zhinst.toolkit.driver.devices"

# Typing
# Weird typing infos that can be replaced with the right term
TYPE_HINT_REPLACEMENTS = {
    "<built-in function array>": "np.array",
    "~Numpy2DArray": "np.ndarray",
}
