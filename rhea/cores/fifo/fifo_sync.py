#
# Copyright (c) 2014 Christopher L. Felton
# See the licence file in the top directory
#

from math import log, fmod, ceil

import pytest

import myhdl
from myhdl import Signal, intbv, modbv, enum, always_comb, always_seq

from rhea import Global
from rhea.system import FIFOBus
from .fifo_mem import fifo_mem


@myhdl.block
def fifo_sync(glbl, fbus, size=128):
    """ Synchronous FIFO
    This block is a basic synchronous FIFO.  In many cases it is
    better to use the `fifo_fast` synchronous FIFO (lower resources).
    
    This FIFO uses a "read acknowledge", the read data is available
    on the read data bus before the read strobe is active.  When the
    read signal is set it is acknowledging the data has been read
    and the next FIFO item will be available on the bus.

    Arguments:
        glbl (Global): global signals, clock and reset
        fbus (FIFOBus): FIFO bus interface

    Parameters:
        size (int): the size of the FIFO, the FIFO will have hold
            at maximum *size* elements.

    Examples: 
    
        Write and read timing::
    
            clock:           /-\_/-\_/-\_/-\_/-\_/-\_/-\_/-\_/-\_/
            fbus.write:      _/---\_______/-----------\___________
            fbus.wrtie_data: -|D1 |-------|D2 |D3 |D4 |-----------
            fbus.read:       _____________/---\___________________
            fbus.read_data:           |D1    |--------------------
            fbus.empty:      ---------\______/--\_________________

        Usage::
    
            fifobus = FIFOBus(width=16)
            fifo_inst = fifo_sync(glbl, fifobus, size=128)
        
    """
    assert isinstance(glbl, Global)
    assert isinstance(fbus, FIFOBus)

    clock, reset = glbl.clock, glbl.reset
    fifosize = size

    if fmod(log(fifosize, 2), 1) != 0:
        asz = int(ceil(log(fifosize, 2)))
        fifosize = 2**asz
        print("@W: fifo_sync only supports power of 2 size")
        print("    forcing size (depth) to %d instread of %d" % (fifosize, fbus.size))

    wptr = Signal(modbv(0, min=0, max=fifosize))    # address to write to
    wptrd = Signal(modbv(0, min=0, max=fifosize))   # aligned write pointer
    rptr = Signal(modbv(0, min=0, max=fifosize))    # address to read from

    # generic memory model, this memory uses two registers on 
    # the input and one on the output, it takes three clock 
    # cycles for write data to appear on the read.
    fifomem_inst = fifo_mem(
        clock, fbus.write, fbus.write_data, wptr,
        clock, fbus.read, fbus.read_data, rptr, wptrd
    )

    # @todo: almost full and almost empty flags
    read, write = fbus.read, fbus.write
    states = enum('init', 'empty', 'active', 'full')
    state = Signal(states.init)

    @always_seq(clock.posedge, reset=reset)
    def beh_fifo():

        if state == states.init:
            wptr.next = 0
            rptr.next = 0
            fbus.full.next = False
            fbus.empty.next = True
            state.next = states.empty

        elif state == states.empty:
            if write:
                wptr.next = wptr + 1
            state.next = states.active

        elif state == states.active:
            # once the data is through the fifo_mem pipeline stages
            # mark the fifo as not empty.  The empty can be overwritten
            # below if a read occurs and the FIFO should go empty
            if wptrd != rptr:
                fbus.empty.next = False

            if read and not write:
                fbus.full.next = False
                if not fbus.empty:
                    rptr.next = rptr + 1
                if rptr+1 == wptrd:
                    fbus.empty.next = True
                    state.next = states.empty

            elif write and not read:
                if not fbus.full:
                    wptr.next = wptr + 1
                if wptr+1 == rptr:
                    fbus.full.next = True
                    state.next = states.full

            elif write and read:
                wptr.next = wptr + 1
                rptr.next = rptr + 1

        elif state == states.full:
            if read and not write:
                state.next = states.active
                rptr.next = rptr + 1

        else:
            state.next = states.init

        if fbus.clear:
            state.next = states.init

    @always_comb
    def beh_assign():
        fbus.read_valid.next = fbus.read and not fbus.empty
                
    nitems = fifosize
    if fifo_sync.occupancy_assertions:
        nvacant = Signal(intbv(fifosize, min=0, max=nitems+1))  # # empty slots
        ntenant = Signal(intbv(0, min=0, max=nitems+1))         # # filled slots
    else:
        nitems = int(2 ** (ceil(log(nitems, 2))))
        nvacant = Signal(modbv(nitems, min=0, max=nitems))
        ntenant = Signal(modbv(0, min=0, max=nitems))

    if fifo_sync.debug:
        @always_seq(clock.posedge, reset=reset)
        def dbg_occupancy():
            if fbus.clear:
                nvacant.next = fifosize   # the number of empty slots
                ntenant.next = 0          # the number of full slots
            else:
                v = int(nvacant)
                f = int(ntenant)

                if fbus.read_valid:
                    v = v + 1
                    f = f - 1
                if fbus.write:
                    v = v -1
                    f = f + 1

                nvacant.next = v
                ntenant.next = f

    # the FIFOBus count references the local signal
    fbus.count = ntenant

    # @todo: will need to replace myhdl.instances with the
    #        conditional collection of inst/gens (see above)
    return myhdl.instances()


# attached a generic fifo bus object to the module
fifo_sync.fbus_intf = FIFOBus
fifo_sync.debug = True
fifo_sync.occupancy_assertions = True
