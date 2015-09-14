
from __future__ import division

"""
This module contains a video driver for the terasic LT24
LCD display ...
"""

from myhdl import Signal, intbv

from ._lt24intf import LT24Interface


def lt24lcd(glbl, vmem, lcd):
    """
    RGB 5-6-5 (8080-system 16bit parallel bus)
    """
    assert isinstance(lcd, LT24Interface)
    resolution = (240, 320)
    refresh_rate = 60

    # write out a new VMEM to the LCD display, a write cycle
    # consists of putting the video data on the bus and latching
    # with the `wrx` signal.  Init (write once) the column and
    # page addresses (cmd = 2A, 2B) then write mem (2C)

