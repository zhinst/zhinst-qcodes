"""Tests that all QCoDeS module wrappers can be instantiated."""

import pytest
from unittest.mock import MagicMock, patch
from fixtures import data_dir, mock_connection

from qcodes import Instrument
from zhinst.qcodes import ZISession
import zhinst.qcodes.driver.modules as ZIModules

# daq_server methods called by toolkit when creating each module
_DAQ_SERVER_MODULE_METHODS = [
    "awgModule",
    "dataAcquisitionModule",
    "dataStreamingModule",
    "deviceSettings",
    "impedanceModule",
    "multiDeviceSyncModule",
    "pidAdvisor",
    "precompensationAdvisor",
    "quantumAnalyzerModule",
    "scopeModule",
    "sweep",
    "timelineModule",
]

_CREATE_METHODS = [
    ("create_awg_module", ZIModules.ZIBaseModule),
    ("create_daq_module", ZIModules.ZIDAQModule),
    ("create_data_streaming_module", ZIModules.ZIDataStreamingModule),
    ("create_device_settings_module", ZIModules.ZIDeviceSettingsModule),
    ("create_impedance_module", ZIModules.ZIImpedanceModule),
    ("create_mds_module", ZIModules.ZIBaseModule),
    ("create_pid_advisor_module", ZIModules.ZIPIDAdvisorModule),
    ("create_precompensation_advisor_module", ZIModules.ZIPrecompensationAdvisorModule),
    ("create_qa_module", ZIModules.ZIBaseModule),
    ("create_scope_module", ZIModules.ZIScopeModule),
    ("create_sweeper_module", ZIModules.ZISweeperModule),
    ("create_shfqa_sweeper", ZIModules.ZISHFQASweeper),
    ("create_timeline_module", ZIModules.ZITimelineModule),
]

_MANAGED_PROPERTIES = [
    ("awg", ZIModules.ZIBaseModule),
    ("daq", ZIModules.ZIDAQModule),
    ("data_streaming", ZIModules.ZIDataStreamingModule),
    ("device_settings", ZIModules.ZIDeviceSettingsModule),
    ("impedance", ZIModules.ZIImpedanceModule),
    ("mds", ZIModules.ZIBaseModule),
    ("pid_advisor", ZIModules.ZIPIDAdvisorModule),
    ("precompensation_advisor", ZIModules.ZIPrecompensationAdvisorModule),
    ("qa", ZIModules.ZIBaseModule),
    ("scope", ZIModules.ZIScopeModule),
    ("sweeper", ZIModules.ZISweeperModule),
    ("shfqa_sweeper", ZIModules.ZISHFQASweeper),
    ("timeline", ZIModules.ZITimelineModule),
]


@pytest.fixture()
def module_session(data_dir, mock_connection):
    json_path = data_dir / "nodedoc_zi.json"
    with json_path.open("r", encoding="UTF-8") as file:
        nodes_json = file.read()
    mock_connection.return_value.listNodesJSON.return_value = nodes_json

    raw_module = MagicMock()
    raw_module.listNodesJSON.return_value = "{}"
    for method in _DAQ_SERVER_MODULE_METHODS:
        getattr(mock_connection.return_value, method).return_value = raw_module

    with patch("zhinst.toolkit.driver.modules.shfqa_sweeper.CoreSweeper"):
        yield ZISession("localhost")
    Instrument.close_all()


@pytest.mark.parametrize("create_method,expected_class", _CREATE_METHODS)
def test_create_module(module_session, create_method, expected_class):
    module = getattr(module_session.modules, create_method)()
    assert isinstance(module, expected_class)


@pytest.mark.parametrize("prop_name,expected_class", _MANAGED_PROPERTIES)
def test_managed_module(module_session, prop_name, expected_class):
    module = getattr(module_session.modules, prop_name)
    assert isinstance(module, expected_class)
    assert getattr(module_session.modules, prop_name) is module
