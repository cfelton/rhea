
from __future__ import print_function
from __future__ import division

import argparse

from myhdl import instance, StopSimulation

from rhea.system import Global, Clock, Reset
from rhea.system import RegisterFile, Register
from rhea.system import Barebone, Wishbone, AvalonMM, AXI4Lite
from rhea.utils.test import run_testbench, tb_args, tb_default_args

from rhea.cores.memmap import memmap_peripheral_regfile

    
def testbench_memmap(args=None):
    """  """
    args = tb_default_args(args)

    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    csrbus = Barebone(glbl, data_width=8, address_width=16)
    
    def _bench_memmap():
        tbdut = memmap_peripheral_regfile(csrbus)
        tbclk = clock.gen()

        print(csrbus.regfiles)

        @instance
        def tbstim():
            yield reset.pulse(111)
            
            raise StopSimulation
            
        return tbdut, tbclk, tbstim

    run_testbench(_bench_memmap)

    
if __name__ == '__main__':
    testbench_memmap(args=tb_args())
