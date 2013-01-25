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
from fifo_mem import fifo_mem_generic

def fifo_async(
    reset,     # global reset

    wclk,      # write clock domain
    winc,      # write strobe
    wfull,     # write full
    wdata,     # write data

    rclk,      # read clock domain
    rinc,      # read strobe
    rempty,    # read empty
    prempty,   # going to be empty
    rdata,     # read data
    rvld,      # read data valid
    
    C_DSZ = 8, # data size, byte storage
    C_ASZ = 4  # address size, 2^4 16 byte FIFO
    ):
    """
    Cross clock boundrary FIFO.  Based on
      \"Simulation and Synthesis Techniques for Asynchronous FIFO design
        with Asynchronouos Pointer Comparisons\".
    """

    wptr  = Signal(intbv(0)[C_ASZ:])
    rptr  = Signal(intbv(0)[C_ASZ:])

    aempty_n   = Signal(False)
    afull_n    = Signal(False)
    p_aempty_n = Signal(False)

    wrst_n = Signal(False)
    rrst_n = Signal(False)


    @always_comb
    def rtl_resets():
        wrst_n.next = not reset
        rrst_n.next = not reset
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # --Text from the paper--
    # This is an asynchronous pointer-comparison module that
    # is used to generate signals that control assertions of the
    # asynchronous "full" and "empty" status bits.  This module
    # only contains combinational comparison logic.  No sequential
    # logic is included.
    direction = Signal(False)
    dirset_n  = Signal(False)
    dirclr_n  = Signal(False)
    high      = Signal(True)

    wrm  = Signal(False)
    wrl = Signal(False)
    
    N = C_ASZ-1

    # generate the quadrant changes
    @always_comb
    def rtl_asycn_quad():
        wrm.next = wptr[N] ^ rptr[N-1]
        wrl.next = wptr[N-1] ^ rptr[N]
        
    @always_comb
    def rtl_async_cmp_dir():
        high.next = True
        
        #dirset_n.next = ~( (wptr[N]^rptr[N-1]) & ~(wptr[N-1]^rptr[N]) )
        if wrm and not wrl:
            dirset_n.next = False
        else:
            dirset_n.next = True
                    
        ##dirclr_n.next = ~(( ~(wptr[N]^rptr[N-1]) & (wptr[N-1]^rptr[N])) | ~wrst_n)
        if (not wrm and wrl) or not wrst_n:
            dirclr_n.next = False
        else:
            dirclr_n.next = True

        if (wptr-1) == rptr and not direction:
            p_aempty_n.next = False
        else:
            p_aempty_n.next = True

        if (wptr == rptr) and not direction:
            aempty_n.next = False
        else:
            aempty_n.next = True

        if (wptr == rptr) and direction:
            afull_n.next = False
        else:
            afull_n.next = True
        
    # little work to get a RS-FF to synthesize
    @always(wclk.posedge, dirset_n.negedge, dirclr_n.negedge)
    def rtl_async_cmp():
        if not dirclr_n:
            direction.next = False
        elif not dirset_n:
            direction.next = True
        else:
            if not high:
                direction.next = high

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Memory for the FIFO
    FIFOMEM = fifo_mem_generic(wclk, winc, wdata, wptr,
                               rclk, rdata,  rptr,
                               DSZ=C_DSZ, ASZ=C_ASZ)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # --Text from the paper--
    # This module is mostly synchronous to the read-clock.
    # domain and contains the FIFO read pointer and empty-flag
    # logic.  Assertion of the aempty_n signal (an input to 
    # this module) is synchronous to the rclk-domain, since aempty_n 
    # can only be asserted when the rptr incremented, but de-assertion
    # of the aempty_n signal happens when the wptr increments, which
    # is asynchronous to rclk.
    rbin    = Signal(intbv(0)[C_ASZ:])
    rgnext  = Signal(intbv(0)[C_ASZ:])
    rbnext  = Signal(intbv(0)[C_ASZ:])
    rempty2 = Signal(False)
    
    # gray style pointer
    @always(rclk.posedge, rrst_n.negedge)
    def rtl_rptr_bin():
        if not rrst_n:
            rbin.next = 0
            rptr.next = 0
        else:
            rbin.next = rbnext
            rptr.next = rgnext

    @always_comb
    def rtl_rptr_inc():
        if not rempty and rinc:
            rbnext.next = (rbin + 1) % 2**C_ASZ
        else:
            rbnext.next = rbin

    @always_comb
    def rtl_rptr_gray():
        # binary-to-gray conversion
        rgnext.next = (rbnext>>1) ^ rbnext

    @always(rclk.posedge, aempty_n.negedge)
    def rtl_rptr_empty():
        if not aempty_n:
            rempty.next  = True
            rempty2.next = True
        else:
            rempty.next  = rempty2
            rempty2.next = not aempty_n


    _rvld1  = Signal(False)
    _rempty = Signal(False)

    @always(rclk.posedge)
    def rtl_rd_vld():
        _rvld1.next  =  rinc
        _rempty.next = rempty;
        
    @always_comb
    def rtl_rd_vldo():
        rvld.next = _rvld1 and not _rempty
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # --Text from the paper--
    # This module is mostly synchronous to the write-clock domain
    # and contains the FIFO write pointer and full-flag logic.  Assertion
    # of the afull_n signal (an input to this module) is syncronous to
    # the wclk domain, since afull_n can only be asserted when the 
    # wptr incremented (and wrst_n), but deassertion of the afull_n 
    # signal happens when the rptr increments, whichis asynchronous to wclk.
    wbin   = Signal(intbv(0)[C_ASZ:])
    wgnext = Signal(intbv(0)[C_ASZ:])
    wbnext = Signal(intbv(0)[C_ASZ:])
    wfull2 = Signal(False)

    @always(wclk.posedge, wrst_n.negedge)
    def rtl_wptr_bin():
        if not wrst_n :
            wbin.next = 0
            wptr.next = 0
        else:
            wbin.next = wbnext
            wptr.next = wgnext

    @always_comb
    def rtl_wptr_inc():
        if not wfull and winc:
            wbnext.next = (wbin + 1) % 2**C_ASZ
        else:
            wbnext.next = wbin


    @always_comb
    def rtl_wptr_gray():
        wgnext.next = (wbnext>>1) ^ wbnext

    @always(wclk.posedge, wrst_n.negedge, afull_n.negedge)
    def rtl_wptr_full():
        if not wrst_n:
            wfull.next  = False
            wfull2.next = False
        elif not afull_n:
            wfull.next  = True
            wfull2.next = True
        else:
            wfull.next  = wfull2
            wfull2.next = not afull_n
        
    return instances()
    
