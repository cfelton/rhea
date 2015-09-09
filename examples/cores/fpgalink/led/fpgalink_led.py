
from myhdl import *
from rhea.cores.usb_ext import fl_fx2
from rhea.cores.usb_ext import fpgalink_fx2


def fpgalink_led(    
    # ~~ FX2 interface signals ~~
    IFCLK,     # 48 MHz clock from FX2 
    RST,       # active low async reset 
    SLWR,      # active low write strobe
    SLRD,      # active low read strobe
    SLOE,      # active low output enable
    FDI,       # input data bus
    FDO,       # output data bus
    FDS,       # data select
    ADDR,      # 2bit address (fifo select)
    FLAGA,     # not used
    FLAGB,     # gotroom
    FLAGC,     # gotdata
    FLAGD,     # not used
    PKTEND,    # submit partial (less than 512)    
    # ~~ peripherals interfaces ~~
    LEDS       # external LEDs
    ):
    """
    """

    # get the local references for the top-level 
    clock,reset,fx2_bus,fl_bus = fl_fx2.get_interfaces()
    clock = IFCLK
    reset = RST
    fx2_bus.data_i = FDI
    fx2_bus.data_o = FDO
    fx2_bus.data_t = FDS
    fx2_bus.gotdata = FLAGC
    fx2_bus.gotroom = FLAGB
    fx2_bus.write = SLWR
    fx2_bus.read = SLRD
    #SLOE = SLRD now shadowed signals for conversion
    fx2_bus.pktend = PKTEND

    # instantiate the fpgalink interface
    g_fli = fpgalink_fx2(clock, reset, fx2_bus, fl_bus)

    # ~~~~~~
    lreg = Signal(intbv(0)[8:])
    f2hValid_in = fl_bus.valid_i
    h2fReady_in = fl_bus.ready_i
    h2fValid_out = fl_bus.valid_o
    chanAddr_out = fl_bus.chan_addr
    f2hData_in = fl_bus.data_i
    h2fData_out = fl_bus.data_o

    fifosel = fx2_bus.fifosel
    @always_comb
    def hdl_assigns():
        ADDR.next[0] = False
        ADDR.next[1] = fifosel
        SLOE.next = SLRD
        f2hValid_in.next = True
        h2fReady_in.next = True

        LEDS.next = lreg

        if chanAddr_out == 0:
            f2hData_in.next = 0xCE 
        elif chanAddr_out == 1:
            f2hData_in.next = lreg
        else:
            f2hData_in.next = 0x55


    @always_seq(clock.posedge, reset=reset)
    def hdl_fl():
        if h2fValid_out and chanAddr_out == 1:
            lreg.next = h2fData_out
        

    return g_fli, hdl_fl, hdl_assigns


def convert():
    FDO = Signal(intbv(0)[8:])
    FDI = Signal(intbv(0)[8:])
    FDS = Signal(bool(0))
    SLWR,SLRD,SLOE = [Signal(bool(0)) for ii in range(3)]
    FLAGA,FLAGB,FLAGC,FLAGD = [Signal(bool(0)) for ii in range(4)]
    ADDR = Signal(intbv(0)[2:])
    IFCLK = Signal(bool(0))
    RST = ResetSignal(bool(1), active=0, async=True)
    LEDS = Signal(intbv(0)[8:])
    PKTEND = Signal(bool(0))

    toVerilog(fpgalink_led, IFCLK, RST, SLWR, SLRD, SLOE,
              FDI, FDO, FDS, ADDR, FLAGA, FLAGB, FLAGC, FLAGD, PKTEND,
              LEDS)

if __name__ == '__main__':
    convert()
    
