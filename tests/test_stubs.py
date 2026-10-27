"""Tests for the generated node tree type stubs."""

import ast
import json
import sys
import types
from pathlib import Path

import pytest
from zhinst.toolkit.nodetree import NodeTree

from zhinst.qcodes import device_creator
from zhinst.qcodes.driver.devices.base import ZIBaseInstrument
from zhinst.qcodes.qcodes_adaptions import ZIChannelList, ZINode, ZIParameter

REPO_ROOT = Path(__file__).parent.parent
GENERATOR_DIR = REPO_ROOT / "generator"
STUB_DIR = REPO_ROOT / "src" / "zhinst" / "qcodes" / "driver" / "devices" / "_stubs"
STUB_DEVICES = ["MFLI"]
SERIAL = "dev0"


def _build_instrument(device: str):
    """Create the QCoDeS instrument from the stored node documentation."""
    nodedoc_file = GENERATOR_DIR / "nodedocs" / f"{device.lower()}.json"
    nodes = json.loads(nodedoc_file.read_text(encoding="utf-8"))["nodes"]
    nodetree = NodeTree(
        None, prefix_hide=SERIAL, list_nodes=[f"/{SERIAL}/*"], preloaded_json=nodes
    )
    tk_device = types.SimpleNamespace(root=nodetree, serial=SERIAL, device_type=device)

    def offline_init(self):
        ZIBaseInstrument.__init__(self, tk_device, session=None, name=f"test_{device}")

    device_class = getattr(device_creator, device)
    return type(f"Offline{device}", (device_class,), {"__init__": offline_init})()


def _parse_stub(device: str) -> dict:
    """Map each class in the stub to its annotated attributes."""
    tree = ast.parse((STUB_DIR / f"{device.lower()}.pyi").read_text(encoding="utf-8"))
    classes = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes[node.name] = {
                item.target.id: ast.unparse(item.annotation)
                for item in node.body
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name)
            }
    return classes


def _compare(layer, class_name: str, stub: dict, path: str) -> None:
    attributes = stub[class_name]
    expected = set()
    for name, parameter in layer.parameters.items():
        if not isinstance(parameter, ZIParameter):
            continue
        expected.add(name)
        assert attributes[name].startswith("ZIParameter["), f"{path}.{name}"
    for name, submodule in layer.submodules.items():
        expected.add(name)
        annotation = attributes[name]
        if isinstance(submodule, ZIChannelList):
            assert annotation.startswith("ZIChannelList["), f"{path}.{name}"
            element_class = annotation[len("ZIChannelList[") : -1]
            for i, element in enumerate(submodule):
                _compare(element, element_class, stub, f"{path}.{name}[{i}]")
        else:
            assert isinstance(submodule, ZINode), f"{path}.{name}"
            _compare(submodule, annotation, stub, f"{path}.{name}")
    assert set(attributes) == expected, path


@pytest.mark.parametrize("device", STUB_DEVICES)
def test_stub_matches_runtime_nodetree(device):
    instrument = _build_instrument(device)
    try:
        _compare(instrument, f"{device}Nodes", _parse_stub(device), device.lower())
    finally:
        instrument.close()


NODEDOC_FRAGMENT = """
<details class="node">
<summary>/dev..../demods/n/adcselect <a class="headerlink" href="#x">¶</a></summary>
<p></p><table class="node_info">
    <tbody>
        <tr><td><strong>Properties:</strong></td><td>Read, Write, Setting</td></tr>
        <tr><td><strong>Type:</strong></td><td>Integer (enumerated)</td></tr>
        <tr><td><strong>Unit:</strong></td><td>None</td></tr>
    </tbody>
</table>
<p>Selects the <code>input</code> signal &amp; more.</p>
<p></p><table class="node_info">
    <tbody>
        <tr>
            <td>0</td>
            <td> "sigin0", "signal_input0": Sig In 1</td>
        </tr>
        <tr>
            <td>-1</td>
            <td> Off</td>
        </tr>
    </tbody>
</table>
</details>
<details class="node">
<summary>/dev..../pids/n/shift <a class="headerlink" href="#y">¶</a></summary>
<p></p><table class="node_info">
    <tbody>
        <tr><td><strong>Properties:</strong></td><td>Read</td></tr>
        <tr><td><strong>Type:</strong></td><td>Double</td></tr>
        <tr><td><strong>Unit:</strong></td><td>Dependent</td></tr>
    </tbody>
</table>
<p>Shift = P<em>Error + I</em>Int(Error, dt)</p>
</details>
"""


def test_parse_nodedoc_html(monkeypatch):
    pytest.importorskip("click")
    monkeypatch.syspath_prepend(str(GENERATOR_DIR))
    nodedoc_scraper = __import__("nodedoc_scraper")
    try:
        nodes = nodedoc_scraper.parse_nodedoc_html(NODEDOC_FRAGMENT)
    finally:
        sys.modules.pop("nodedoc_scraper", None)
    assert nodes == {
        "/dev0/demods/0/adcselect": {
            "Node": "/DEV0/DEMODS/0/ADCSELECT",
            "Description": "Selects the input signal & more.",
            "Properties": "Read, Write, Setting",
            "Type": "Integer (enumerated)",
            "Unit": "None",
            "Options": {"0": '"sigin0", "signal_input0": Sig In 1', "-1": "Off"},
        },
        "/dev0/pids/0/shift": {
            "Node": "/DEV0/PIDS/0/SHIFT",
            "Description": "Shift = P*Error + I*Int(Error, dt)",
            "Properties": "Read",
            "Type": "Double",
            "Unit": "Dependent",
        },
    }
