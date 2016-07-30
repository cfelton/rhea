
import myhdl
from myhdl import Signal, intbv, ResetSignal, always

from rhea.system import Global, Clock, Reset
from rhea.cores.video import VGA, VideoMemory
from rhea.cores.video import vga_sync, color_bars
from rhea.utils.test import tb_convert


@myhdl.block
def xula_vga(
    # ~~~[PORTS]~~~
    vselect,
    hsync, vsync, 
    red, green, blue,
    pxlen, active,
    clock,
    reset=None,

    # ~~~~[PARAMETERS]~~~~
    # @todo: replace these parameters with a single VGATimingParameter
    resolution=(640, 480,),
    color_depth=(8, 8, 8,),
    refresh_rate=60,
    line_rate=31250
):
    """
    (arguments == ports)
    Arguments:
        vselect:

    Parameters:
        resolution: the video resolution
        color_depth: the color depth of a pixel, the number of bits
            for each color component in a pixel.
        refresh_rate: the refresh rate of the video
    """
    # stub out reset if needed
    if reset is None:
        reset = ResetSignal(0, active=0, async=False)

        @always(clock.posedge)
        def reset_stub():
            reset.next = not reset.active

    else:
        reset_stub = None

    # create the system-level signals, overwrite clock, reset
    glbl = Global(clock=clock, reset=reset)

    # VGA inteface
    vga = VGA()
    # assign the top-level ports to the VGA interface
    vga.assign(
        hsync=hsync, vsync=vsync,
        red=red, green=green, blue=blue,
        pxlen=pxlen, active=active
    )

    # video memory interface
    vmem = VideoMemory(color_depth=color_depth)
        
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

    inst = xula_vga(
        clock, reset, vselect,
        hsync, vsync, red, green, blue,
        pxlen, active
    )
    tb_convert(inst)


if __name__ == '__main__':
    convert()

