
from __future__ import division
from __future__ import absolute_import


from myhdl import *

from rhea import cores
from rhea.system import FIFOBus


def fifo_cdc(glbl, emesh_i, emesh_o):
    """
    map the packet interfaces to the FIOF interface
    """

    fifo_intf = FIFOBus(size=16, width=len(emesh_i.bits))

    @always_comb
    def rtl_assign():
        wr.next = emesh_i.access and not fifo_intf.full
        rd.next = not fifo_intf.empty and not emesh_i.wait
        emesh_o.wait.next = fifo_intf.full

    @always(emesh_o.clock.posedge)
    def rtl_access():
        if not emesh_i.wait:
            emesh_o.access.next = fifo_intf.rd

    # assign signals ot the FIFO interface
    fifo_intf.wdata = emesh_i.bits
    fifo_intf.rdata = emesh_o.bits

    g_fifo = cores.fifo.fifo_async(glbl.reset, emesh_i.clock, 
                                   emesh_o.clock, fifo_intf)

    return rtl_assign, rtl_access, g_fifo