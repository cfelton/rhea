
from myhdl import Signal,intbv

class SPIBus(object):
    def __init__(self):
        self.sck = Signal(True)
        self.mosi = Signal(True)
        self.miso = Signal(True)
        #self.ss = [Signal(True) for _ in range(8)]
        self.ss = Signal(intbv(0)[8:])
        # make into an array
        self.csn = Signal(True)
