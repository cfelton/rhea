
from __future__ import print_function, division

import myhdl
from myhdl import (Signal, SignalType, intbv, ConcatSignal,
                   always_comb, concat)

from rhea.models import FIFO


@myhdl.block
def epkt_from_bits(epkt, bits):
    """ Map a bit-vector to an EMeshPacket interface
    :param epkt: EMeshPacket interface
    :param bits: bit-vector (myhdl.intbv)
    :return: myhdl generators

    Convertible
    """
    @always_comb
    def beh_assign():
        epkt.access.next = bits[1:0]
        epkt.write.next = bits[2:1]
        epkt.datamode.next = bits[4:2]
        epkt.ctrlmode.next = bits[8:4]
        epkt.dstaddr.next = bits[40:8]
        epkt.data.next = bits[72:40]
        epkt.srcaddr.next = bits[104:72]
    return beh_assign


class EMeshPacket(object):
    def __init__(self, access=0, write=0, datamode=2, ctrlmode=0,
                 dstaddr=0, data=0, srcaddr=0):
        """
                  PACKET FIELD  | BITS    | DESCRIPTION
        --------------|---------|----------
        access        | [0]     | Indicates a valid transaction
        write         | [1]     | Indicates a write transaction
        datamode[1:0] | [3:2]   | Datasize (00=8b,01=16b,10=32b,11=64b)
        ctrlmode[3:0] | [7:4]   | Various special modes for the Epiphany chip
        dstaddr[31:0] | [39:8]  | Address for write, read-request, or
                                  read-responses
        data[31:0]    | [71:40] | Data for write transaction, data for
                                  read response
        srcaddr[31:0] | [103:72]| Return address for read-request, upper
                                  data for write

        Arguments:
            access: Indicates a valid transaction, initial value
            write: Indicates a write transaction, initial value
            datamode: Data size (0=8b, 1=16b, 2=32b, 3=64b),
                initial value
            ctrlmode: Various special modes for the Epiphany chip,
                initial value
            dstaddr: Address for write, read-request, or
                read-response, initial value
            data: Data for a write transaction, data for read
                response, initial value
            srcaddr: Return addres for read-request upper data for
                write, initial value
        """

        # set the packet fields
        self.access = Signal(bool(access))
        self.write = Signal(bool(write))
        self.datamode = Signal(intbv(datamode)[2:])
        self.ctrlmode = Signal(intbv(ctrlmode)[4:])
        self.dstaddr = Signal(intbv(dstaddr)[32:])
        self.data = Signal(intbv(data)[32:])
        self.srcaddr = Signal(intbv(srcaddr)[32:])

        # all the above a flattened into a signal bus
        self.bits = ConcatSignal(self.srcaddr, self.data, self.dstaddr,
                                 self.ctrlmode, self.datamode, self.write,
                                 self.access)

        # flow control ...
        self.wait = Signal(bool(0))

        # some extra signals used for modeling and testing
        self.finished = Signal(bool(0))

    def __str__(self):
        bits = self._bits()
        return "{:026X}".format(int(bits))

    def _bits(self):
        bits = concat(self.srcaddr, self.data, self.dstaddr,
                      self.ctrlmode, self.datamode, self.write, self.access)
        return bits

    def tobytes(self):
        bytes = [intbv(0)[8:] for _ in range(13)]
        bits = self._bits()
        for ii in range(13):
            bytes[ii][:] = bits[8*ii+8:8*ii]
        return bytes

    def frombytes(self, bytes):
        self.clear()
        self.access.next = bytes[0][0]
        self.write.next = bytes[0][1]
        self.datamode.next = bytes[0][4:2]
        self.ctrlmode.next = bytes[0][8:4]
        self.dstaddr.next = concat(*reversed(bytes[1:5]))
        self.data.next = concat(*reversed(bytes[5:9]))
        self.srcaddr.next = concat(*reversed(bytes[9:13]))

    def clear(self):
        self.access.next = False
        self.write.next = False
        self.datamode.next = 0
        self.ctrlmode.next = 0
        self.dstaddr.next = 0
        self.data.next = 0
        self.srcaddr.next = 0

    def assign(self, pkt):
        """ assign values of pkt.
        This can only be used for modeling and testing.
        """
        self.access.next = pkt.access
        self.write.next = pkt.write
        self.datamode.next = pkt.datamode
        self.ctrlmode.next = pkt.ctrlmode
        self.dstaddr.next = pkt.dstaddr
        self.data.next = pkt.data
        self.srcaddr.next = pkt.srcaddr


class EMeshPacketSnapshot(object):
    def __init__(self, epkt=None):
        """ Snapshot of an EMeshPacket interface
        This object is used to capture a snapshot, values only,
        of a EMeshPacket at a particular point in time
        """
        if epkt is not None:
            for k, v in epkt.__dict__.items():
                if isinstance(v, SignalType):
                    self.__dict__[k] = int(v)

    def update(self, epkt):
        if epkt is not None:
            for k, v in epkt.__dict__.items():
                if isinstance(v, SignalType):
                    self.__dict__[k] = int(v)

    def __eq__(self, other):
        assert isinstance(other, EMeshPacketSnapshot)
        mismatch = False
        for k, v in self.__dict__.items():
            if v != other.__dict__[k]:
                mismatch = True
        return not mismatch


class EMesh(object):
    def __init__(self, clock):
        """
        The EMesh interface on the external ELinks is defined as having
        three EMeshPacket conduits.  These conduits are used to send
        write and read requests over the Elink.

        """

        self.clock = clock         # the interface clock
        self.txwr = EMeshPacket()  # TX write, send write commands
        self.txrd = EMeshPacket()  # TX read, send read commands
        self.txrr = EMeshPacket()  # TX read response, acknowledge external read commands

        self.rxwr = EMeshPacket()  # RX write, receive external write commands
        self.rxrd = EMeshPacket()  # RX read, receive external read commands
        self.rxrr = EMeshPacket()  # RX read response, receive read acknowledge

        # transmit and receive FIFOs - simulation only
        # @todo: want these to be private (_) but then a bunch of
        # @todo: methods need to be added to wait on packet events, etc.
        self.packet_types = ('wr', 'rd', 'rr',)
        self.txwr_fifo = FIFO()
        self.txrd_fifo = FIFO()
        self.txrr_fifo = FIFO()

        self.rxwr_fifo = FIFO()
        self.rxrd_fifo = FIFO()
        self.rxrr_fifo = FIFO()

        self._outstanding_reads = {}

    def __str__(self):
        s = "txwr: {}, txrd: {}, txrr: {}, rxwr: {}, rxrd: {}, rxrr: {}".format(
             self.txwr_fifo.count, self.txrd_fifo.count, self.txrr_fifo.count,
             self.rxwr_fifo.count, self.rxrd_fifo.count, self.rxrr_fifo.count)
        return s

    def set_clock(self, clock):
        self.clock = clock

    def write(self, dstaddr, data, datau=0):
        """ send a write packet

        Arguments:
            dstaddr: destination address for the write
            data: 32bit data for the write
            datau: upper 32bit data for the write (64bit write)

        @todo: add explanation why a separate packet is used to push
               onto the transaction FIFOs (needs copies on the FIFOs
               and not actual bus interface).

        myhdl not convertible.
        """
        # get a new packet for the transaction emulation
        pkt = EMeshPacket(access=True, write=True,
                          dstaddr=dstaddr, data=data, srcaddr=datau)
        # push the packet onto the TX write FIFO
        # also assign the txwr packet to the new packet, the txwr
        # will mirror the transaction packet
        self.txwr.assign(pkt)
        self.txwr_fifo.write(pkt)
        yield self.clock.posedge
        self.txwr.clear()

    def read(self, dstaddr, data, srcaddr):
        """ send a read packet

        Arguments:
            dstaddr:
            data:
            srcaddr:

        myhdl not convertible.
        """
        # sent a read packet through the txrd fifo
        pkt = EMeshPacket(access=True, write=False,
                          dstaddr=dstaddr, data=data, srcaddr=srcaddr)
        # push the packet onto the TX read FIFO
        self.txrd_fifo.write(pkt)
        self._outstanding_reads[dstaddr] = pkt
        yield self.clock.posedge

    def read_response(self, read_packet):
        """ send a read response

        Arguments:
            read_packet:

        @todo: complete
        myhdl not convertible.
        """
        pass

    def route_to_fifo(self, pkt):
        """ take a freshly received packet from the ELink interface
        Take a freshly received packet from the ELink interface and route
        it to the correct RX fifo.

        Arguments:
            pkt:

        myhdl not convertible
        """
        # if the write bit is set pass it to RX write FIFO
        # @todo: how to determine the other packets??

        if pkt.write:
            self.rxwr_fifo.write(pkt)
        else:
            # determine if this is a read-request or read-response.
            pass

    def get_packet(self, pkt_type):
        """ Get a packet from one of the channels
        :param pkt_type:
        :return:
        """
        assert pkt_type in self.packet_types
        pkt = None
        if pkt_type == 'wr':
            pkt = self.rxwr_fifo.read()
        elif pkt_type == 'rd':
            pkt = self.rxrd_fifo.read()
        elif pkt_type == 'rr':
            pkt = self.rxrr_fifo.read()

        return pkt


class EMeshSnapshot(object):
    def __init__(self, emesh):
        for k, v in emesh.__dict__.items():
            if isinstance(v, EMeshPacket):
                self.__dict__[k] = EMeshPacketSnapshot(v)

    def __eq__(self, other):
        assert isinstance(other, EMeshSnapshot)
        mismatch = False
        for k, v in self.__dict__.items():
            if v != other.__dict__[k]:
                mismatch = True
        return not mismatch




