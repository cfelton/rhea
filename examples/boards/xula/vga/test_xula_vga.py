
import pytest
import myhdl
from myhdl import Signal, intbv, instance, delay, StopSimulation

from rhea.system import Clock, Reset, Global, Signals
from rhea.cores.video import VGA
from rhea.models.video import VGADisplay

from rhea.utils.test import run_testbench, tb_default_args, tb_convert

from xula_vga import xula_vga


@pytest.mark.xfail()
def test_xula_vga(args=None):
    args = tb_default_args(args)

    resolution = (64, 48,)
    refresh_rate = 60
    line_rate = 31250
    color_depth = (3, 4, 3,)

    clock = Clock(0, frequency=12e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    vga = VGA(color_depth=color_depth)
    vga_hsync, vga_vsync = Signals(bool(0), 2)
    vga_red, vga_green, vga_blue = Signals(intbv(0)[6:], 3)
    vselect = Signal(bool(0))
    pxlen, active = Signals(bool(0), 2)

    @myhdl.block
    def bench():
        tbdut = xula_vga(
            clock, reset,
            vselect, vga_hsync, vga_vsync,
            vga_red, vga_green, vga_blue,
            pxlen, active,
            resolution=resolution, color_depth=color_depth,
            refresh_rate=refresh_rate, line_rate=line_rate
        )
        tbclk = clock.gen()

        mdl = VGADisplay(frequency=clock.frequency,
                         resolution=resolution,
                         refresh_rate=refresh_rate,
                         line_rate=line_rate,
                         color_depth=color_depth)
        tbmdl = mdl.process(glbl, vga)

        @instance
        def tbstim():
            yield delay(100000)
            raise StopSimulation

        return tbdut, tbclk, tbmdl, tbstim

    # run the above stimulus, the above is not self checking it simply
    # verifies the code will simulate.
    run_testbench(bench, args=args)
    portmap = dict(vselect=vselect, hsync=vga_hsync, vsync=vga_vsync,
                   red=vga_red, green=vga_green, blue=vga_blue,
                   clock=clock)

    # convert the module, check for any conversion errors
    tb_convert(xula_vga, **portmap)
