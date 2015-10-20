
from myhdl import Signal, intbv, concat, always
from . import SERDESInterface


def input_serdes(serdes_intf):
    """
    """
    assert isinstance(serdes_intf, SERDESInterface)

    mods = []
    nbits = serdes_intf.number_of_bits
    hbits = nbits//2
    serial_in = serdes_intf.serial
    sclk, pclk, data = serdes_intf.get_signals()

    bcnt = Signal(intbv(0, min=0, max=nbits))
    input_reg = Signal(intbv(0)[nbits:])
    capture_reg = Signal(intbv(0)[nbits:])
    _pclk = Signal(bool(0))

    # get the serial input from the diff signals
    #mods += serdes_intf.input_buffer(serial_in)

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

    mods += (rtl_input_capture, rtl_data,)

    return mods


def input_serdes_bank(serdes_intf_list):
    assert isinstance(serdes_intf_list, (list, tuple,))

    mods = []
    for intf in serdes_intf_list:
        mods += input_serdes(intf)

    return mods
