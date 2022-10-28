"""Module for toolkit representations of native LabOne modules."""
import typing as t

from zhinst.qcodes.driver.modules.base_module import ZIBaseModule
from zhinst.qcodes.driver.modules.daq_module import ZIDAQModule
from zhinst.qcodes.driver.modules.scope_module import ZIScopeModule
from zhinst.qcodes.driver.modules.shfqa_sweeper import ZISHFQASweeper
from zhinst.qcodes.driver.modules.sweeper_module import ZISweeperModule

ModuleType = t.Union[ZIBaseModule, ZIDAQModule, ZISHFQASweeper, ZISweeperModule]
