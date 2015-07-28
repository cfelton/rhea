#
# Copyright (c) 2014-2015 Christopher L. Felton
#

from __future__ import absolute_import
from myhdl import Signal, intbv
from ._memmap import MemMap

class Barebone(MemMap):
    """ Generic memory-mapped interface.

    This interface is the "generic" and most basic memory-map
    interface.  This can be used for common but also limited
    functionality.

    Timing Diagram
    ---------------
    clock  /--\__/--\__/--\__/--\__/--\__/--\__/--\__/--\__
    reset  /-----\_________________________________________
    wr     ____________/-----\_____________________________
    rd     _____________________________/------\___________
    ack    ___________________/----\___________/-----\_____
    rdat   -----------------------------|read data |-------
    wdat   ------------|write data |-----------------------
    addr   ------------\write addr |----|read addr |-------
    """
    def __init__(self, data_width=8, address_width=16):
        self.write = Signal(False)
        self.read = Signal(False)
        self.ack = Signal(False)
        self.rdata = Signal(intbv(0)[data_width:])
        self.wdata = Signal(intbv(0)[data_width:])
        self.addr = Signal(intbv(0)[address_width:])
        super(Barebone, self).__init__(data_width=data_width,
                                       address_width=address_width)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Transactors
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def write(self, addr, val):
        self._start_transaction(write=True, address=addr, data=val)
        self.write.next = True
        self.wdata.next = val
        to = 0
        while not self.ack and to < self.timeout:
            yield self.clock.posedge
            to += 1
        self.write.next = False
        self.wdata.next = 0
        self._end_transaction(self.wdata)

    def read(self, addr):
        self._start_transaction(write=False, address=addr)
        self.read.next = True
        to = 0
        while not self.ack and to < self.timeout:
            yield self.clock.posedge
            to += 1
        self.read.next = False
        self._end_transaction(self.rdata)

    def ack(self, data=None):
        self.ack.next = True
        if data is not None:
            self.rdata.next = data
        yield self.clock.posedge
        self.ack.next = False

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Modules
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def m_per_regfile(self, glbl, regfile, name, base_address=0):
        pass

    def m_controller(self, generic):
        self.write = generic.write
        self.read = generic.read
        self.wdata = generic.wdata
        self.addr = generic.addr
        generic.ack = self.ack
        generic.rdata = self.rdata

        return []

    def m_peripherial(self, generic):
        self.write = generic.write
        self.read = generic.read
        self.wdata = generic.wdata
        self.addr = generic.addr
        generic.ack = self.ack
        generic.rdata = self.rdata

        return []
