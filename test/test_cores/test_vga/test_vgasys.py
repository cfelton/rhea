

from __future__ import division
from __future__ import print_function

"""
"""

import argparse
from argparse import Namespace

from myhdl import *

import mn
from mn.system import Clock
from mn.system import Reset
from mn.system import Global
from mn.cores.video import VGA

# a video display model to check the timings
from mn.models.video import VideoDisplay

from mn.utils.test import *

# local wrapper to build a VGA system
from mm_vgasys import mm_vgasys
from mm_vgasys import convert

def test_vgasys(args):
    # @todo: retrieve these from ...
    res = (640, 480,)  # (80,60,),  (640,480,)
    line_rate = int(31250)

    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=False)
    vselect = Signal(bool(0))

    vga = VGA(color_depth=(10,10,10), )
    

    def _test():
        # top-level VGA system 
        tbdut = mm_vgasys(clock, reset, vselect, 
                          vga.hsync, vga.vsync, 
                          vga.red, vga.green, vga.blue,
                          vga.pxlen, vga.active,
                          resolution=res,
                          line_rate=line_rate)

        # group global signals
        glbl = Global(clock=clock, reset=reset)

        # a display for each dut        
        mvd = VideoDisplay(frequency=clock.frequency,
                           resolution=res,
                           line_rate=line_rate)

        # connect VideoDisplay model to the VGA signals
        tbvd = mvd.process(glbl, vga)
        # clock generator
        tbclk = clock.gen()

        @instance
        def tbstim():
            reset.next = reset.active
            yield delay(18)
            reset.next = not reset.active
            
            # Wait till a full screen has been updated
            while mvd.update_cnt < 4:
                 yield delay(1000)

            # @todo: verify video system memory is correct!
            #    (self checking!)

            raise StopSimulation

        return tbclk, tbvd, tbstim, tbdut


    vcd = tb_clean_vcd('_test')
    traceSignals.timescale = '1ns'
    traceSignals.name = vcd
    Simulation(traceSignals(_test)).run()
    convert()

if __name__ == '__main__':
    test_vgasys(Namespace())
