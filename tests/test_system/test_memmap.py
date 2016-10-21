
from __future__ import print_function, division

import myhdl
from myhdl import instance, StopSimulation

from rhea.system import Global, Clock, Reset
from rhea.system import Barebone, Wishbone, AvalonMM, AXI4Lite
from rhea.utils.test import run_testbench, tb_args, tb_default_args

from rhea.cores.memmap import peripheral

    
def testbench_memmap(args=None):
    """  """
    args = tb_default_args(args)

    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    csbus = Barebone(glbl, data_width=8, address_width=16)

    @myhdl.block
    def bench_memmap():
        tbdut = peripheral(csbus)
        tbclk = clock.gen()

        print(csbus.regfiles)

        @instance
        def tbstim():
            yield reset.pulse(111)
            
            raise StopSimulation
            
        return tbdut, tbclk, tbstim

    run_testbench(bench_memmap)

    
if __name__ == '__main__':
    testbench_memmap(args=tb_args())
