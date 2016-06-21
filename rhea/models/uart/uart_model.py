
try:
    import queue
except ImportError:
    import Queue as queue

import myhdl
from myhdl import Signal, intbv, enum, always_seq, always, always_comb


class UARTModel(object):
    def __init__(self, stopbits=1, parity=None):
        """ """
        self._txq = queue.Queue()
        self._rxq = queue.Queue()
        self._rxbyte = None

        self.baudrate = 115200
        self.stopbits = stopbits
        # @todo: add parity
        assert parity in (None, 'even', 'odd')
        self.parity = parity

    def write(self, byte):
        self._txq.put(intbv(byte)[8:])
        
    def read(self):
        self._rxbyte = None
        if not self._rxq.empty():
            self._rxbyte = self._rxq.get()
        return self._rxbyte

    @myhdl.block
    def process(self, glbl, serin, serout):
        """ """

        clock, reset = glbl.clock, glbl.reset
        txq, rxq = self._txq, self._rxq

        maxbaud = clock.frequency / self.baudrate
        baudcnt = Signal(0)
        baudce, baudceh = Signal(bool(0)), Signal(bool(0))
        syncbaud = Signal(bool(0))

        @always_seq(clock.posedge, reset=reset)
        def mdlbaud():
            # @todo: need separate tx and rx baud strobes, the rx
            #        syncs the count to the start of a byte frame
            #        can't share a counter if rx and tx are at the
            #        same time.
            # this will not work if currently transmitting
            if syncbaud:
                baudcnt.next = 0
            else:
                if baudcnt > maxbaud:
                    baudcnt.next = 0
                    baudce.next = True
                    baudceh.next = False
                elif baudcnt == maxbaud//2:
                    baudcnt.next = baudcnt + 1
                    baudce.next = False
                    baudceh.next = True
                else:
                    baudcnt.next = baudcnt + 1
                    baudce.next = False
                    baudceh.next = False

        # tx and rx states
        states = enum('wait', 'start', 'byte', 'parity', 'stop', 'end')
        txbyte = Signal(intbv(0)[8:])
        txbitcnt = Signal(0)
        txstate = Signal(states.wait)

        @always_seq(clock.posedge, reset=reset)
        def mdltx():
            if txstate == states.wait:
                serout.next = True
                if not txq.empty():
                    txbyte.next = txq.get()
                    txbitcnt.next = 0
                    txstate.next = states.start

            elif txstate == states.start:
                if baudce:
                    serout.next = False
                    txstate.next = states.byte

            elif txstate == states.byte:
                if baudce:
                    serout.next = True if txbyte & 0x01 else False
                    txbitcnt.next = txbitcnt + 1
                    txbyte.next = txbyte >> 1

                elif txbitcnt == 8:
                    txbitcnt.next = 0
                    txstate.next = states.stop

            elif txstate == states.stop:
                if baudce:
                    serout.next = True
                    txbitcnt.next = txbitcnt + 1
                elif txbitcnt.next == self.stopbits:
                    txstate.next = states.end

            elif txstate == states.end:
                txstate.next = states.wait

        rxbyte = Signal(intbv(0)[8:])
        rxbitcnt = Signal(0)
        rxstate = Signal(states.wait)
        _serin = Signal(bool(1))
        serin_posedge, serin_negedge = Signal(bool(0)), Signal(bool(0))

        @always(clock.posedge)
        def mdlrxd():
            _serin.next = serin

        @always_comb
        def mdledges():
            serin_posedge.next = False
            serin_negedge.next = False
            if not _serin and serin:
                serin_posedge.next = True
            elif _serin and not serin:
                serin_negedge.next = True

        @always_seq(clock.posedge, reset=reset)
        def mdlrx():
            syncbaud.next = False

            if rxstate == states.wait:
                if serin_negedge:
                    rxstate.next = states.start
                    syncbaud.next = True

            elif rxstate == states.start:
                if baudceh:
                    rxstate.next = states.byte
                    rxbitcnt.next = 0
                    
            elif rxstate == states.byte:
                if baudceh:
                    rxbyte.next[rxbitcnt] = serin
                    rxbitcnt.next = rxbitcnt + 1
                elif rxbitcnt == 8:
                    rxstate.next = states.stop
                    rxbitcnt.next = 0

            elif rxstate == states.stop:
                if baudceh:
                    assert serin
                    rxbitcnt.next = rxbitcnt + 1
                elif rxbitcnt == self.stopbits:
                    rxstate.next = states.end

            elif rxstate == states.end:
                self._rxq.put(int(rxbyte))
                rxstate.next = states.wait

        return myhdl.instances()
