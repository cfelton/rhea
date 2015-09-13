
from __future__ import division
from __future__ import print_function

"""
"""

import sys
import os
import argparse
from argparse import Namespace
from array import array

from myhdl import *

import rhea
from rhea.system import Global
from rhea.cores.video import HDMI
from rhea.cores.video import hdmi

# a video desplay model to check the timings
from rhea.models.video import VideoDisplay
from rhea.utils.test import tb_clean_vcd

# @todo move cosimulation to cosimulation directory
#from _hdmi_prep_cosim import prep_cosim
#from interfaces import HDMI


def test_hdmi():
    """ simple test to demonstrate test framework
    """

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=0, async=True)

    # this currently tests a Verilog version
    #tbdut = prep_cosim(clock, reset, args=args)
    tbdut = hdmi()
    
    def _test():

        #tbdut = mm_hdmisys(glbl, vselect, hdmi,
        #                   resolution=res,
        #                   line_rate=line_rate)

        # clock for the design
        @always(delay(5))
        def tbclk():
            clock.next = not clock

        @instance
        def tbstim():
            yield delay(13)
            reset.next = reset.active
            yield delay(33)
            reset.next = not reset.active
            yield clock.posedge

            try:
                for ii in range(100):
                    yield delay(100)
                
            except AssertionError as err:
                print("@E: assertion error @ %d ns" % (now(),))
                print("    %s" % (str(err),))
                # additional simulation cycles after the error
                yield delay(111)
                raise err

            except Exception as err:
                print("@E: error occurred")
                print("    %s" % (str(err),))
                raise err

            raise StopSimulation

        return tbclk, tbstim

    # run the above test
    vcd = tb_clean_vcd('_test')
    traceSignals.timescale = '1ns'
    traceSignals.name = vcd
    #Simulation((traceSignals(_test), tbdut,)).run()


