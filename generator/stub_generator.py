"""Generate type stubs for the dynamically created QCoDeS node tree of a device.

The QCoDeS parameters and submodules of a device are created at runtime from
the node tree reported by the LabOne Data Server. Static type checkers therefore
cannot know them. This module recreates the same QCoDeS object offline from the
stored node documentation (see ``nodedoc_scraper.py``) and writes a ``.pyi``
stub describing its structure.

The generated stub defines a mixin class ``<DEVICE>Nodes`` that the device
class in ``device_creator.py`` inherits from during type checking.
"""

from __future__ import annotations

import keyword
import re
import textwrap
import types
import typing as t
from dataclasses import dataclass, field
from pathlib import Path

from nodedoc_scraper import DEVICE_SERIAL, load_nodedoc, nodedoc_path

from zhinst.qcodes import device_creator
from zhinst.qcodes.driver.devices.base import ZIBaseInstrument
from zhinst.qcodes.qcodes_adaptions import ZIChannelList, ZINode, ZIParameter
from zhinst.toolkit.nodetree import NodeTree

STUB_DIR = (
    Path(__file__).parent.parent
    / "src"
    / "zhinst"
    / "qcodes"
    / "driver"
    / "devices"
    / "_stubs"
)
LINE_LENGTH = 88

_STREAMING_SAMPLE_TYPES = ("ZIDemodSample", "ZIDIOSample")
# Builtin types used in annotations that a node name can shadow inside a class.
_SHADOWABLE_BUILTINS = frozenset({"int", "float", "complex", "str", "dict"})
# Names used in annotations that must not be shadowed by a node name.
_RESERVED_NAMES = frozenset(
    {"Any", "Never", "np", "builtins", "ZIParameter", "ZINode", "ZIChannelList"}
)


def _qualify_builtins(annotation: str, names: t.AbstractSet[str]) -> str:
    """Prefix the given builtin type names in an annotation with ``builtins.``."""
    for name in names:
        annotation = re.sub(rf"\b{name}\b", f"builtins.{name}", annotation)
    return annotation


@dataclass
class _Attribute:
    name: str
    annotation: str
    docstring: t.Optional[str] = None


@dataclass
class _StubClass:
    name: str
    base: str
    docstring: str
    attributes: dict[str, _Attribute] = field(default_factory=dict)


def _value_types(info: dict[str, t.Any]) -> tuple[str, str]:
    """Static types for getting and setting the value of a node.

    Args:
        info: Node documentation of the node.

    Returns:
        Type annotation for the get and the set value.
    """
    node_type = info["Type"]
    if node_type == "Integer (enumerated)":
        # Get returns an ``IntEnum``; set also accepts the keyword string.
        get_type, set_type = "int", "int | str"
    elif node_type.startswith("Integer"):
        get_type, set_type = "int", "int"
    elif node_type == "Double":
        get_type, set_type = "float", "float"
    elif node_type == "Complex Double":
        get_type, set_type = "complex", "complex"
    elif node_type == "String":
        get_type, set_type = "str", "str"
    elif node_type in _STREAMING_SAMPLE_TYPES:
        get_type, set_type = "dict[str, np.ndarray]", "Never"
    else:
        # Vector nodes and nodes that can only be polled.
        get_type, set_type = "Any", "Any"
    if "Write" not in info["Properties"]:
        set_type = "Never"
    return get_type, set_type


def _documented_path(node: str) -> str:
    """Convert a node path into the notation used in the documentation."""
    segments = node.strip("/").split("/")
    return "/DEV..../" + "/".join(
        "n" if s.isdigit() else s.upper() for s in segments[1:]
    )


def _docstring(info: dict[str, t.Any], indent: str) -> str:
    """Create the docstring of a parameter from its node documentation."""
    # Leave room for the opening quotes on the first line.
    width = LINE_LENGTH - len(indent) - len('"""')
    lines = textwrap.wrap(info["Description"], width=width) or [""]
    lines += [
        "",
        f"Node: {_documented_path(info['Node'])}",
        f"Properties: {info['Properties']}",
        f"Type: {info['Type']}",
    ]
    if info["Unit"] not in ("None", ""):
        lines.append(f"Unit: {info['Unit']}")
    options = info.get("Options")
    if options:
        lines += ["", "Options:"]
        for key, value in options.items():
            lines += textwrap.wrap(
                f"{key}: {value}",
                width=width,
                initial_indent="    ",
                subsequent_indent="        ",
            )
    text = "\n".join(lines).replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    return textwrap.indent(text, indent).lstrip() + f"\n{indent}"


def _class_name(device: str, path: list[str]) -> str:
    return device.upper() + "".join(part.capitalize() for part in path)


class _StubBuilder:
    """Collect the stub classes for a QCoDeS node tree."""

    def __init__(self, device: str, nodedoc: dict[str, dict[str, t.Any]]):
        self._device = device.upper()
        self._nodedoc = nodedoc
        self.classes: dict[str, _StubClass] = {}
        self.skipped: list[str] = []

    def add_layer(
        self,
        layer: t.Any,
        path: list[str],
        node_path: list[str],
        class_name: t.Optional[str] = None,
        base: str = "ZINode",
    ) -> str:
        """Add the class describing a QCoDeS layer (instrument or ZINode).

        Elements of the same channel list share one class, the attributes of
        all elements are merged.

        Args:
            layer: QCoDeS instrument or submodule.
            path: Names of the submodules leading to the layer.
            node_path: Node path of the layer below the device root.
            class_name: Name of the class. Derived from the path if not set.
            base: Base class of the generated class.

        Returns:
            Name of the generated class.
        """
        class_name = class_name or _class_name(self._device, path)
        docstring = (
            f"Node ``{_documented_path('/dev0/' + '/'.join(node_path))}``."
            if node_path
            else f"Node tree of the {self._device}."
        )
        stub_class = self.classes.setdefault(
            class_name, _StubClass(class_name, base, docstring)
        )
        for name, parameter in layer.parameters.items():
            if not isinstance(parameter, ZIParameter):
                continue
            info = self._nodedoc[parameter.zi_node.lower()]
            get_type, set_type = _value_types(info)
            self._add_attribute(
                stub_class,
                _Attribute(
                    name,
                    f"ZIParameter[{get_type}, {set_type}]",
                    _docstring(info, "    "),
                ),
            )
        for name, submodule in layer.submodules.items():
            if isinstance(submodule, ZIChannelList):
                element_class = _class_name(self._device, [*path, name])
                for element in submodule:
                    self.add_layer(
                        element, [*path, name], [*node_path, name, "0"], element_class
                    )
                annotation = f"ZIChannelList[{element_class}]"
            elif isinstance(submodule, ZINode):
                annotation = self.add_layer(
                    submodule, [*path, name], [*node_path, name]
                )
            else:
                continue
            self._add_attribute(stub_class, _Attribute(name, annotation))
        return class_name

    def _add_attribute(self, stub_class: _StubClass, attribute: _Attribute) -> None:
        if attribute.name in _RESERVED_NAMES:
            raise RuntimeError(
                f"{stub_class.name}.{attribute.name} shadows a name used in the stub."
            )
        if not attribute.name.isidentifier() or keyword.iskeyword(attribute.name):
            # Only accessible through ``getattr`` and therefore not typable.
            self.skipped.append(f"{stub_class.name}.{attribute.name}")
            return
        existing = stub_class.attributes.get(attribute.name)
        if existing and existing.annotation != attribute.annotation:
            raise RuntimeError(
                f"{stub_class.name}.{attribute.name} has conflicting types "
                f"{existing.annotation} and {attribute.annotation}."
            )
        stub_class.attributes.setdefault(attribute.name, attribute)


def build_instrument(device: str, nodedoc: dict[str, dict[str, t.Any]]) -> t.Any:
    """Create the QCoDeS instrument of a device without a data server.

    The instrument is created with the same class used at runtime, so the
    naming of the parameters and submodules is identical.

    Args:
        device: Device type, e.g. ``MFLI``.
        nodedoc: Node documentation in the ``listNodesJSON`` format.

    Returns:
        The QCoDeS instrument. Must be closed by the caller.
    """
    device_class = getattr(device_creator, device.upper())
    nodetree = NodeTree(
        None,  # type: ignore[arg-type]
        prefix_hide=DEVICE_SERIAL,
        list_nodes=[f"/{DEVICE_SERIAL}/*"],
        preloaded_json=nodedoc,
    )
    tk_device = types.SimpleNamespace(
        root=nodetree, serial=DEVICE_SERIAL, device_type=device.upper()
    )

    def offline_init(self: t.Any) -> None:
        ZIBaseInstrument.__init__(
            self, tk_device, session=None, name=f"stubgen_{device.lower()}"
        )

    offline_class = type(
        f"Offline{device_class.__name__}", (device_class,), {"__init__": offline_init}
    )
    return offline_class()


def render_stub(device: str) -> str:
    """Render the type stub for the node tree of a device.

    Args:
        device: Device type, e.g. ``MFLI``.

    Returns:
        Content of the ``.pyi`` file (not formatted).
    """
    device = device.upper()
    nodedoc = load_nodedoc(device)
    instrument = build_instrument(device, nodedoc)
    try:
        builder = _StubBuilder(device, nodedoc)
        builder.add_layer(instrument, [], [], f"{device}Nodes", base="")
    finally:
        instrument.close()
    for skipped in builder.skipped:
        print(f"WARNING {skipped}: not a valid identifier -> ignored")

    source = nodedoc_path(device).relative_to(Path(__file__).parent.parent)
    lines = [
        "# This file is autogenerated by `python generator/generator.py stubs "
        f"{device}`. Do not edit!",
        f'"""Type stubs for the node tree of the {device}.',
        "",
        f"Generated from the node documentation in ``{source.as_posix()}``.",
        "The classes only exist for static type checking and cannot be imported",
        "at runtime.",
        '"""',
        "",
        "from typing import Any, Never",
        "",
        "import numpy as np",
        "",
        "from zhinst.qcodes.qcodes_adaptions import ZIChannelList, ZINode, ZIParameter",
        "",
    ]
    # Reverse the order so that classes are defined before they are used.
    needs_builtins = False
    for stub_class in reversed(builder.classes.values()):
        base = f"({stub_class.base})" if stub_class.base else ""
        lines += ["", f"class {stub_class.name}{base}:"]
        lines.append(f'    """{stub_class.docstring}"""')
        shadowed = _SHADOWABLE_BUILTINS & stub_class.attributes.keys()
        needs_builtins |= bool(shadowed)
        for attribute in sorted(stub_class.attributes.values(), key=lambda a: a.name):
            annotation = _qualify_builtins(attribute.annotation, shadowed)
            lines.append(f"    {attribute.name}: {annotation}")
            if attribute.docstring:
                lines.append(f'    """{attribute.docstring}"""')
    if needs_builtins:
        lines.insert(lines.index("from typing import Any, Never"), "import builtins")
    return "\n".join(lines) + "\n"


def stub_path(device: str) -> Path:
    """Path of the generated stub file of a device."""
    return STUB_DIR / f"{device.lower()}.pyi"
