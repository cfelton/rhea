
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
import rhea
from rhea.system import Clock
from rhea.system import Reset
from rhea.system import Global
from rhea.system import Wishbone

from rhea.cores.sdram import SDRAMInterface
from rhea.cores.sdram import sdram_sdr_controller
from rhea.models.sdram import SDRAMModel
from rhea.models.sdram import sdram_controller_model


@pytest.mark.xfail
def test_sdram(args):
    
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=False)

    def _test_stim():

        # interfaces to the modules
        ibus = Wishbone()
        extmem = SDRAMInterface(clock)
        print(vars(extmem))
        glbl = Global(clock=clock, reset=reset)

        # Models
        sdram = SDRAMModel()
        sdram_ctlr_model = sdram_controller_model(extmem, ibus)


        tbdut = sdram_sdr_controller(ibus, extmem)
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
