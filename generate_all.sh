#!/bin/bash
# This should move to some github action

# toolkit driver
python generator/codegen/generator.py instrument-class SHFQA
python generator/codegen/generator.py instrument-class SHFSG
python generator/codegen/generator.py instrument-class SHFQC
python generator/codegen/generator.py instrument-class HDAWG
python generator/codegen/generator.py instrument-class PQSC
python generator/codegen/generator.py instrument-class UHFLI
python generator/codegen/generator.py instrument-class UHFQA
