#!/bin/bash
# This should move to some github action

# toolkit driver
python generator/generator.py instrument-class SHFQA
python generator/generator.py instrument-class SHFSG
python generator/generator.py instrument-class SHFQC
python generator/generator.py instrument-class HDAWG
python generator/generator.py instrument-class PQSC
python generator/generator.py instrument-class UHFLI
python generator/generator.py instrument-class UHFQA
