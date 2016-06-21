
from __future__ import division

import myhdl
from myhdl import always_comb, always

from rhea import cores
from rhea import Signals
from rhea.system import FIFOBus


@myhdl.block
def fifo_cdc(glbl, emesh_i, emesh_o):
    """
    map the packet interfaces to the FIFO interface
    """

    wr, rd = Signals(bool(0), 2)
    fifo_intf = FIFOBus(width=len(emesh_i.bits))

    @always_comb
    def beh_assign():
        wr.next = emesh_i.access and not fifo_intf.full
        rd.next = not fifo_intf.empty and not emesh_i.wait
        emesh_o.wait.next = fifo_intf.full

    @always(emesh_o.clock.posedge)
    def beh_access():
        if not emesh_i.wait:
            emesh_o.access.next = fifo_intf.read

    # assign signals ot the FIFO interface
    fifo_intf.write_data = emesh_i.bits
    fifo_intf.read_data = emesh_o.bits

    fifo_inst = cores.fifo.fifo_async(
        clock_write=emesh_i.clock, clock_read=emesh_o.clock,
        fifobus=fifo_intf, reset=glbl.reset, size=16
    )

    return beh_assign, beh_access, fifo_inst