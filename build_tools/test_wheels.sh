#!/bin/bash
wheelPath=$(find dist -type f -name \*.whl)
pip install --upgrade --force-reinstall $wheelPath
python3 -c "
import zhinst.qcodes;
from zhinst.qcodes import __version__;
print(__version__);
version = '$1'[1:] if '$1'.startswith('v') else '$1';
print(version);
assert __version__ == version
"
