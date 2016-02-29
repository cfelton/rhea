
from myhdl import Signal, intbv


class SPIBus(object):
    def __init__(self, sck=None, mosi=None, miso=None, ss=None):
        if any([port is None for port in (sck, mosi, miso, ss)]):
            self.sck = Signal(True)
            self.mosi = Signal(True)
            self.miso = Signal(True)
            #self.ss = [Signal(True) for _ in range(8)]
            self.ss = Signal(intbv(0)[8:])
        else:
            self.sck = sck
            self.mosi = mosi
            self.miso = miso
            self.ss = ss

        # @todo: where/how is the following used?
        # make into an array
        self.csn = Signal(True)

