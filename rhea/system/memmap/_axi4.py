
from __future__ import absolute_import

from myhdl import Signal, intbv

from .. import Clock
from .. import Reset
from . import MemMap

class AXI4(MemMap):
    def __init__(self, glbl, data_width=8, address_width=16):

        # @todo: get clock and reset from global
        self.aclk = Clock(0)
        self.aresetn = Reset(0, active=0, async=False)

        self.awid = Signal(intbv(0)[4:0])
        self.awvalid = Signal(bool(0))

        super(AXI4, self).__init__(data_width=data_width,
                                   address_width=address_width) 
