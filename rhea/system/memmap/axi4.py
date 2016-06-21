
from __future__ import absolute_import

from math import log, ceil

import myhdl
from myhdl import Signal, intbv, always_seq
from . import MemoryMapped


class AXI4Lite(MemoryMapped):
    def __init__(self, glbl, data_width=8, address_width=16):
        """ 
        """
        super(AXI4Lite, self).__init__(glbl,
                                       data_width=data_width,
                                       address_width=address_width) 
        self.aclk = glbl.clock
        # not used, use
        # self.aresetn = glbl.reset
        
        self.awaddr = Signal(intbv(0)[address_width:])
        self.awprot = Signal(intbv(0)[3:])
        self.awvalid = Signal(bool(0))
        self.awready = Signal(bool(0))
        
        self.wdata = Signal(intbv(0)[data_width:])
        num_strb_bits = int(ceil(data_width/8))
        self.wstrb = Signal(intbv(0)[num_strb_bits:])
        self.wvalid = Signal(bool(0))
        self.wready = Signal(bool(0))
        
        self.bresp = Signal(intbv(0)[2:])
        self.bvalid = Signal(bool(0))
        self.bready = Signal(bool(0))
        
        self.araddr = Signal(intbv(0)[address_width:])
        self.arprot = Signal(intbv(0)[3:])
        self.arvalid = Signal(bool(0))
        self.arready = Signal(bool(0))
        
        self.rdata = Signal(intbv(0)[data_width:])
        self.rresp = Signal(intbv(0)[2:])
        self.rvalid = Signal(bool(0))
        self.rready = Signal(bool(0))
        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Transactors
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~        
    def writetrans(self, addr, val):
        """ Emulate a write transfer from a master
        The following is a very basic write transaction, future 
        enhancements are needed to verify/validate of features of 
        the AXI4Lite bus. 
        
        @todo: add priority  (not often used)
        @todo: add byte strobe
        @todo: add response checks
        @todo: and checks for all channel acks
        """
        self.awaddr.next = addr 
        self.awvalid.next = True
        self.wdata.next = val 
        self.wvalid.next = True 
        self.bready.next = True 
        tickcount = 0
        yield self.aclk.posedge
        while not self.wready and tickcount < self.timeout:
            yield self.aclk.posedge
            tickcount += 1 
        self.awvalid.next = False 
        self.wvalid.next = False 
        self.bready.next = False 
    
    def readtrans(self, addr):
        pass
    
    def acktrans(self, data=None):
        pass
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Modules
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def map_generic(self):
        pass

    @myhdl.block
    def peripheral_regfile(self, glbl, regfile, name):
        clock, reset = glbl.clock, glbl.reset
        readtrans = Signal(bool(0))
        writetrans = Signal(bool(0))
        
        # @todo: incomplete finish
        @always_seq(clock.posedge, reset=reset)
        def beh_row():
            if self.awvalid:
                writetrans.next = True
            
            if self.arvalid:
                readtrans.next = True
                
        return beh_row
    
    def controller(self, generic):
        pass
    
    def peripheral(self, generic):
        pass 
    
    


