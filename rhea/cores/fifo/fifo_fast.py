#
# Copyright (c) 2014 Christopher L. Felton
#

from myhdl import (Signal, intbv, always, always_comb, always_seq)

from rhea.system import FIFOBus
from .fifo_srl import fifo_srl


def fifo_fast(reset, clock, fbus, use_srl_prim=False):
    """
    Often small simple, synchronous, FIFOs can be implemented with 
    specialized hardware in an FPGA (e.g. vertically chaining LUTs).

    This FIFO is intended to be used for small fast FIFOs.  But when
    used for large ...
    
    This FIFO is a small FIFO (currently fixed to 16) that is implemented
    to take advantage of some hardware implementations.

    Typical FPGA synthesis will infer shift-register-LUT (SRL) for small
    synchronous FIFOs.  This FIFO is implemented generically, consult the
    synthesis and map reports.

    Arguments (ports):

    Parameters:
    use_slr_prim: this parameter indicates to use the SRL primitive
      (inferrable primitive).  If SRL are not inferred from the generic
      description this option can be used.  Note, srl_prim will only
      use a size (FIFO depth) of 16.
    """

    # @todo: this is intended to be used for small fast fifo's but it
    # @todo: can be used for large synchronous fifo as well

    N = 32   # default and max size    
    if use_srl_prim:
        N = 16
    elif fbus.size > N:
        print("@W: m_fifo_fast only supports size < {}, for fast".format(N))
        print("    forcing size (depth) to {}".format(N))
    else:
        N = fbus.size

    mem = [Signal(intbv(0)[fbus.width:]) for _ in range(N)]
    addr = Signal(intbv(0, min=0, max=N))

    # aliases to the FIFO bus interface
    srlce = fbus.write     # single cycle write
    
    # note: use_srl_prim has not been tested!
    # note: signal slices write_data() will need to be used instead of
    #       bit slices wsdata[].  Have add 
    if use_srl_prim:
        gsrl = [None for _ in range(N)]
        for ii in range(N):
            gsrl[ii] = fifo_srl(clock, fbus.write_data(ii), fbus.write,
                                addr, fbus.read_data(ii))
    else:
        # the SRL based FIFO always writes to address 0 and shifts
        # the FIFO, only a read address is accounted.
        @always(clock.posedge)
        def rtl_srl_in():
            if srlce:
                mem[0].next = fbus.write_data
                for ii in range(1, N):
                    mem[ii].next = mem[ii-1]

    @always_comb
    def rtl_srl_out():
        fbus.read_data.next = mem[addr]

    @always_comb
    def rtl_vld():
        # no delay on reads
        fbus.read_valid.next = fbus.read and not fbus.empty

    # the address is the read address, the write address is always
    # zero but on a write all values are shifted up one index, only
    # the read address is accounted in the following.
    @always_seq(clock.posedge, reset=reset)
    def rtl_fifo():
        if fbus.clear:
            addr.next = 0
            fbus.empty.next = True
            fbus.full.next = False

        elif fbus.read and not fbus.write:
            fbus.full.next = False
            if addr == 0:
                fbus.empty.next = True
            else:
                addr.next = addr - 1

        elif fbus.write and not fbus.read:
            fbus.empty.next = False
            if not fbus.empty:
                addr.next = addr + 1
            if addr == N-2:
                fbus.full.next = True

        # nothing happens if read and write at the same time
            
    # note: failures occur if write/read when full/empty respectively
                
    nvacant = Signal(intbv(N, min=0, max=N+1))  # # empty slots
    ntenant = Signal(intbv(0, min=0, max=N+1))  # # filled slots

    @always_seq(clock.posedge, reset=reset)
    def rtl_occupancy():
        if fbus.clear:
            nvacant.next = N
            ntenant.next = 0
        elif fbus.read and not fbus.write:
            nvacant.next = nvacant + 1
            ntenant.next = ntenant - 1
        elif fbus.write and not fbus.read:
            nvacant.next = nvacant - 1
            ntenant.next = ntenant + 1

    @always_comb
    def rtl_count():
        fbus.count.next = ntenant

    gens = (rtl_srl_in, rtl_srl_out, rtl_vld, rtl_fifo,
            rtl_occupancy, rtl_count,)
    return gens


fifo_fast.fbus_intf = FIFOBus
