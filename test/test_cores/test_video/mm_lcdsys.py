
from myhdl import Signal, intbv

from rhea.system import Clock, Reset, Global
from rhea.cores.video import VideoMemory
from rhea.cores.video import color_bars
from rhea.cores.video.lcd import LT24Interface
from rhea.cores.video.lcd import lt24lcd


def mm_lcdsys(clock, reset,
              lcd_on, lcd_resetn, lcd_csn, lcd_rs,
              lcd_wrn, lcd_rdn, lcd_data):
    """

    :param clock:
    :param reset:
    :param lcd_on:
    :param lcd_resetn:
    :param lcd_csn:
    :param lcd_rs:
    :param lcd_wrn:
    :param lcd_rdn:
    :param lcd_data:
    :return:
    """
    resolution = (240, 320)
    refresh_rate = 60

    # interfaces
    glbl = Global(clock, reset)
    vmem = VideoMemory(resolution=resolution, color_depth=(5, 6, 5))
    lcd = LT24Interface()
    # assign the ports to the interface
    lcd.assign(lcd_on, lcd_resetn, lcd_csn, lcd_rs, lcd_wrn, lcd_rdn, lcd_data)

    # modules
    gbar = color_bars(glbl, vmem, resolution=resolution)
    glcd = lt24lcd(glbl, vmem, lcd)

    return gbar, glcd
