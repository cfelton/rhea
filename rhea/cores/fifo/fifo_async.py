#
# Copyright (c) 2006-2014 Christopher L. Felton
#

from __future__ import absolute_import

from math import log, ceil

import myhdl
from myhdl import *

from rhea.system import FIFOBus
from .fifo_mem import fifo_mem_generic
from .fifo_syncers import *
from .fifo_intf import check_fifo_intf


def fifo_async(reset, wclk, rclk, fbus):
    """
    The following is a general purpose, platform independent 
    asynchronous FIFO (dual clock domains).

    Cross-clock boundary FIFO, based on:
    "Simulation and Synthesis Techniques for Asynchronous FIFO Design"

    Typically in the "mn" package the FIFOBus interface is used to 
    describe 
    Timing:
    """
    # @todo: use the clock_write and clock_read from the FIFOBus
    # @todo: interface, make this interface compliant with the
    # @todo: fifos: fifo_async(reset, clock, fifobus)

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
    gs1 = sync_reset(wclk, reset, wrst)
    gs2 = sync_reset(rclk, reset, rrst)

    gs3 = sync_mbits(wclk, wrst, rptr, wq2_rptr)
    gs4 = sync_mbits(rclk, rrst, wptr, rq2_wptr)

    @always_comb
    def rtl_assigns():
        fbus.empty.next = rempty
        fbus.full.next = wfull

    _we = Signal(bool(0))

    @always_comb
    def rtl_wr():
        _we.next = fbus.write and not fbus.full
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Memory for the FIFO
    g_fifomem = fifo_mem_generic(wclk, _we, fbus.write_data, waddr,
                                 rclk, fbus.read_data,  raddr,
                                 mem_size=fbus.size)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # --Text from the paper--
    # The read pointer is a dual nbit Gray code counter.  The nbit 
    # pointer (rptr) is passed to the write clock domain through the 
    # syncs.  The (n-1)bit pointer (raddr) is used to address the FIFO 
    # buffer.  The FIFO empty output is registered and is asserted on 
    # the next rising rclk edge when the next rptr value equals the 
    # sync wptr value. 
    rbin = Signal(modbv(0)[Asz+1:])
    # raddr.assign(rbin[Asz:0]

    @always_seq(rclk.posedge, reset=rrst)
    def rtl_rptrs():
        # increment when read and not empty 
        rbn = rbin + (fbus.read and not rempty)
        rbin.next = rbn
        rpn = (rbn >> 1) ^ rbn  # gray counter
        rptr.next = rpn   

        # FIFO empty when the next rptr == sync'd wptr or on reset
        rempty.next = (rpn == rq2_wptr)

        # the data is register from the memory, the data is delayed
        fbus.read_valid.next = fbus.read and not rempty
        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # --Text from the paper--
    # The write pointer is a dual nbit gray code conter.  The nbit 
    # pointer (wptr) is passed to the read clock domain through the 
    # sync'ers.  The (n-1)-bit pointer (waddr) is used ot address the
    # FIFO buffer.  The FIFO full asserted when the next modified 
    # value equals the sync'd and modified wrptr2 value (except MSBs).
    wbin = Signal(modbv(0)[Asz+1:])
    # waddr.assign(wbin[Asz:0])

    @always_seq(wclk.posedge, reset=wrst)
    def rtl_wptrs():
        # increment when write and not full
        wbn = wbin + (fbus.write and not wfull)
        wbin.next = wbn
        wpn = (wbn >> 1) ^ wbn
        wptr.next = wpn

        # what the dillio with the full determination ...
        wfull.next = (wpn == concat(~wq2_rptr[Asz+1:Asz-1],
                                    wq2_rptr[Asz-1:0]))    
    
    @always_comb
    def rtl_addrs():
        waddr.next = wbin[Asz:0]
        raddr.next = rbin[Asz:0]

    return myhdl.instances()


fifo_async.fbus_intf = FIFOBus