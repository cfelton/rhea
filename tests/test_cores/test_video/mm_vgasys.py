
import myhdl
from myhdl import Signal, intbv


from rhea import Clock, Reset, Global
from rhea.cores.video import VGA
from rhea.cores.video import VideoMemory

from rhea.cores.video import vga_sync
from rhea.cores.video import color_bars


@myhdl.block
def mm_vgasys(

    # ~~~[PORTS]~~~
    clock,  reset, vselect,
    hsync, vsync, 
    red, green, blue,
    pxlen, active,

    # ~~~~[PARAMETERS]~~~~
    resolution=(640, 480,),
    color_depth=(8, 8, 8,),
    refresh_rate=60,
    line_rate=31250
    ):
    
    # create the system-level signals, overwrite clock, reset
    glbl = Global(clock=clock, reset=reset)

    # VGA interface
    vga = VGA()
    vga.assign(
        hsync=hsync, vsync=vsync,
        red=red, green=green, blue=blue,
        pxlen=pxlen, active=active
    )

    # video memory interface
    vmem = VideoMemory(color_depth=color_depth)
        
    # instances of modules
    bar_inst = color_bars(
        glbl, vmem, resolution=resolution, color_depth=color_depth
    )

    vga_inst = vga_sync(
        glbl, vga, vmem, resolution=resolution, refresh_rate=refresh_rate,
        line_rate=line_rate
    )

    return myhdl.instances()

 
def convert(color_depth=(8, 8, 8,)):
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
    inst.convert(hdl='Verilog', directory='output', timescale='1ns/1ns')


if __name__ == '__main__':
    convert()
