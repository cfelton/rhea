#
# Copyright (c) 2006-2014 Christopher L. Felton
# See the licence file in the top directory
#

from __future__ import absolute_import

from math import log, ceil

import myhdl
from myhdl import (Signal, ResetSignal, intbv, modbv, concat,
                   always_comb, always_seq,)

from rhea.system import FIFOBus
from .fifo_mem import fifo_mem
from .fifo_syncers import sync_reset, sync_mbits


@myhdl.block
def fifo_async(clock_write, clock_read, fifobus, reset, size=128):
    """
    The following is a general purpose, platform independent 
    asynchronous FIFO (dual clock domains).

    Cross-clock boundary FIFO, based on:
    "Simulation and Synthesis Techniques for Asynchronous FIFO Design"

    Typically in the "rhea" package the FIFOBus interface is used to
    interface with the FIFOs
    """
    # @todo: use the clock_write and clock_read from the FIFOBus
    # @todo: interface, make this interface compliant with the
    # @todo: fifos: fifo_async(reset, clock, fifobus)

    # for simplification the memory size is forced to a power of 
    # two - full address range, ptr (mem indexes) will wrap
    asz = int(ceil(log(size, 2)))
    fbus = fifobus   # alias
    
    # an extra bit is used to determine full vs. empty (see paper)
    waddr = Signal(modbv(0)[asz:])
    raddr = Signal(modbv(0)[asz:])
    wptr = Signal(modbv(0)[asz+1:])
    rptr = Signal(modbv(0)[asz+1:])
    wq2_rptr = Signal(intbv(0)[asz+1:])
    rq2_wptr = Signal(intbv(0)[asz+1:])

    wfull = Signal(bool(0))
    rempty = Signal(bool(1))

    # sync'd resets, the input reset is more than likely sync'd to one
    # of the clock domains, sync both regardless ...
    wrst = ResetSignal(reset.active, active=reset.active, async=reset.async)
    rrst = ResetSignal(reset.active, active=reset.active, async=reset.async)

    # @todo: if ResetSignal use the active attribute to determine 
    #        if 'not reset' or 'reset'.  If the active==0 then 
    #        set invert=False
    sr1_inst = sync_reset(clock_write, reset, wrst)
    sr2_inst = sync_reset(clock_read, reset, rrst)

    mb1_inst = sync_mbits(clock_write, wrst, rptr, wq2_rptr)
    mb2_inst = sync_mbits(clock_read, rrst, wptr, rq2_wptr)

    @always_comb
    def beh_assigns():
        fbus.empty.next = rempty
        fbus.full.next = wfull

    _we = Signal(bool(0))
    _re = Signal(bool(0))

    @always_comb
    def beh_wr():
        _we.next = fbus.write and not fbus.full
        _re.next = False

    # unused but needed for the fifo_mem block
    wad = Signal(waddr.val)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Memory for the FIFO
    fifomem_inst = fifo_mem(
        clock_write, _we, fbus.write_data, waddr,
        clock_read, _re, fbus.read_data,  raddr, wad
    )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # --Text from the paper--
    # The read pointer is a dual nbit Gray code counter.  The nbit 
    # pointer (rptr) is passed to the write clock domain through the 
    # syncs.  The (n-1)bit pointer (raddr) is used to address the FIFO 
    # buffer.  The FIFO empty output is registered and is asserted on 
    # the next rising rclk edge when the next rptr value equals the 
    # sync wptr value. 
    rbin = Signal(modbv(0)[asz+1:])

    @always_seq(clock_read.posedge, reset=rrst)
    def beh_rptrs():
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
    wbin = Signal(modbv(0)[asz+1:])

    @always_seq(clock_write.posedge, reset=wrst)
    def beh_wptrs():
        # increment when write and not full
        wbn = wbin + (fbus.write and not wfull)
        wbin.next = wbn
        wpn = (wbn >> 1) ^ wbn
        wptr.next = wpn

        # what the dillio with the full determination ...
        wfull.next = (wpn == concat(~wq2_rptr[asz+1:asz-1],
                                    wq2_rptr[asz-1:0]))
    
    @always_comb
    def beh_addrs():
        waddr.next = wbin[asz:0]
        raddr.next = rbin[asz:0]

    return myhdl.instances()


fifo_async.fbus_intf = FIFOBus