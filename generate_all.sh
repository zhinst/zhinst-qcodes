#!/bin/bash
# This should move to some github action

# toolkit driver
python generator.py instrument-class SHFQA
python generator.py instrument-class SHFSG
python generator.py instrument-class SHFQC
python generator.py instrument-class HDAWG
python generator.py instrument-class PQSC
python generator.py instrument-class UHFLI
python generator.py instrument-class UHFQA
