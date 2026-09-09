"""Tests for snapshot ``update`` handling in the ZI qcodes adaptions.

These cover the fix for the bulk node-tree read being performed for any truthy
``update`` value: since QCoDeS 0.59 the measurement ``Runner`` snapshots the
station with ``update="Only_invalid"`` (a truthy string) before every dataset,
which previously forced a full ``get("/dev.../*")`` read on every acquisition
and could time out. The bulk read must only happen for a full ("All"/``True``)
snapshot.
"""

from unittest.mock import MagicMock

import pytest
from qcodes.instrument import Instrument

from zhinst.qcodes.qcodes_adaptions import (
    ZIInstrument,
    ZINode,
    ZIParameter,
    _is_full_snapshot_update,
)


@pytest.mark.parametrize(
    "update, expected",
    [
        (True, True),
        ("All", True),
        (None, False),
        ("Only_invalid", False),
        (False, False),
        ("Never", False),
    ],
)
def test_is_full_snapshot_update(update, expected):
    assert _is_full_snapshot_update(update) is expected


class _FakeConnection:
    def __init__(self, value_map):
        self._value_map = value_map
        self.get_calls = []

    def get(self, path, **kwargs):
        self.get_calls.append(path)
        return dict(self._value_map)


class _FakeNodeTree:
    def __init__(self, connection):
        self.connection = connection
        self.prefix_hide = ""


@pytest.fixture()
def instrument():
    root_node = "/dev3000/oscs/0/freq"
    child_node = "/dev3000/demods/0/rate"
    connection = _FakeConnection(
        {
            root_node.lower(): {"value": [111]},
            child_node.lower(): {"value": [222]},
        }
    )
    instr = ZIInstrument("zi_snapshot_test", _FakeNodeTree(connection))

    counters = {"root": 0, "child": 0}

    def root_get():
        counters["root"] += 1
        return 1.0

    def child_get():
        counters["child"] += 1
        return 2.0

    instr.add_parameter(
        "freq",
        parameter_class=ZIParameter,
        get_cmd=root_get,
        set_cmd=lambda value: None,
        snapshot_cache=instr._snapshot_cache,
        zi_node=root_node,
        tk_node=MagicMock(),
    )
    child = ZINode(
        parent=instr,
        name="demod0",
        snapshot_cache=instr._snapshot_cache,
        zi_node="/dev3000/demods/0",
    )
    instr.add_submodule("demod0", child)
    child.add_parameter(
        "rate",
        parameter_class=ZIParameter,
        get_cmd=child_get,
        set_cmd=lambda value: None,
        snapshot_cache=instr._snapshot_cache,
        zi_node=child_node,
        tk_node=MagicMock(),
    )

    yield instr, connection, counters
    Instrument.close_all()


@pytest.mark.parametrize("update", ["Only_invalid", None, "Never", False])
def test_partial_snapshot_does_not_bulk_read(instrument, update):
    instr, connection, _counters = instrument
    instr.snapshot(update=update)
    # No whole-tree ``get(".../*")`` at the instrument or submodule level.
    assert connection.get_calls == []


@pytest.mark.parametrize("update", ["Only_invalid", None])
def test_only_invalid_reads_invalid_caches_individually(instrument, update):
    instr, connection, counters = instrument
    instr.snapshot(update=update)
    assert connection.get_calls == []
    # The invalid caches (root + submodule child) are refreshed one at a time.
    assert counters["root"] == 1
    assert counters["child"] == 1


@pytest.mark.parametrize("update", ["All", True])
def test_full_snapshot_uses_single_bulk_read(instrument, update):
    instr, connection, counters = instrument
    instr.snapshot(update=update)
    assert len(connection.get_calls) == 1
    # Values come from the bulk dict, so no per-parameter device reads.
    assert counters["root"] == 0
    assert counters["child"] == 0


def test_bare_snapshot_defaults_to_full_read(instrument):
    instr, connection, _counters = instrument
    instr.snapshot()
    assert len(connection.get_calls) == 1
