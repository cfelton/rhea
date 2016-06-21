
import myhdl
from myhdl import (Signal, intbv, concat, always, always_comb)

from . import SERDESInterface


@myhdl.block
def device_serdes_output_prim(serdes):
    assert isinstance(serdes, SERDESInterface)
    clockser, clockpar = (serdes.clock_serial,
                          serdes.clock_parallel)
    nbits = serdes.number_of_bits
    hold = Signal(intbv(0)[nbits:])
    bcnt = Signal(intbv(0, min=0, max=nbits))
    tic = Signal(bool(0))
    tik = Signal(bool(0))
    toc = Signal(bool(0))

    @always(clockpar.posedge)
    def rtl_par():
        hold.next = serdes.data
        tic.next = not tic

    @always(clockser.posedge)
    def rtl_tic():
        tik.next = tic

    @always_comb
    def rtl_toc():
        toc.next = tic != tik

    @always(clockser.posedge)
    def rtl_ser():
        serdes.serial.next = hold[bcnt]

        if bcnt == nbits-1:
            bcnt.next = 0
        else:
            bcnt.next = bcnt + 1

        assert bcnt == 0 and toc, "bit count not synced"

    return rtl_par, rtl_tic, rtl_toc, rtl_ser


@myhdl.block
def device_serdes_input_prim(serdes):
    """
    """
    assert isinstance(serdes, SERDESInterface)

    nbits = serdes.number_of_bits
    hbits = nbits//2
    serial_in = serdes.serial
    sclk, pclk, data = serdes.get_signals()

    bcnt = Signal(intbv(0, min=0, max=nbits))
    input_reg = Signal(intbv(0)[nbits:])
    capture_reg = Signal(intbv(0)[nbits:])
    _pclk = Signal(bool(0))

    # get the serial input from the diff signals
    # g = serdes.input_buffer(serial_in)
    # mods.append(g)

    # capture the input serial stream
    @always(sclk.posedge)
    def rtl_input_capture():
        input_reg.next = concat(input_reg[nbits-1:1], serial_in)
        if bcnt == nbits-1:
            bcnt.next = 0
            capture_reg.next = input_reg
            _pclk.next = True
        elif bcnt == hbits:
            _pclk.next = False

    @always(pclk.posedge)
    def rtl_data():
        data.next = capture_reg

    return rtl_input_capture, rtl_data
