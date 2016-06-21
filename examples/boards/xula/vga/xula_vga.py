
import myhdl
from myhdl import Signal, intbv

from rhea import Clock, Reset, Global
from rhea.cores.video import VGA
from rhea.cores.video import VideoMemory
from rhea.cores.video import vga_sync
from rhea.cores.video import color_bars
from rhea.utils.test import tb_convert


@myhdl.block
def mm_vgasys(
    # ~~~[PORTS]~~~
    clock,  reset, vselect,
    hsync, vsync, 
    red, green, blue,
    pxlen, active,

    # ~~~~[PARAMETERS]~~~~
    resolution=(640, 480,),
    color_depth=(10, 10, 10,),
    refresh_rate=60,
    line_rate=31250
):
    """
    """
    # create the system-level signals, overwrite clock, reset
    glbl = Global(clock=clock, reset=reset)

    # VGA inteface
    vga = VGA()
    vga.assign(
        hsync=hsync, vsync=vsync,
        red=red, green=green, blue=blue,
        pxlen=pxlen, active=active
    )

    # video memory interface
    vmem = VideoMemory()
        
    # color bar generation
    bar_inst = color_bars(glbl, vmem, resolution=resolution)

    # VGA driver
    vga_inst = vga_sync(glbl, vga, vmem, resolution=resolution)

    return myhdl.instances()


def convert(color_depth=(10, 10, 10,)):
    """ convert the vgasys to verilog
    """
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=False)
    vselect = Signal(bool(0))

    hsync = Signal(bool(0))
    vsync = Signal(bool(0))
    cd = color_depth
    red = Signal(intbv(0)[cd[0]:])
    green = Signal(intbv(0)[cd[1]:])
    blue = Signal(intbv(0)[cd[2]:])
    pxlen = Signal(bool(0))
    active = Signal(bool(0))

    inst = mm_vgasys(
        clock, reset, vselect,
        hsync, vsync, red, green, blue,
        pxlen, active
    )
    tb_convert(inst)


if __name__ == '__main__':
    convert()
