
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

import mn
from mn.system import Global
from mn.cores.video import HDMI
from mn.cores.video import m_hdmi

# a video desplay model to check the timings
form mn.models.video import VideoDisplay

# @todo move cosimulation to cosimulation directory
from _hdmi_prep_cosim import prep_cosim
from interfaces import HDMI


def test_hdmi(args):
    """ simple test to demonstrate test framework
    """

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=0, async=True)

    # this currently tests a Verilog version
    tbdut = prep_cosim(clock, reset, args=args)

    
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
                
            except AssertionError, err:
                print("@E: assertion error @ %d ns" % (now(),))
                print("    %s" % (str(err),))
                # additional simulation cycles after the error
                yield delay(111)
                raise err

            except Exception, err:
                print("@E: error occurred")
                print("    %s" % (str(err),))
                raise err

            raise StopSimulation

        return tbclk, tbstim

    # run the above test
    vcd = tb_clean_vcd('_test')
    traceSignals.timescale = '1ns'
    traceSignals.name = vcd
    Simulation((traceSignals(_test), tbdut,)).run()


