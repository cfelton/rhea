
from __future__ import print_function, division

import myhdl
from myhdl import (Signal, always, instance, delay, StopSimulation)

from rhea.cores.elink import ELink   # ELink interface
# a simple model for the FPGA side
from rhea.utils.test import run_testbench, tb_args, tb_default_args


def test_elink_io(args=None):
    args = tb_default_args(args)

    @myhdl.block
    def bench_elink_io():

        @instance
        def tbstim():
            yield delay(10)
            raise StopSimulation

        return tbstim

    run_testbench(bench_elink_io, timescale='1ps', args=args)


if __name__ == '__main__':
    args = tb_args()
    test_elink_io(args)


