
# Copyright (c) 2014 Christopher L. Felton
#

from math import log, fmod, ceil
from myhdl import Signal, intbv, modbv, always_comb, always_seq

from rhea.system import FIFOBus
from .fifo_mem import fifo_mem_generic


def fifo_sync(clock, reset, fbus):
    """ Simple synchronous FIFO

    PORTS
    =====

    PARAMETERS
    ==========
    """

    # @todo: this is intended to be used for small fast fifo's but it
    #        can be used for large synchronous fifo as well
    N = fbus.size

    if fmod(log(N, 2), 1) != 0:
        Asz = int(ceil(log(N,2)))
        N = 2**Asz
        print("@W: m_fifo_sync only supports power of 2 size")
        print("    forcing size (depth) to %d instread of %d" % (N, fbus.size))

    wptr = Signal(modbv(0, min=0, max=N))
    rptr = Signal(modbv(0, min=0, max=N))
    _vld = Signal(False)

    # generic memory model
    g_fifomem = fifo_mem_generic(clock, fbus.write, fbus.write_data, wptr,
                                 clock, fbus.read_data, rptr,
                                 mem_size=fbus.size)

    # @todo: almost full and almost empty flags
    read = fbus.read
    write = fbus.write

    @always_seq(clock.posedge, reset=reset)
    def rtl_fifo():
        if fbus.clear:
            wptr.next = 0
            rptr.next = 0
            fbus.full.next = False
            fbus.empty.next = True

        elif read and not write:
            fbus.full.next = False
            if not fbus.empty:
                rptr.next = rptr + 1
            if rptr == (wptr-1):
                fbus.empty.next = True

        elif write and not read:
            fbus.empty.next = False
            if not fbus.full:
                wptr.next = wptr + 1
            if wptr == (rptr-1):
                fbus.full.next = True

        elif write and read:
            wptr.next = wptr + 1
            rptr.next = rptr + 1

        _vld.next = read

    @always_comb
    def rtl_assign():
        fbus.read_valid.next = _vld & fbus.read
                
    nvacant = Signal(intbv(N, min=-0, max=N+1))  # # empty slots
    ntenant = Signal(intbv(0, min=-0, max=N+1))  # # filled slots
    
    @always_seq(clock.posedge, reset=reset)
    def dbg_occupancy():
        if fbus.clear:
            nvacant.next = N
            ntenant.next = 0
        else:
            v = nvacant
            f = ntenant
            
            if fbus.read_valid:
                v = v + 1
                f = f - 1
            if fbus.write:
                v = v -1 
                f = f + 1

            nvacant.next = v
            ntenant.next = f

    fbus.count = ntenant

    return (g_fifomem, rtl_fifo, rtl_assign, dbg_occupancy,)


# attached a generic fifo bus object to the module
fifo_sync.fbus_intf = FIFOBus