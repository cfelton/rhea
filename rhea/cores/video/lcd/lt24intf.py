
from myhdl import Signal, intbv


class LT24Interface(object):
    def __init__(self, resolution=(240, 320)):
        """
        The resolution for the terasic LT24 is 240x320, the resolution
        argument is to supoort simulation and testing (short sim times).
        """
        self.resolution = res = resolution
        self.number_of_pixels = res[0] * res[1]
        self.color_depth = (5, 6, 5)

        self.on = Signal(bool(0))
        self.resetn = Signal(bool(1))
        self.csn = Signal(bool(1))
        self.dcn = Signal(bool(1))
        self.wrn = Signal(bool(1))
        self.rdn = Signal(bool(1))
        self.data = Signal(intbv(0)[16:])

    def assign(self, on, resetn, csn, rs, wrn, rdn, data):
        self.on = on
        self.resetn = resetn
        self.csn = csn
        self.dcn = rs
        self.wrn = wrn
        self.rdn = rdn
        self.data = data


