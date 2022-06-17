"""Configuration for zhinst QCoDes driver generation."""

DEVICE_DRIVERS = ["SHFQA", "SHFSG", "SHFQC", "HDAWG", "PQSC", "UHFLI", "UHFQA"]
TOOLKIT_DEVICE_MODULE = "zhinst.toolkit.driver.devices"

# Typing
# Weird typing infos that can be replaced with the right term
TYPE_HINT_REPLACEMENTS = {"<built-in function array>": "np.array", "~Numpy2DArray": "np.ndarray"}
