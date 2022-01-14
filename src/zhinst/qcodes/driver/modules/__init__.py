import typing as t

from zhinst.qcodes.driver.modules.base_module import ZIBaseModule
from zhinst.qcodes.driver.modules.shfqa_sweeper import ZISHFQASweeper
from zhinst.qcodes.driver.modules.sweeper_module import ZISweeperModule

ModuleType = t.Union[ZIBaseModule, ZISHFQASweeper, ZISweeperModule]
