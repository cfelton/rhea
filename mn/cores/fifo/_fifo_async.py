#
# Copyright (c) 2006-2014 Christopher L. Felton
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

from math import log, ceil

from myhdl import *

from _fifo_mem import m_fifo_mem_generic
from _fifo_syncers import *
from _fifo_intf import check_fifo_intf
from _fifo_intf import _fifobus

def m_fifo_async(reset, wclk, rclk, fbus):
    """
    The following is a general purpose, platform independent 
    asynchronous FIFO (dual clock domains).

    Cross-clock boundrary FIFO, based on: 
    "Simulation and Synthesis Techniques for Asynchronous FIFO Design"

    Typically in the "mn" package the FIFOBus interface is used to 
    describe 
    Timing:
    """

    # verify that the "interface" passed has the required Signals
    # (attributes).
    check_fifo_intf(fbus)

    # for simplification the memory size is forced to a power of 
    # two - full address range, ptr (mem indexes) will wrap
    Asz = int(ceil(log(fbus.size, 2)))
    
    # an extra bit is used to determine full vs. empty (see paper)
    waddr = Signal(modbv(0)[Asz:])
    raddr = Signal(modbv(0)[Asz:])
    wptr = Signal(modbv(0)[Asz+1:])
    rptr = Signal(modbv(0)[Asz+1:])
    wq2_rptr = Signal(intbv(0)[Asz+1:])
    rq2_wptr = Signal(intbv(0)[Asz+1:])

    wfull = Signal(bool(0))
    rempty = Signal(bool(1))

    # sync'd resets, the input reset is more than likely sync'd to one
    # of the clock domains, sync both regardless ...
    wrst = ResetSignal(reset.active, active=reset.active, async=reset.async)
    rrst = ResetSignal(reset.active, active=reset.active, async=reset.async)

    # @todo: if ResetSignal use the active attribute to determine 
    #        if 'not reset' or 'reset'.  If the active==0 then 
    #        set invert=False
    gs1 = m_sync_rst(wclk, reset, wrst)
    gs2 = m_sync_rst(rclk, reset, rrst)

    gs3 = m_sync_mbits(wclk, wrst, rptr, wq2_rptr)
    gs4 = m_sync_mbits(rclk, rrst, wptr, rq2_wptr)

    @always_comb
    def rtl_assigns():
        fbus.empty.next = rempty
        fbus.full.next = wfull

    _we = Signal(bool(0))
    @always_comb
    def rtl_wr():
        _we.next = fbus.wr and not fbus.full
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Memory for the FIFO
    g_fifomem = m_fifo_mem_generic(wclk, _we, fbus.wdata, waddr,
                                   rclk, fbus.rdata,  raddr,
                                   mem_size=fbus.size)


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # --Text from the paper--
    # The read pointer is a dual nbit Gray code counter.  The nbit 
    # pointer (rptr) is passed to the write clock domain through the 
    # syncs.  The (n-1)bit pointer (raddr) is used to address the FIFO 
    # buffer.  The FIFO empty output is registered and is asserted on 
    # the next rising rclk edge when the next rptr value equals the 
    # sync wptr value. 
    rbin = Signal(modbv(0)[Asz+1:])
    #raddr.assign(rbin[Asz:0]

    @always_seq(rclk.posedge, reset=rrst)
    def rtl_rptrs():
        # increment when read and not empty 
        rbn = rbin + (fbus.rd and not rempty)
        rbin.next = rbn
        rpn = (rbn >> 1) ^ rbn  # gray counter
        rptr.next = rpn   

        # FIFO empty when the next rptr == sync'd wptr or on reset
        rempty.next = (rpn == rq2_wptr)

        # the data is register from the memory, the data is delayed
        fbus.rvld.next = fbus.rd and not rempty
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # --Text from the paper--
    # The write pointer is a dual nbit gray code conter.  The nbit 
    # pointer (wptr) is passed to the read clock domain through the 
    # sync'ers.  The (n-1)-bit pointer (waddr) is used ot address the
    # FIFO buffer.  The FIFO full asserted when the next modified 
    # value equals the sync'd and modified wrptr2 value (except MSBs).
    wbin = Signal(modbv(0)[Asz+1:])
    #waddr.assign(wbin[Asz:0])

    @always_seq(wclk.posedge, reset=wrst)
    def rtl_wptrs():
        # increment when write and not full
        wbn = wbin + (fbus.wr and not wfull)
        wbin.next = wbn
        wpn = (wbn >> 1) ^ wbn
        wptr.next = wpn

        # the dillio with the full determination ...
        wfull.next = (wpn == concat(~wq2_rptr[Asz+1:Asz-1],
                                    wq2_rptr[Asz-1:0]))
    
    
    @always_comb
    def rtl_addrs():
        waddr.next = wbin[Asz:0]
        raddr.next = rbin[Asz:0]


    return instances()

m_fifo_async.fbus_intf = _fifobus