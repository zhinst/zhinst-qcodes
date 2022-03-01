import typing as t

from zhinst.qcodes.driver.devices.base import ZIBaseInstrument
from zhinst.qcodes.driver.devices.hdawg import HDAWG
from zhinst.qcodes.driver.devices.pqsc import PQSC
from zhinst.qcodes.driver.devices.shfqa import SHFQA
from zhinst.qcodes.driver.devices.shfsg import SHFSG
from zhinst.qcodes.driver.devices.uhfli import UHFLI
from zhinst.qcodes.driver.devices.uhfqa import UHFQA

DeviceType = t.Union[ZIBaseInstrument, HDAWG, PQSC, SHFQA, SHFSG, UHFLI, UHFQA]

DEVICE_CLASS_BY_MODEL = {
    "SHFQA": SHFQA,
    "SHFSG": SHFSG,
    "HDAWG": HDAWG,
    "PQSC":  PQSC,
    "UHFQA": UHFQA,
    "UHFLI": UHFLI,
}
