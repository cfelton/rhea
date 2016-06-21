
from __future__ import division, print_function, absolute_import

import myhdl
from myhdl import always_comb, always

from rhea.system import FIFOBus
from rhea.cores.fifo import fifo_async


from . import EMeshPacket, epkt_from_bits


@myhdl.block
def emesh_fifo(reset, emesh_i, emesh_o):
    """ EMesh transmit FIFO
    """

    # @todo: add rx channels ...

    nbits = len(emesh_i.txwr.bits)
    fbus_wr, fbus_rd, fbus_rr = [FIFOBus(width=nbits) for _ in range(3)]

    @myhdl.block
    def emesh_to_fifo(epkt, fbus):
        """ assign the EMesh inputs to the FIFO bus """
        @always_comb
        def beh_assign():
            fbus.write_data.next = epkt.bits
            print(epkt)
            if epkt.access:
                fbus.write.next = True
            else:
                fbus.write.next = False
        return beh_assign,

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
        def beh_read():
            if not fbus.empty and not epkt.wait:
                fbus.read.next = True
            else:
                fbus.read.next = False

        @always(clock.posedge)
        def beh_assign():
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

        return map_inst, beh_read, beh_assign

    # create a FIFO foreach channel: write, read, read-response
    fifo_insts = []
    for epkt, fifobus in zip((emesh_i.txwr, emesh_i.txrd, emesh_i.txrr,),
                             (fbus_wr, fbus_rd, fbus_rr,)):
        fifo_insts += emesh_to_fifo(epkt, fifobus)
        fifo_insts += fifo_async(
            clock_write=emesh_i.clock, clock_read=emesh_o.clock,
            fifobus=fifobus, reset=reset, size=16
        )

    # assign the output of the FIFO
    for epkt, fifobus in zip((emesh_o.txwr, emesh_o.txrd, emesh_o.txrr,),
                             (fbus_wr, fbus_rd, fbus_rr,)):
        fifo_insts += fifo_to_emesh(fifobus, epkt, emesh_o.clock)

    return fifo_insts

