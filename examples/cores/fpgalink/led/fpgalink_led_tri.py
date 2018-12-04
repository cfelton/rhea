
from myhdl import *
from rhea.cores.usb_ext import fl_fx2
from rhea.cores.usb_ext import fpgalink_fx2

def tristate(dio, din, dout, dsel):
    dout = dio.driver()
    @always(dsel)
    def hdl():
        pass
    dio.driven = "wire"
    din.driven = "wire"
    return hdl
tristate.verilog_code = """
//module tristate(
//   inout  [7:0] dio,
//   input  [7:0] din,
//   output [7:0] dout,
//   input  [7:0] dsel):
   assign din = dio;
   assign dio = dsel ? dout : 8'bz;
//endmodule
"""

def fpgalink_led(    

    # ~~ FX2 interface signals ~~
    IFCLK,     # 48 MHz clock from FX2 
    RST,       # active low async reset 
    SLWR,      # active low write strobe
    SLRD,      # active low read strobe
    SLOE,      # active low output enable
    FDIO,      # bi-directional data bus
    ADDR,      # 2bit address (fifo select)
    FLAGA,     # not used
    FLAGB,     # gotroom
    FLAGC,     # gotdata
    FLAGD,     # not used
    PKTEND,    # submit partial (less than 512)
    
    # ~~ peripherals interfaces ~~
    leds       # external LEDs
    ):
    """
    """

    
    clock,reset,fx2_bus,fl_bus = fl_fx2.get_interfaces()
    clock = IFCLK
    reset = RST
    din = fx2_bus.data_i
    dout = fx2_bus.data_o
    dsel = fx2_bus.data_t
    fx2_bus.gotdata = FLAGC
    fx2_bus.gotroom = FLAGB
    fx2_bus.write = SLWR
    fx2_bus.read = SLRD
    #SLOE = SLRD now shadowed signals for conversion
    fx2_bus.pktend = PKTEND

    # instantiate the fpgalink interface
    g_fli = fpgalink_fx2(clock, reset, fx2_bus, fl_bus)
    g_tri = tristate(FDIO, din, dout, dsel)

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
        ADDR.next[0] = fifosel
        ADDR.next[1] = True
        SLOE.next = SLRD
        f2hValid_in.next = True
        h2fReady_in.next = True

        leds.next = lreg

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
        


    return g_fli, g_tri, hdl_fl, hdl_assigns


def convert():
    FDIO = TristateSignal(intbv(0)[8:])
    SLWR,SLRD,SLOE = [Signal(bool(0)) for ii in range(3)]
    FLAGA,FLAGB,FLAGC,FLAGD = [Signal(bool(0)) for ii in range(4)]
    ADDR = Signal(intbv(0)[2:])
    IFCLK = Signal(bool(0))
    RST = ResetSignal(bool(1), active=0, isasync=True)
    leds = Signal(intbv(0)[8:])
    PKTEND = Signal(bool(0))

    toVerilog(fpgalink_led, IFCLK, RST, SLWR, SLRD, SLOE,
              FDIO, ADDR, FLAGA, FLAGB, FLAGC, FLAGD, PKTEND,
              leds)

if __name__ == '__main__':
    convert()
    
