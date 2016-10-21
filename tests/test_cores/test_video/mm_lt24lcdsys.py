
import myhdl
from myhdl import Signal, intbv

from rhea import Global, Clock, Reset
from rhea.cores.video import VideoMemory
from rhea.cores.video import color_bars
from rhea.cores.video.lcd import LT24Interface
from rhea.cores.video.lcd import lt24lcd
from rhea.cores.misc import glbl_timer_ticks
from rhea.utils.test import tb_move_generated_files


@myhdl.block
def mm_lt24lcdsys(clock, reset,
    lcd_on, lcd_resetn, lcd_csn, lcd_rs,
    lcd_wrn, lcd_rdn, lcd_data):
    """
    """
    # interfaces
    glbl = Global(clock, reset)
    lcd = LT24Interface()
    resolution = lcd.resolution
    color_depth = lcd.color_depth
    refresh_rate = 60
    vmem = VideoMemory(resolution=resolution, color_depth=color_depth)

    # assign the ports to the interface
    lcd.assign(lcd_on, lcd_resetn, lcd_csn, lcd_rs, lcd_wrn,
               lcd_rdn, lcd_data)

    # simulation mode, reduce the dead time between real-world ticks
    # modules
    tck_inst = glbl_timer_ticks(glbl, user_timer=16, tick_div=100)
    bar_inst = color_bars(glbl, vmem, resolution=resolution,
                          color_depth=color_depth)
    lcd_inst = lt24lcd(glbl, vmem, lcd)

    return myhdl.instances()


def convert():
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=True)
    lcd_on = Signal(bool(0))
    lcd_resetn = Signal(bool(0))
    lcd_csn = Signal(bool(0))
    lcd_rs = Signal(bool(0))
    lcd_wrn = Signal(bool(0))
    lcd_rdn = Signal(bool(0))
    lcd_data = Signal(intbv(0)[16:])

    inst = mm_lt24lcdsys(
        clock, reset, lcd_on, lcd_resetn, lcd_csn, lcd_rs,
        lcd_wrn, lcd_rdn, lcd_data
    )

    inst.convert(hdl='Verilog', directory='output')

