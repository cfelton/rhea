from __future__ import division, print_function

from myhdl import *

from rhea.system import Barebone
from . import SPIBus


def spi_controller_model(clock, ibus, spibus):
    """

      ibus   : internal bus
      spibus : SPI interface (SPIBus)
    """
    assert isinstance(ibus, Barebone)
    assert isinstance(spibus, SPIBus)

    @instance
    def decode_ibus():
        while True:
            yield clock.posedge

            if ibus.write:
                yield spibus.writeread(ibus.get_write_data())
                yield ibus.acktrans(spibus.get_read_data())
            elif ibus.read:
                yield spibus.writeread(0x55)  # dummy write byte
                yield ibus.acktrans(spibus.get_read_data())

    return decode_ibus


class SPISlave(object):
    def __init__(self):
        self.reg = intbv(0)[8:]

    def process(self, spibus):
        mosi = spibus.mosi
        miso = spibus.miso
        sck = spibus.sck
        csn = spibus.csn

        @instance
        def gproc():
            while True:
                yield csn.negedge
                bcnt = 8
                while not csn:
                    if bcnt > 0:
                        miso.next = self.reg[bcnt-1]
                        yield sck.posedge
                        bcnt -= bcnt
                        self.reg[bcnt] = mosi
                    else:
                        yield delay(10)

        return gproc