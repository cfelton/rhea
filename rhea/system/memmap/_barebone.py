#
# Copyright (c) 2014-2015 Christopher L. Felton
#

from __future__ import absolute_import

from math import log, ceil
from myhdl import Signal, intbv
from ._memmap import MemMap


class Barebone(MemMap):
    """ Generic memory-mapped interface.

    This interface is the "generic" and most basic memory-map
    interface.  This can be used for common but also limited
    functionality.

    Timing Diagram
    ---------------
    clock       /--\__/--\__/--\__/--\__/--\__/--\__/--\__/--\__
    reset       /-----\_________________________________________
    write       ____________/-----\_____________________________
    read        _____________________________/------\___________
    ack         ___________________/----\___________/-----\_____
    done        ------------\______/---------\______/-----------
    read_data   -----------------------------|read data |-------
    write_data  ------------|write data |-----------------------
    per_addr
    reg_addr    ------------\write addr |----|read addr |-------

    @todo: replace 'ack' with 'done'
    """
    def __init__(self, num_peripherals=16, data_width=8, address_width=8):
        self.write = Signal(bool(0))
        self.read = Signal(bool(0))
        # @todo: replace "ack" with "done" (?)
        self.ack = Signal(bool(0))
        self.done = Signal(bool(0))
        self.read_data = Signal(intbv(0)[data_width:])
        self.write_data = Signal(intbv(0)[data_width:])

        # separate address bus for selecting a peripheral and the register
        # addresses.  The total number of peripherals is num_periphal-1,
        # the max address (all 1s) is reserved to indicate "done" (idle)
        pwidth = int(ceil(log(num_peripherals, 2)))
        self.per_addr = Signal(intbv(0)[pwidth:])
        self.reg_addr = Signal(intbv(0)[address_width:])
        super(Barebone, self).__init__(data_width=data_width,
                                       address_width=address_width)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Transactors
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def write(self, addr, val):
        self._start_transaction(write=True, address=addr, data=val)
        self.write.next = True
        self.write_data.next = val
        to = 0
        while not self.ack and to < self.timeout:
            yield self.clock.posedge
            to += 1
        self.write.next = False
        self.write_data.next = 0
        self._end_transaction(self.write_data)

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
    def map_generic(self, generic):
        self.write = generic.write
        self.read = generic.read
        self.wdata = generic.wdata
        self.addr = generic.addr
        generic.ack = self.ack
        generic.rdata = self.rdata
        return []

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

    def m_peripheral(self, generic):
        self.write = generic.write
        self.read = generic.read
        self.wdata = generic.wdata
        self.addr = generic.addr
        generic.ack = self.ack
        generic.rdata = self.rdata

        return []
