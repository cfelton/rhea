
from __future__ import print_function, division

from argparse import Namespace
import time 

import myhdl
from myhdl import Signal, instance, delay, StopSimulation

from rhea import Clock, Reset, Global
from rhea.cores.video import VGA

# a video display model to check the timings
from rhea.models.video import VGADisplay

from rhea.utils.test import skip_long_sim_test
from rhea.utils.test import run_testbench, tb_default_args

# local wrapper to build a VGA system
from mm_vgasys import mm_vgasys
from mm_vgasys import convert


@skip_long_sim_test
def test_vgasys(args=None):
    if args is None:
        args = Namespace(resolution=(80, 60), color_depth=(8, 8, 8),
                         line_rate=31250, refresh_rate=60)
    args = tb_default_args(args)

    resolution = args.resolution
    refresh_rate = args.refresh_rate
    line_rate = args.line_rate
    color_depth = args.color_depth

    args = tb_default_args(args)

    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=False)
    vselect = Signal(bool(0))

    # interface to the VGA driver and emulated display
    vga = VGA(color_depth=color_depth)

    @myhdl.block
    def bench_vgasys():
        # top-level VGA system 
        tbdut = mm_vgasys(
            clock, reset, vselect, vga.hsync, vga.vsync,
            vga.red, vga.green, vga.blue, vga.pxlen, vga.active,
            resolution=resolution,
            color_depth=color_depth,
            refresh_rate=refresh_rate,
            line_rate=line_rate
        )

        # group global signals
        glbl = Global(clock=clock, reset=reset)

        # a display for each dut        
        mvd = VGADisplay(
            frequency=clock.frequency,
            resolution=resolution,
            refresh_rate=refresh_rate,
            line_rate=line_rate,
            color_depth=color_depth
        )

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
            while mvd.update_cnt < 3:
                 yield delay(1000)

            print("display updates complete")
            time.sleep(1)
            # @todo: verify video system memory is correct!
            # @todo: (self checking!).  Read one of the frame
            # @todo: png's and verify a couple bars are expected

            raise StopSimulation

        return tbclk, tbvd, tbstim, tbdut

    # run the verification simulation
    run_testbench(bench_vgasys, args=args)


def test_vgasys_conversion():
    convert()


if __name__ == '__main__':
    args = Namespace(
        resolution=(80, 60),
        color_depth=(10, 10, 10),
        line_rate=4000,
        refresh_rate=60
    )
    test_vgasys(args)
    convert()
