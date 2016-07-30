
import myhdl
from myhdl import (Signal, ResetSignal, intbv, always,
                   always_comb, concat)

from rhea.system import Global
from rhea.cores.video import VGA
from rhea.cores.video import VideoMemory
from rhea.cores.video import vga_sync
from rhea.cores.video import color_bars


@myhdl.block
def zybo_vga(
    # Ports
    led, btn, vga_red, vga_grn, vga_blu,
    vga_hsync, vga_vsync, clock, reset=None,
    # Parameters
    resolution=(1280, 1024), color_depth=(5, 6, 5),
    refresh_rate=60, line_rate=64512):
    """
    This is a VGA example for the Digilent Zybo board.

    Arguments (ports):
        led: the Zybo 4 LEDs
        btn: the Zybo 4 buttons
        vga_red: red bits
        vga_grn: green bits
        vga_blu: blue bits
        vga_hsync: horizontal sync
        vga_vsync: vertical sync

    Parameters:
        resolution: the monitor desired resolution
        color_depth: the number of bits per color
        refresh_rate: the monitor refresh rate
        line_rate: the monitor line rate

    Common configurations
        600x480, 60
        800x600, 60, 37880
        1280x1024, 60, 64512
    """

    glbl = Global(clock=clock, reset=reset)

    # VGA interface
    vga = VGA(color_depth=color_depth)
    vga.assign(hsync=vga_hsync, vsync=vga_vsync,
               red=vga_red, green=vga_grn, blue=vga_blu,)

    # video memory interface
    vmem = VideoMemory(resolution=resolution, color_depth=color_depth)

    # rhea.core instances
    bar_inst = color_bars(glbl, vmem, resolution=resolution,
                          color_depth=color_depth)

    vga_inst = vga_sync(glbl, vga, vmem, resolution=resolution,
                        refresh_rate=refresh_rate, line_rate=line_rate)

    bcnt = Signal(intbv(0, min=0, max=clock.frequency))
    blink = Signal(bool(0))

    nticks = int(clock.frequency-1)
    
    @always(clock.posedge)
    def beh_blink():
        if bcnt == nticks:
            bcnt.next = 0
            blink.next = not blink
        else:
            bcnt.next = bcnt + 1

    @always(clock.posedge)
    def beh_led():
        led.next = concat("000", blink)

    return bar_inst, vga_inst, beh_blink, beh_led
