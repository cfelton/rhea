
from __future__ import absolute_import

import myhdl
from myhdl import Signal, intbv, delay, instance, always_comb

from . import EMeshPacket
from rhea.models import FIFO


class ELinkChannel(object):
    """ RX or TX channel in an ELink interface
    """
    def __init__(self):
        # The Signals for the channel
        self.lclk = Signal(bool(0))       # interface sync clock
        self.frame = Signal(bool(0))      # valid frame/data
        self.data = Signal(intbv(0)[8:])  # byterized emesh packet data
        self.wr_wait = Signal(bool(0))    # write pushback
        self.rd_wait = Signal(bool(0))    # read pushback

        # clock rate assuming 1ps simulation step
        self.htick = 500

    @myhdl.block
    def _clkgen(self):
        """ Generate the clock for this interface
        :return:
        """
        @instance
        def gclkgen():
            self.lclk.next = False
            while True:
                yield delay(self.htick)
                self.lclk.next = not self.lclk

        return gclkgen

    @myhdl.block
    def instances(self):
        return self._clkgen()


class _ELinkTransaction(object):
    """ Simple object to manage ELink transactions
    """
    def __init__(self, bytes):
        if not isinstance(bytes[0], intbv):
            bytes = [intbv(bb)[8:] for bb in bytes]
        self.bytes = bytes               # bytes to be transferred
        self.finished = Signal(bool(0))  # transfer finished / completed


class ELink(object):
    """
    The ELink interface is the external interface between devices (typically
    the Adapteva Epiphany and an FPGA).

    @todo: more description ...

    The Epiphany datasheet (has a description of the chip-to-chip (ELink)
    interfaces):
    http://www.adapteva.com/docs/e16g301_datasheet.pdf

    The Parallella open-hardware (oh) repository:
    https://github.com/parallella/oh/tree/master/elink
    """

    def __init__(self):
        self._tx = ELinkChannel()
        self._rx = ELinkChannel()

        self._tx_fifo = FIFO()
        self._rx_fifo = FIFO()

        # Keep track how this interface is connected, only an east-west or
        # north-south connections can be established (not both).
        # The east-west and north-south are redundant but commonly used.
        self.connections = {'east': False, 'west': False,
                            'north': False, 'south': False}

    def connect(self, pos):
        """ Return relative relation
        In this implementation the TX and RX are from the perspective of
        the external link (e.g. the FPGA link).  This function is used
        to get local perspective.
        :param pos: where the component is logically positioned (located)
        :return: tx link, rx link
        """
        pos = pos.lower()
        assert pos in self.connections
        assert not self.connections[pos], "{} connection exists".format(pos)
        self.connections[pos] = True
        if pos in ('east', 'north'):
            links = self._tx, self._rx
        elif pos in ('west', 'south'):
            links = self._rx, self._tx
        return links

    @myhdl.block
    def instances(self):
        return self._tx.instances(), self._rx.instances()

    def write(self, dstaddr, data, srcaddr=0, block=True):
        """A single ELink write transaction
        """
        packet = EMeshPacket(access=1, write=1, datamode=2,
                             dstaddr=dstaddr, data=data, srcaddr=srcaddr)
        bytes = packet.tobytes()
        bpkt = _ELinkTransaction(bytes)
        self._tx_fifo.write(bpkt)
        if block:
            yield bpkt.finished.posedge

    def read(self, dstaddr, data, srcaddr=0, block=True):
        """ A single ELink read transaction
        """
        packet = EMeshPacket(access=1, write=0, datamode=2,
                             dstaddr=dstaddr, data=data, srcaddr=srcaddr)
        bytes = packet.tobytes()
        tpkt = _ELinkTransaction(bytes)
        self._tx_fifo.append(tpkt)
        if block:
            yield tpkt.finished.posedge

    def send_packet(self, emesh, block=True):
        bytes = emesh.tobytes()
        tpkt = _ELinkTransaction(bytes)
        self._tx_fifo.write(tpkt)
        if block:
            yield tpkt.finished.posedge

    def receive_packet(self, emesh, block=True):
        if self._rx_fifo.is_empty() and block:
            yield self._rx_fifo.empty.negedge

        # if blocked will not be empty, if not block maybe
        if not self._rx_fifo.is_empty():
            tpkt = self._rx_fifo.read()
            emesh.frombytes(tpkt.bytes)
            # allow emesh to update
            yield self._rx.lclk.posedge

    def write_bytes(self, bytes, block=True):
        assert isinstance(bytes, (list, tuple))

    def read_bytes(self, bytes, block=True):
        assert isinstance(bytes, list)

    @myhdl.block
    def process(self):
        """ Drive the ELink signals
        This process mimics the behavior of the external ELink logic.

        @todo: this really needs to exist in a specific module model???

        myhdl not convertible
        """
        @instance
        def tx_bytes():
            while True:
                if not self._tx_fifo.is_empty():
                    pkt = self._tx_fifo.read()
                    assert isinstance(pkt, _ELinkTransaction)
                    yield self._send_bytes(pkt.bytes)
                    pkt.finished.next = True
                else:
                    yield self._tx_fifo.empty.negedge

        @instance
        def rx_bytes():
            while True:
                bytes = [None for _ in range(13)]
                yield self._receive_bytes(bytes)
                self._rx_fifo.write(_ELinkTransaction(bytes))

        return tx_bytes, rx_bytes

    def _send_bytes(self, bytes):
        yield self._tx.lclk.posedge
        self._tx.frame.next = True
        for ii in range(13):
            self._tx.data.next = bytes[ii]
            yield self._tx.lclk.posedge
        self._tx.frame.next = False
        yield self._tx.lclk.posedge

    def _receive_bytes(self, bytes):
        ri = 0
        while ri < 13:
            yield self._rx.lclk.posedge
            if self._rx.frame:
                bytes[ri] = intbv(int(self._rx.data))[8:0]
                ri += 1
