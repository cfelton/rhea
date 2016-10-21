
from __future__ import print_function, division

import pytest

import myhdl
from myhdl import always, delay, instance, now, StopSimulation

import rhea
from rhea.system import Global
from rhea.cores.video import VideoStream, HDMIExtInterface
from rhea.cores.video import hdmi_xcvr

# a video desplay model to check the timings
from rhea.models.video import VideoDisplay
from rhea.utils.test import run_testbench

# @todo move cosimulation to cosimulation directory
# from _hdmi_prep_cosim import prep_cosim
# from interfaces import HDMI


def test_hdmi():
    """ simple test to demonstrate test framework
    """

    @myhdl.block
    def bench_hdmi():
        glbl = Global()
        clock, reset = glbl.clock, glbl.reset
        vid = VideoStream()
        ext = HDMIExtInterface()

        tbdut = hdmi_xcvr(glbl, vid, ext)

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
    run_testbench(bench_hdmi)
