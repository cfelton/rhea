
from myhdl import Signal, intbv


class LT24Interface(object):
    def __init__(self):
        """
        """
        self.on = Signal(bool(0))
        self.resetn = Signal(bool(0))
        self.csn = Signal(bool(0))
        self.dcn = Signal(bool(0))
        self.wrn = Signal(bool(0))
        self.rdn = Signal(bool(0))
        self.data = Signal(intbv(0)[16:])

    def assign(self, on, resetn, csn, rs, wrn, rdn, data):
        self.on = on
        self.resetn = resetn
        self.csn = csn
        self.dcn = rs
        self.wrn = wrn
        self.rdn = rdn
        self.data = data


