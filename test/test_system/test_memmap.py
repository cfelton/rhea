
from __future__ import print_function
from __future__ import division

import argparse

from rhea.system import RegisterFile, Register
from rhea.system import Barebone, Wishbone, AvalonMM, AXI4Lite
from rhea.utils.test import run_testbench, tb_args, tb_default_args

from regfilesys import regfilesys

    
def testbench_memmap(args=None):
    """  """
    args = tb_default_args(args)
    
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    
    def _bench_memmap():
        tbdut = regfilesys()
        tbclk = clock.gen()
        
    
    run_testbench(_bench_memmap)

    
if __name__ == '__main__':
    testbench_memmap(args=tb_args())
    
    