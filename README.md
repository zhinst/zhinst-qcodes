# Zurich Instruments Drivers for QCoDeS (zhinst-qcodes)
The Zurich Instruments drivers for QCoDeS (zhinst-qcodes) is a package of
instrument drivers for devices produced by [Zurich Instruments](https://www.zhinst.com)
for QCoDeS. [QCoDeS](http://qcodes.github.io/Qcodes) is a Python-based data
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
to the previous version in many ways. If you upgrade from an older version take
a look at the dedicated
[documentation page](https://docs.zhinst.com/zhinst-qcodes/en/latest/refactoring/index.html)
for more information.

## Install

Install the package with pip:

```
pip install zhinst-qcodes
```

## Documentation
See the documentation page [here](https://docs.zhinst.com/zhinst-qcodes/en/latest).
Since zhinst-qcodes is based on zhinst-toolkit and has exactly the same interface
and functions, the [documenation](https://docs.zhinst.com/zhinst-toolkit/en/latest)
for zhinst-toolkit can be applied nearly one to one and has much more examples.

## Contributing
We welcome contributions by the community, either as bug reports, fixes and new
code. Please use the GitHub issue tracker to report bugs or submit patches.
Before developing something new, please get in contact with us.

## License
This software is licensed under the terms of the MIT license.
See [LICENSE](LICENSE) for more detail.
