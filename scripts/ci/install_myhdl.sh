#!/bin/sh
git clone https://github.com/jandecaluwe/myhdl
cd myhdl
python setup.py install
make -C cosimulation/icarus
# copy the VPI to the test directory
cp cosimulation/icarus/myhdl.vpi ../test/test_cosim
