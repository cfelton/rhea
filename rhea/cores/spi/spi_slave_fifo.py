
import myhdl
from myhdl import Signal, intbv, always, concat

from rhea import Signals
from rhea.system import FIFOBus
from rhea.cores.misc import syncro
from rhea.cores.fifo import fifo_fast
from . import SPIBus


@myhdl.block
def spi_slave_fifo(glbl, spibus, fifobus):
    """
    This is an SPI slave peripheral, when the master starts clocking
    any data in the TX FIFO (fifobus.write) will be sent (the next
    byte) and the received byte will be copied to RX FIFO
    (fifobus.read).  The `cso` interface can be used to configure
    how the SPI slave peripheral behaves.

    (Arguments == Ports)
    Arguments:
        glbl (Global): global clock and reset
        spibus  (SPIBus): the external SPI interface
        fifobus (FIFOBus): the fifo interface
        cso (ControlStatus): the control status signals
    """
    fifosize = 8

    # Use an async FIFO to transfer from the SPI SCK clock domain and
    # the internal clock domain.  This allows for high-speed SCK.
    clock, reset = glbl.clock, glbl.reset
    assert isinstance(spibus, SPIBus)
    assert isinstance(fifobus, FIFOBus)

    sck, csn = spibus.sck, spibus.csn
    # the FIFOs for the receive and transmit (external perspective)
    readpath = FIFOBus(width=fifobus.width)
    writepath = FIFOBus(width=fifobus.width)

    # the FIFO instances
    tx_fifo_inst = fifo_fast(glbl, writepath, size=fifosize)
    rx_fifo_inst = fifo_fast(glbl, readpath, size=fifosize)
    mp_fifo_inst = fifobus.assign_read_write_paths(readpath, writepath)

    spi_start = Signal(bool(0))
    ireg, icap, icaps = Signals(intbv(0)[8:], 3)
    oreg, ocap = Signals(intbv(0)[8:], 2)
    bitcnt, b2, b3 = Signals(intbv(0, min=0, max=10), 3)

    @always(sck.posedge, csn.negedge)
    def csn_falls():
        if sck:
            spi_start.next = False
        elif not csn:
            spi_start.next = True

    # SCK clock domain, this allows high SCK rates
    @always(sck.posedge, csn.posedge)
    def sck_capture_send():
        if csn:
            b2.next = 0
            bitcnt.next = 0
        else:
            if bitcnt == 0 or spi_start:
                spibus.miso.next = ocap[7]
                oreg.next = (ocap << 1) & 0xFF
            else:
                spibus.miso.next = oreg[7]
                oreg.next = (oreg << 1) & 0xFF

            ireg.next = concat(ireg[7:0], spibus.mosi)
            bitcnt.next = bitcnt + 1
            if bitcnt == (8-1):
                bitcnt.next = 0
                b2.next = 8
                icap.next = concat(ireg[7:0], spibus.mosi)
            else:
                b2.next = 0

    # synchronize the SCK domain to the clock domain
    syncro(clock, icap, icaps)
    syncro(clock, b2, b3)

    gotit = Signal(bool(0))

    @always(clock.posedge)
    def beh_io_capture():
        # default no writes
        readpath.write.next = False
        writepath.read.next = False

        if b3 == 0:
            gotit.next = False
        elif b3 == 8 and not gotit:
            readpath.write.next = True
            readpath.write_data.next = icaps
            gotit.next = True
            ocap.next = writepath.read_data
            if not writepath.empty:
                writepath.read.next = True

    return myhdl.instances()
