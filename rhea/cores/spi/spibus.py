
from myhdl import Signal, intbv, delay
from rhea.system import Clock

class SPIBus(object):
    def __init__(self, sck=None, mosi=None, miso=None, ss=None):
        """
        """
        self.htck = 234
        if any([port is None for port in (sck, mosi, miso, ss)]):
            self.sck = Clock(0, frequency=100e3)
            self.mosi = Signal(True)
            self.miso = Signal(True)
            self.ss = Signal(intbv(0xFF)[8:])
        else:
            self.sck = sck
            self.mosi = mosi
            self.miso = miso
            self.ss = ss

        # @todo: where/how is the following used?
        # make into an array
        self.csn = Signal(True)

        # for simulation and modeling only
        self.outval = intbv(0)[8:]
        self.inval = intbv(0)[8:]

    def _set_ss(self):
        pass

    def writeread(self, val):
        htck = self.htck
        self.outval[:] = val
        self.csn.next = False
        yield delay(htck//2)
        for ii in range(7, -1, -1):
            self.sck.next = False
            self.mosi.next = self.outval[ii]
            yield delay(htck)
            self.sck.next = True
            yield delay(3)
            self.inval[ii] = self.miso
            yield delay(htck-3)

        self.csn.next = True
        yield delay(htck)

    def get_read_data(self):
        return int(self.inval)

    def get_write_data(self):
        return int(self.outval)


