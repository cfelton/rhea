
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from myhdl import (Signal, always_comb, always)

from rhea.cores.fifo import fifo_async
from rhea.system import FIFOBus

from . import EMeshPacket
from . import epkt_from_bits


def emesh_fifo(reset, emesh_i, emesh_o):
    """ EMesh transmit FIFO
    """

    # @todo: add rx channels ...

    nbits = len(emesh_i.txwr.bits)
    fbus_wr, fbus_rd, fbus_rr = [FIFOBus(size=16, width=nbits)
                                 for _ in range(3)]

    def emesh_to_fifo(epkt, fbus):
        """ assign the EMesh inputs to the FIFO bus """
        @always_comb
        def rtl_assign():
            fbus.write_data.next = epkt.bits
            print(epkt)
            if epkt.access:
                #fbus.write.next = True
                fbus.write.next = True
            else:
                #fbus.write.next = False
                fbus.write.next = False
        return rtl_assign,

    def fifo_to_emesh(fbus, epkt, clock):
        """ assign FIFO bus to emesh output """
        fpkt = EMeshPacket()

        # map the bit-vector to the EMeshPacket interface
        map_inst = epkt_from_bits(fpkt, fbus.read_data)

        # the FIFOs work with a read acknowledge vs. a read
        # request - meaning the data is available before the
        # read and transitions to the next data after the read
        # strobe

        # @todo: there is (might be) an error here if the FIFO
        #   works in read-ack, if wait is set the same packet
        #   will be stuck on the bus, need to make sure the EMesh
        #   ignores the packet when wait is set
        @always_comb
        def rtl_read():
            if not fbus.empty and not epkt.wait:
                #fbus.read.next = True
                fbus.read.next = True
            else:
                #fbus.read.next = False
                fbus.read.next = False

        @always(clock.posedge)
        def rtl_assign():
            # @todo: check and see if this will convert fine
            # @todo: epkt.assign(fpkt)
            if fbus.read_valid:
                print("YES READ VALID {} {} {}".format(fbus.read_data, fpkt, epkt))
                epkt.access.next = fpkt.access
                epkt.write.next = fpkt.write
                epkt.datamode.next = fpkt.datamode
                epkt.ctrlmode.next = fpkt.ctrlmode
                epkt.dstaddr.next = fpkt.dstaddr
                epkt.data.next = fpkt.data
                epkt.srcaddr.next = fpkt.srcaddr
            else:
                epkt.access.next = False

        return map_inst, rtl_read, rtl_assign

    # create a FIFO foreach channel: write, read, read-response
    fifo_insts = []
    for epkt, fifobus in zip((emesh_i.txwr, emesh_i.txrd, emesh_i.txrr,),
                             (fbus_wr, fbus_rd, fbus_rr,)):
        g = emesh_to_fifo(epkt, fifobus)
        fifo_insts.append(g)
        g = fifo_async(reset, emesh_i.clock, emesh_o.clock, fifobus)
        fifo_insts.append(g)

    # assign the output of the FIFO
    for epkt, fifobus in zip((emesh_o.txwr, emesh_o.txrd, emesh_o.txrr,),
                             (fbus_wr, fbus_rd, fbus_rr,)):
        g = fifo_to_emesh(fifobus, epkt, emesh_o.clock)
        fifo_insts.append(g)

    return fifo_insts

