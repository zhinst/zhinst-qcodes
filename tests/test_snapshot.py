"""Tests for snapshot ``update`` handling in the ZI qcodes adaptions.

Covers: the bulk read only fires for a full snapshot or an "Only_invalid"
snapshot with an invalid cache, and a failing bulk read falls back
per-parameter instead of aborting.
"""

from unittest.mock import MagicMock

import pytest
from qcodes.instrument import Instrument

from zhinst.qcodes.qcodes_adaptions import (
    ZIInstrument,
    ZINode,
    ZIParameter,
    _is_full_snapshot_update,
    _needs_bulk_snapshot_read,
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


class _FakeCache:
    def __init__(self, valid):
        self.valid = valid


class _FakeParameter:
    def __init__(self, valid):
        self.cache = _FakeCache(valid)


class _FakeNode:
    def __init__(self, parameters=None, submodules=None):
        self.parameters = parameters or {}
        self.submodules = submodules or {}


@pytest.mark.parametrize(
    "update, any_invalid, expected",
    [
        (True, False, True),
        ("All", False, True),
        (False, True, False),
        ("Never", True, False),
        ("Only_invalid", True, True),
        ("Only_invalid", False, False),
        (None, True, True),
        (None, False, False),
    ],
)
def test_needs_bulk_snapshot_read(update, any_invalid, expected):
    node = _FakeNode(
        parameters={"p": _FakeParameter(valid=not any_invalid)},
        submodules={"sub": _FakeNode(parameters={"q": _FakeParameter(valid=True)})},
    )
    assert _needs_bulk_snapshot_read(node, update) is expected


def test_needs_bulk_snapshot_read_rejects_unrecognized_update():
    # Only None/"Only_invalid" may trigger the invalid-cache check; anything
    # else not covered by _is_full_snapshot_update must not read at all,
    # even with an invalid cache present.
    node = _FakeNode(parameters={"p": _FakeParameter(valid=False)})
    assert _needs_bulk_snapshot_read(node, "some_unexpected_value") is False


def test_needs_bulk_snapshot_read_checks_nested_submodule():
    node = _FakeNode(
        parameters={"p": _FakeParameter(valid=True)},
        submodules={"sub": _FakeNode(parameters={"q": _FakeParameter(valid=False)})},
    )
    assert _needs_bulk_snapshot_read(node, "Only_invalid") is True
    assert _needs_bulk_snapshot_read(node, None) is True


class _FakeConnection:
    def __init__(self, value_map, raise_on_get=False):
        self._value_map = value_map
        self.get_calls = []
        self.raise_on_get = raise_on_get

    def get(self, path, **kwargs):
        self.get_calls.append(path)
        if self.raise_on_get:
            raise TimeoutError("Command timed out")
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


@pytest.mark.parametrize("update", ["Never", False])
def test_never_snapshot_does_not_bulk_read(instrument, update):
    instr, connection, _counters = instrument
    instr.snapshot(update=update)
    assert connection.get_calls == []


@pytest.mark.parametrize("update", ["Only_invalid", None])
def test_only_invalid_bulk_reads_when_a_cache_is_invalid(instrument, update):
    instr, connection, counters = instrument
    instr.snapshot(update=update)
    assert len(connection.get_calls) == 1
    assert counters["root"] == 0
    assert counters["child"] == 0


@pytest.mark.parametrize("update", ["Only_invalid", None])
def test_only_invalid_skips_bulk_read_once_caches_are_valid(instrument, update):
    instr, connection, _counters = instrument
    instr.snapshot(update="All")  # marks every cache valid
    connection.get_calls.clear()
    instr.snapshot(update=update)
    assert connection.get_calls == []


def test_only_invalid_second_snapshot_costs_nothing_at_all(instrument):
    # Skipping the per-parameter get too is qcodes' own behavior, only
    # guaranteed for ``None`` (not the "Only_invalid" string pre-0.59).
    instr, connection, counters = instrument
    instr.snapshot(update="All")
    connection.get_calls.clear()
    instr.snapshot(update=None)
    assert connection.get_calls == []
    assert counters["root"] == 0
    assert counters["child"] == 0


@pytest.mark.parametrize("update", ["Only_invalid", None])
def test_only_invalid_falls_back_per_parameter_if_bulk_read_fails(instrument, update):
    instr, connection, counters = instrument
    connection.raise_on_get = True
    instr.snapshot(update=update)
    # Bulk read failed but didn't abort; fell back per-parameter instead.
    assert len(connection.get_calls) == 1
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
