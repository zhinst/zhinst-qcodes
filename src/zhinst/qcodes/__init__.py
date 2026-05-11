"""QCoDeS Drivers for Zurich Instruments devices."""

from zhinst.qcodes.device_creator import (
    GHFLI,
    HDAWG,
    HF2,
    MFIA,
    MFLI,
    PQSC,
    SHFLI,
    SHFQA,
    SHFQC,
    SHFSG,
    UHFLI,
    UHFQA,
    ZIDevice,
)
from zhinst.qcodes.session import ZISession
from zhinst.toolkit import (
    AveragingMode,
    CommandTable,
    PollFlags,
    Sequence,
    SHFQAChannelMode,
    Waveforms,
)

try:
    from zhinst.qcodes._version import version as __version__
except ModuleNotFoundError:
    pass

__all__ = [
    "ZISession",
    "HDAWG",
    "MFLI",
    "MFIA",
    "PQSC",
    "SHFQA",
    "SHFQC",
    "SHFSG",
    "UHFLI",
    "UHFQA",
    "ZIDevice",
    "HF2",
    "SHFLI",
    "GHFLI",
    "Waveforms",
    "CommandTable",
    "Sequence",
    "PollFlags",
    "AveragingMode",
    "SHFQAChannelMode",
]
