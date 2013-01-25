#
# Copyright (c) 2006-2013 Christopher L. Felton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from myhdl import *
from fifo_mem import *

def fifo_two_port_sync(
    rst,
    clk,
    
    # FIFO A interface
    wra,     # Write strobe
    rda,     # Read strobe
    fulla,   # Fifo full (almost full)
    emptya,  # Fifo empty (almost empty)
    dia,     # Data in
    doa,     # Data out
    doa_vld, # Data out vld
    
    # FIFO B interface
    wrb,     # Write strobe
    rdb,     # Read strobe
    fullb,   # Fifo full (almost full)
    emptyb,  # Fifo empty 
    dib,     # Data in
    dob,     # Data out
    dob_vld, # Data out valid
    
    hwma = None,  # high water mark
    hwmb = None,  # high water mark
    
    # Parameters
    DSZ    = 8, # Data size, check dia, doa, dib, dob with DSZ
    ASZ    = 8, # Address size, size of the fifo 2**ASZ    
    C_HWMA = 0, # Fifo highwater mark (threshold), if FIFO count is greater
    C_HWMB = 0
    ):
    """
    The full and empty flags are active 1 cycle before the fifo is actually
    full or empty.  A read / write 1 cycle after full or empty.

    Timing Diagram:
    """
    nfulla  = Signal(False)
    nfullb  = Signal(False)
    aemptya = Signal(False)
    aemptyb = Signal(False)
    _fullb  = Signal(False)

    dcnta   = Signal(intbv(0)[ASZ:])
    dcntb   = Signal(intbv(0)[ASZ:])

    
    fifoA = fifo_sync(rst, clk, wra, rda, nfulla, emptya, fulla, aemptya,
                      dia, doa, doa_vld, dcnta,  DSZ, ASZ)
    
    fifoB = fifo_sync(rst, clk, wrb, rdb, nfullb, emptyb, _fullb, aemptyb,
                      dib, dob, dob_vld, dcntb, DSZ, ASZ)

    # @todo Need to review these fifo!! and the intended use.
    #    make it easier on the external fifos
    @always_comb
    def rtl_full():
        fullb.next = nfullb or _fullb
        
    if hwma is not None:
        _ihwma = fifo_hwm(clk, hwma, dcnta, C_HWMA)
 
    if hwmb is not None:
        _ihwmb = fifo_hwm(clk, hwmb, dcntb, C_HWMB)


    return instances()

def fifo_hwm(clk, hwm, dcnt, C_HWM):

    @always(clk.posedge)
    def rtl_hwm():
        if dcnt >= C_HWM:
            hwm.next = True
        else:
            hwm.next = False

    return rtl_hwm
             
def fifo_sync(
    rst,
    clk,

    wr,       # Write Strobe
    rd,       # Read Strobe
    full,     # Fifo Full
    empty,    # Fifo Empty
    afull,    # Almost Full
    aempty,   # Almost Empty
    din,      # Data in
    dout,     # Data out
    dout_vld, # Data out valid

    data_cnt=None, # Data count
    
    #  -- Parameters --
    DSZ=8,    # Data size
    ASZ=9     # Address size, FIFO size 2**ASZ
    ):
    """
    """

    wptr     = Signal(intbv(0)[ASZ:])
    wptr_p1  = Signal(intbv(0)[ASZ:])
    wptr_p2  = Signal(intbv(0)[ASZ:])
    rptr     = Signal(intbv(0)[ASZ:])
    _empty   = Signal(intbv(0)[2:])
    _rd      = Signal(False)
    _rptr_c  = Signal(intbv(0)[ASZ:])
    _rptr_d  = Signal(intbv(0)[ASZ:])
    _vld     = Signal(False)

    # Mainly debugging, can remove
    din_mem  = Signal(intbv(0)[DSZ:])
    dout_mem = Signal(intbv(0)[DSZ:])
    
    fmem = fifo_mem_generic(clk, wr, din_mem, dout_mem,
                            wptr, rptr, DSZ, ASZ)

    # Error with cver and verilog power operator, pre-compute
    ADDR_MOD = int(2**ASZ)

    @always(clk.posedge)
    def rtl_wr():
        if rst:
            wptr.next = 0
        else:
            if wr and wptr_p1 != rptr:
                wptr.next = (wptr + 1) % ADDR_MOD
            elif wr and wptr_p1 == rptr:
                print "SYNC FIFO DATA DROPPED"

    @always_comb
    def rtl_wr_p1():
        wptr_p1.next = (wptr + 1) % ADDR_MOD
        wptr_p2.next = (wptr + 2) % ADDR_MOD

    @always(clk.posedge)
    def rtl_d_rd():
        _rd.next     = rd
        _rptr_d.next = rptr
                        
    @always(clk.posedge)
    def rtl_rd():
        if rst:
            _rptr_c.next  = 0
            _vld.next  = False
        else:
            if rd and _rptr_c != wptr:
                _rptr_c.next  = (_rptr_c + 1) % ADDR_MOD
                _vld.next  = True
            else:
                _vld.next = False

            # Since the data is pipelined, if read falling edge rollback
            # the address pointer.
            if not rd and _rd:
                _rptr_c.next = _rptr_d

    @always_comb
    def rtl_rd_pointer():
        if rd:
            rptr.next = _rptr_c
        else:
            rptr.next = _rptr_d
            
    # The fifo_mem output is registered (delayed one clock) delay the
    # empty signal by one
    @always(clk.posedge)
    def rtl_e():
        if rptr == wptr:
            empty.next  = True
            _empty.next = 0
        else:
            if _empty == 0:
                _empty.next = 1
            elif _empty == 1:
                _empty.next = 2
            else:
                _empty.next = 3
                empty.next  = False


    @always(clk.posedge)
    def rtl_ae():
        if (rptr+1) == wptr or empty:
            aempty.next = True
        else:
            aempty.next = False
            
    @always_comb
    def rtl_f():
        if wptr_p1 == rptr:
            full.next = True
        else:
            full.next = False

    @always_comb
    def rtl_af():
        if wptr_p2 == rptr or full:
            afull.next = True
        else:
            afull.next = False


    @always_comb
    def rtl_dio():
        dout.next     = dout_mem
        din_mem.next  = din
        dout_vld.next = _vld & rd

    if data_cnt is not None:
        @always_comb
        def rtl_data_cnt():
            data_cnt.next = (wptr - rptr) % ADDR_MOD

                
    return instances()
                
    
              
