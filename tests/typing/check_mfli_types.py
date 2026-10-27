# mypy: warn-unused-ignores
"""Static typing checks for the generated MFLI node tree stubs.

This file is not executed. It is checked by mypy and pyright
(see the ``typing`` environment in ``tox.ini``).
"""

from typing import TYPE_CHECKING, Any, Never

import numpy as np
from typing_extensions import assert_type

from zhinst.qcodes import MFLI
from zhinst.qcodes.qcodes_adaptions import ZIChannelList, ZIParameter

if TYPE_CHECKING:
    # Stub only module; pyright warns that there is no runtime source.
    from zhinst.qcodes.driver.devices._stubs.mfli import (  # pyright: ignore[reportMissingModuleSource]
        MFLIDemods,
    )


def check_mfli_types(mfli: MFLI) -> None:
    # Nested submodules and channel lists
    assert_type(mfli.demods, ZIChannelList[MFLIDemods])
    assert_type(mfli.demods[0], MFLIDemods)
    assert_type(mfli.oscs[0].freq, ZIParameter[float, float])
    assert_type(mfli.demods[0].freq, ZIParameter[float, Never])
    assert_type(mfli.demods[0].rate(), float)
    assert_type(mfli.sigins[0].range(), float)
    assert_type(mfli.sigins[0].float(), int)
    assert_type(mfli.auxins[0].values[1].value(), float)
    assert_type(mfli.system.fwrevision(), int)
    assert_type(mfli.features.devtype(), str)
    assert_type(mfli.demods[0].sample(), dict[str, np.ndarray])
    assert_type(mfli.scopes[0].wave(), Any)

    for demod in mfli.demods:
        assert_type(demod.enable(), int)

    # Enumerated nodes accept the integer value and the keyword
    mfli.demods[0].adcselect(0)
    mfli.demods[0].adcselect("sigin0")
    # Read only nodes can not be set
    mfli.demods[0].sample(1)  # type: ignore[call-overload] # pyright: ignore[reportCallIssue, reportArgumentType]
    mfli.clockbase(1.0)  # type: ignore[call-overload] # pyright: ignore[reportCallIssue, reportArgumentType]
    # Value types are checked
    mfli.oscs[0].freq("1MHz")  # type: ignore[call-overload] # pyright: ignore[reportCallIssue, reportArgumentType]

    # Get and set options
    assert_type(mfli.oscs[0].freq(1e6), None)
    assert_type(mfli.oscs[0].freq(1e6, deep=True), float)
    assert_type(mfli.oscs[0].freq(deep=True), tuple[int | None, float])
    assert_type(mfli.oscs[0].freq(enum=False, parse=False), float)

    # Regular instrument attributes are still available
    assert_type(mfli.serial, str)
