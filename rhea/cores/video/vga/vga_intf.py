
from myhdl import *


class VGA:
    def __init__(self, color_depth=(10, 10, 10,)):
        """
        color_depth the number of bits per RGB
        """
        self.N = color_depth

        # the sync signals
        self.hsync = Signal(bool(1))
        self.vsync = Signal(bool(1))
        # the RGB signals to the video
        cd = color_depth
        self.red = Signal(intbv(0)[cd[0]:])
        self.green = Signal(intbv(0)[cd[1]:])
        self.blue = Signal(intbv(0)[cd[2]:])

        # logic VGA timing signals, used internally only
        self.pxlen = Signal(bool(0))
        self.active = Signal(bool(0))

        # these are used for verification.
        self.States = enum('NONE', 'ACTIVE',
                           'HOR_FRONT_PORCH', 'HSYNC', 'HOR_BACK_PORCH',
                           'VER_FRONT_PORCH', 'VSYNC', 'VER_BACK_PORCH')
        self.state = Signal(self.States.ACTIVE)

    def assign(self, hsync, vsync, red, green, blue, pxlen, active):
        """ in some cases discrete signals are connected """
        self.hsync = hsync
        self.vsync = vsync
        self.red = red
        self.green = green
        self.blue = blue
        self.pxlen = pxlen
        self.active = active
