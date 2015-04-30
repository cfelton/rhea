
from __future__ import division
from __future__ import print_function

import sys
import os
import argparse
from argparse import Namespace
from array import array

import pytest

from myhdl import *

# resuse some of the interfaces
import mn
from mn.system import Clock
from mn.system import Reset
from mn.system import Global
from mn.system import Wishbone

from mn.cores.sdram import SDRAM
from mn.cores.sdram import m_sdram
#from mn.models.sdram import SDRAMModel


@pytest.mark.xfail
def test_sdram(args):
    
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=False)
    

    def _test():
        ibus = Wishbone()
        extmem = SDRAM(clock)
        print(vars(extmem))
        tbdut = m_sdram(clock, reset, ibus, extmem)
        glbl = Global(clock=clock, reset=reset)
        tbclk = clock.gen()

        @instance
        def tbstim():
            reset.next = reset.active
            yield delay(18)
            reset.next = not reset.active

            for ii in range(100):
                yield delay(1000)

            raise StopSimulation

        return tbclk, tbdut, tbstim

    if os.path.isfile('vcd/_test.vcd'):
        os.remove('vcd/_test.vcd')

    traceSignals.timescale = '1ns'
    traceSignals.name = 'vcd/_test'
    Simulation(traceSignals(_test)).run()
    #convert()

if __name__ == '__main__':
    test_sdram(Namespace())
