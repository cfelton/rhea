
from myhdl import Signal, intbv, always_seq

from rhea.system import FIFOBus
from . import SPIBus


def spi_slave_fifo(glbl, spibus, fifobus, cso=None):
    """
    This is an SPI slave peripheral, when the master starts clocking
    any data in the TX FIFO (fifobus.write) will be sent (the next
    byte) and the received byte will be copied to RX FIFO
    (fifobus.read).  The `cso` interface can be used to configure
    how the SPI slave peripheral behaves.

    Arguments (Ports):
        glbl (Global): global clock and reset
        spibus  (SPIBus): the external SPI interface
        fifobus (FIFOBus): the fifo interface
        cso (SPIControlStatus): the control status signals
    """

    # Use an async FIFO to transfer from the SPI SCK clock domain and
    # the internal clock domain.  This allows for high-speed SCK.
    clock, reset = glbl.clock, glbl.reset
    assert isinstance(spibus, SPIBus)
    assert isinstance(fifobus, FIFOBus)

    @always_seq(clock.posedge, reset=reset)
    def beh_loopback():
        spibus.miso.next = spibus.mosi

    return beh_loopback
