
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

from _hdmi_prep_cosim import prep_cosim
from interfaces import HDMI


def test_hdmi(args):
    """ simple test to demonstrate test framework
    """

    clock = Signal(bool(0))
    reset = ResetSignal(0, active=0, async=True)

    tbdut = prep_cosim(clock, reset, args=args)
    
    def _test():

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

    traceSignals.timescale = '1ns'
    traceSignals.name = 'vcd/_test'
    fn = traceSignals.name + '.vcd'
    if os.path.isfile(fn):
        os.remove(fn)

    Simulation((traceSignals(_test), tbdut,)).run()


