#
# Copyright (c) 2014 Christopher L. Felton
#

from math import log, ceil
import myhdl
from myhdl import (Signal, ResetSignal, intbv, modbv,
                   always, always_comb, always_seq)

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
        reset: system reset
        clock: system clock
        fbus: FIFOBus FIFO interface

    Parameters:
    use_slr_prim: this parameter indicates to use the SRL primitive
      (inferrable primitive).  If SRL are not inferred from the generic
      description this option can be used.  Note, srl_prim will only
      use a size (FIFO depth) of 16.
    """

    # @todo: this is intended to be used for small fast fifo's but it
    # @todo: can be used for large synchronous fifo as well

    nitems = 32   # default and max size
    if use_srl_prim:
        nitems = 16
    elif fbus.size > nitems:
        print("@W: fifo_fast only supports size < {}, for fast".format(nitems))
        print("    forcing size (depth) to {}".format(nitems))
    else:
        nitems = fbus.size

    mem = [Signal(intbv(0)[fbus.width:]) for _ in range(nitems)]
    addr = Signal(intbv(0, min=0, max=nitems))

    # aliases to the FIFO bus interface
    srlce = fbus.write     # single cycle write
    
    # note: use_srl_prim has not been tested!
    # note: signal shadow slices write_data() and not index []
    if use_srl_prim:
        srl_inst = [None for _ in range(nitems)]
        for ii in range(nitems):
            srl_inst[ii] = fifo_srl(clock, fbus.write_data(ii), fbus.write,
                                    addr, fbus.read_data(ii))
    else:
        # the SRL based FIFO always writes to address 0 and shifts
        # the FIFO, only a read address is accounted.
        @always(clock.posedge)
        def rtl_srl_in():
            if srlce:
                mem[0].next = fbus.write_data
                for jj in range(1, nitems):
                    mem[jj].next = mem[jj-1]

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
            if addr == nitems-2:
                fbus.full.next = True

        # nothing happens if read and write at the same time
            
    # note: failures occur if write/read when full/empty respectively

    if fifo_fast.occupancy_assertions:
        nvacant = Signal(intbv(nitems, min=0, max=nitems+1))  # # empty slots
        ntenant = Signal(intbv(0, min=0, max=nitems+1))       # # filled slots
    else:
        nitems = int(2**(ceil(log(nitems, 2))))
        nvacant = Signal(modbv(nitems, min=0, max=nitems))
        ntenant = Signal(modbv(0, min=0, max=nitems))

    if fifo_fast.debug:
        @always_seq(clock.posedge, reset=reset)
        def rtl_occupancy():
            if fbus.clear:
                nvacant.next = nitems
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

    return myhdl.instances()


# fifo_fast block attributes, these will affect all instances
fifo_fast.portmap = dict(
    reset=ResetSignal(0, active=1, async=False),
    clock=Signal(bool(0)),
    fbus=FIFOBus()
)
fifo_fast.debug = True
fifo_fast.occupancy_assertions = True
