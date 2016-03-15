
from myhdl import *


class VGA:
    def __init__(
        self, 
        hsync=None, vsync=None,
        red=None, green=None, blue=None,
        pxlen=None, active=None,
        color_depth=(10, 10, 10,)
    ):
        """
        color_depth the number of bits per RGB
        """
        self.N = color_depth

        # the sync signals
        self.hsync = Signal(bool(1)) if hsync is None else hsync
        self.vsync = Signal(bool(1)) if vsync is None else vsync
        # the RGB signals to the video
        cd = color_depth
        self.red = Signal(intbv(0)[cd[0]:]) if red is None else red
        self.green = Signal(intbv(0)[cd[1]:]) if green is None else green
        self.blue = Signal(intbv(0)[cd[2]:]) if blue is None else blue

        # logic VGA timing signals, used internally only
        self.pxlen = Signal(bool(0)) if pxlen is None else pxlen
        self.active = Signal(bool(0)) if active is None else active

        # these are used for verification.
        self.States = enum('NONE', 'ACTIVE',
                           'HOR_FRONT_PORCH', 'HSYNC', 'HOR_BACK_PORCH',
                           'VER_FRONT_PORCH', 'VSYNC', 'VER_BACK_PORCH')
        self.state = Signal(self.States.ACTIVE)  
