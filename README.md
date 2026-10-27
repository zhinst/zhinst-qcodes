# Zurich Instruments Drivers for QCoDeS (zhinst-qcodes)

The Zurich Instruments drivers for QCoDeS (zhinst-qcodes) is a package of
instrument drivers for devices produced by [Zurich Instruments](https://www.zhinst.com)
for QCoDeS. [QCoDeS](http://microsoft.github.io/Qcodes) is a Python-based data
acquisition framework developed to serve the needs of nanoelectronic device
experiments, but not limited to that. It is intended to be used within QCoDeS
and not as standalone package. The QCoDeS instrument drivers are based on the
[Zurich Instruments Toolkit](https://github.com/zhinst/zhinst-toolkit). So if
you are looking for a framework independent high level python API, zhinst-toolkit
it the right place for you.

## Status

The zhinst-qcodes is well tested and considered stable enough for general usage.
The interfaces may have some incompatible changes between releases. Please check
the changelog when updating.

### Refactoring with version 0.3

Version 0.3 is a more or less complete new driver and breaks the API compared
to the previous version in many ways.

## Install

Install the package with pip:

```
pip install zhinst-qcodes
```

## Documentation

Since zhinst-qcodes is based on zhinst-toolkit and has exactly the same interface
and functions, the [documentation](https://docs.zhinst.com/labone_api_user_manual/reference/toolkit/index.html)
for zhinst-toolkit can be applied nearly one to one.
Moreover, similar examples to those of zhinst-toolkit available
[here](https://github.com/zhinst/zhinst-toolkit/tree/main/examples)
can be used for zhinst-qcodes.

### Static typing

The parameters and submodules of a device are created at runtime from the
node tree of the connected device. For the MFLI, the package ships type stubs
describing its node tree, so IDEs and static type checkers (e.g. mypy or
pyright) know the nodes, their value types and documentation:

```python
from zhinst.qcodes import MFLI

mfli = MFLI("dev1234", "localhost")
mfli.oscs[0].freq(10e3)  # accepts a float
rate = mfli.demods[0].rate()  # float
```

The stubs are based on the node documentation of the MFLI user manual and
cover all options. Nodes of options not installed on a device are not
available at runtime.

## Contributing

We welcome contributions by the community, either as bug reports, fixes and new
code. Please use the GitHub issue tracker to report bugs or submit patches.
Before developing something new, please get in contact with us.

## License

This software is licensed under the terms of the MIT license.
See [LICENSE](LICENSE) for more detail.
