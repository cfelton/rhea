
from __future__ import absolute_import

import myhdl
from myhdl import instance
from rhea.cores.elink import ELink, EMesh, EMeshPacket


@myhdl.block
def elink_external_model(elink, emesh):
    """ This is a simple model of the ELink component (FPGA)

    Arguments:
        elink (ELink): Interface to the external ELink device
        emesh (EMesh): Interface to the internal EMesh

    myhdl not convertible.
    """
    print(type(elink), type(emesh))
    assert isinstance(elink, ELink)
    assert isinstance(emesh, EMesh)

    # get the tx and rx links based on this module's location
    # (refer to the tx/rx from this components perspective).
    tx, rx = elink.connect('north')

    # get the clock generator for the interface
    txclk_inst = tx.instances()

    # use the elink process to drive the signals
    elink_inst = elink.process()

    @instance
    def process_tx():
        """ process the TX FIFOs (wr, rd, rr)
        Check for packets on the TX FIFOs and forward them to the Elink
        interface to be transmitted.
        """
        while True:
            if not emesh.txwr_fifo.is_empty():
                pkt = emesh.txwr_fifo.read()
                # update the interface to reflect this
                emesh.txwr.assign(pkt)
                yield elink.send_packet(pkt)
            elif not emesh.txrd_fifo.is_empty():
                pkt = emesh.txrd_fifo.read()
                emesh.txrd.assign(pkt)
                yield elink.send_packet(pkt)
            elif not emesh.txrr_fifo.is_empty():
                pkt = emesh.txrr_fifo.read()
                emesh.txrr.assign(pkt)
                yield elink.send_packet(pkt)

            # wait for one of the FIFOs not empty
            if (emesh.txwr_fifo.is_empty() and
                emesh.txrd_fifo.is_empty() and
                emesh.txrr_fifo.is_empty()):

                events = (emesh.txwr_fifo.empty.negedge,
                          emesh.txrd_fifo.empty.negedge,
                          emesh.txrr_fifo.empty.negedge)
                yield events
            else:
                yield emesh.clock.posedge

    @instance
    def process_rx():
        """ process the incoming packets (RX)
        Check for ELink transactions (packets) and place the received
        packets on to the EMesh FIFOs
        """
        while True:
            epkt = EMeshPacket()
            yield elink.receive_packet(epkt)
            print("[ELINK] {}".format(epkt))
            emesh.route_to_fifo(epkt)

    return myhdl.instances()


