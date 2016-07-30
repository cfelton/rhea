
import myhdl
from myhdl import Signal, intbv, instance, delay, StopSimulation

from rhea.system import Clock, Reset, Global, Signals
from rhea.cores.video import VGA
from rhea.models.video import VGADisplay

from rhea.utils.test import run_testbench, tb_args, tb_default_args, tb_convert

from zybo_vga import zybo_vga


def test_zybo_vga(args=None):
    args = tb_default_args(args)

    resolution = (80, 60,)
    refresh_rate = 60
    line_rate = 31250
    color_depth = (6, 6, 6,)

    clock = Clock(0, frequency=125e6)
    glbl = Global(clock)
    vga = VGA(color_depth=color_depth)
    vga_hsync, vga_vsync = Signals(bool(0), 2)
    vga_red, vga_green, vga_blue = Signals(intbv(0)[6:], 3)
    led, btn = Signals(intbv(0)[4:], 2)

    @myhdl.block
    def bench():
        tbdut = zybo_vga(led, btn, vga_red, vga_green, vga_blue,
                         vga_hsync, vga_vsync, clock,
                         resolution=resolution, color_depth=color_depth,
                         refresh_rate=refresh_rate, line_rate=line_rate)
        tbclk = clock.gen()
        mdl = VGADisplay(frequency=clock.frequency, resolution=resolution,
                         refresh_rate=refresh_rate, line_rate=line_rate,
                         color_depth=color_depth)
        tbmdl = mdl.process(glbl, vga)

        @instance
        def tbstim():
            yield delay(100000)
            raise StopSimulation

        return tbdut, tbclk, tbmdl, tbstim

    # run the above testbench, the above testbench doesn't functionally
    # verify anything only verifies basics.
    run_testbench(bench, args=args)

    # test conversion
    portmap = dict(led=led, btn=btn, vga_red=vga_red, vga_grn=vga_green,
                   vga_blu=vga_blue, vga_hsync=vga_hsync, vga_vsync=vga_vsync,
                   clock=clock)
    inst = zybo_vga(**portmap)
    tb_convert(inst)



