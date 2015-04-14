
from __future__ import absolute_import

from mn.system.memmap._memmap import MemMap

class Barebone(MemMap):
    def __init__(self, data_width=8, address_width=16):
        self.wr = Signal(False)
        self.rd = Signal(False)
        self.ack = Signal(False)
        self.rdat = Signal(intbv(0)[data_width:])
        self.wdat = Signal(intbv(0)[data_width:])
        self.addr = Signal(intbv(0)[address_width:])
        super(Barebone, self).__init__(data_width=data_width,
                                       address_width=address_width) 

        