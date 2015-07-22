
from myhdl import *
import _fpgalink_fx2 as fl

def comm_fpga_fx2_v2(
    clk_in,
    reset_in,
    fx2FifoSel_out,
    fx2Data_in,
    fx2Data_out,
    fx2Data_sel,
    fx2Read_out,
    fx2GotData_in,
    fx2Write_out,
    fx2GotRoom_in,
    fx2PktEnd_out,
    chanAddr_out,
    h2fData_out,
    h2fValid_out,
    h2fReady_in,
    f2hData_in,
    f2hValid_in,
    f2hReady_out
    ):
    """ Original port definition
    This module bridges the "original" port mapping to the MyHDL
    version.    
    """
    clock,reset,fx2_bus,fl_bus = fl.get_interfaces()

    # assign the ports to the busses
    fx2_bus.fifosel = fx2FifoSel_out
    fx2_bus.data_i = fx2Data_in
    fx2_bus.data_o = fx2Data_out
    fx2_bus.data_t = fx2Data_sel
    
    # get the fpgalink module
    g = fl.fpgalink_fx2(clk_in, reset_in, fx2_bus, fl_bus)

    return g

def comm_fpga_fx2_v1_stub(
    clk_in,
    reset_in,
    fx2FifoSel_out,
    fx2Data_in,
    fx2Data_out,
    fx2Data_sel,
    fx2Read_out,
    fx2GotData_in,
    fx2Write_out,
    fx2GotRoom_in,
    fx2PktEnd_out,
    chanAddr_out,
    h2fData_out,
    h2fValid_out,
    h2fReady_in,
    f2hData_in,
    f2hValid_in,
    f2hReady_out
    ):
    """ A stub for the Verilog cosimulation
    The following does absolutely nothing except let the converter know what
    ports are inputs and which arre outputs.
    """

    @always(clk_in.posedge, reset_in.negedge)
    def hdl():
        if fx2GotData_in or fx2GotRoom_in or h2fReady_in or f2hValid_in \
               or fx2Data_in == 0 or f2hData_in == 0 :
            fx2Data_out.next = 2
            fx2Data_sel.next = False
            fx2FifoSel_out.next = True
            fx2Read_out.next = True
            fx2Write_out.next = True
            fx2PktEnd_out.next = True
            chanAddr_out.next = True
            h2fData_out.next = 3
            h2fValid_out.next = True
            f2hReady_out.next = True            
            

    return hdl

def convert(dir=None):
    clk_in = Signal(bool(0))
    reset_in = ResetSignal(bool(0), active=0, async=True)
    fx2FifoSel_out = Signal(bool(0))
    #fxData_io
    fx2Data_in = Signal(intbv(0)[8:])
    fx2Data_out = Signal(intbv(0)[8:])
    fx2Data_sel = Signal(bool(0))
    fx2Read_out = Signal(bool(0))
    fx2GotData_in = Signal(bool(0))
    fx2Write_out = Signal(bool(0))
    fx2GotRoom_in = Signal(bool(0))
    fx2PktEnd_out = Signal(bool(0))
    chanAddr_out = Signal(intbv(0)[7:])
    h2fData_out = Signal(intbv(0)[8:])
    h2fValid_out = Signal(bool(0))
    h2fReady_in = Signal(bool(0))
    f2hData_in = Signal(intbv(0)[8:])
    f2hValid_in = Signal(bool(0))
    f2hReady_out = Signal(bool(0))

    # create the default tb_* to interface to the original Verilog module
    toVerilog(comm_fpga_fx2_v1_stub, clk_in, reset_in, fx2FifoSel_out,
              fx2Data_in, fx2Data_out, fx2Data_sel,
              fx2Read_out, fx2GotData_in, fx2Write_out, fx2GotRoom_in, fx2PktEnd_out,
              chanAddr_out, h2fData_out, h2fValid_out, h2fReady_in, f2hData_in,
              f2hValid_in, f2hReady_out)

    # Convert the MyHDL with the original port names
    toVerilog(comm_fpga_fx2_v2, clk_in, reset_in, fx2FifoSel_out,
              fx2Data_in, fx2Data_out, fx2Data_sel,
              fx2Read_out, fx2GotData_in, fx2Write_out, fx2GotRoom_in, fx2PktEnd_out,
              chanAddr_out, h2fData_out, h2fValid_out, h2fReady_in, f2hData_in,
              f2hValid_in, f2hReady_out)

    toVHDL(comm_fpga_fx2_v2, clk_in, reset_in, fx2FifoSel_out,
           fx2Data_in, fx2Data_out, fx2Data_sel,
           fx2Read_out, fx2GotData_in, fx2Write_out, fx2GotRoom_in, fx2PktEnd_out,
           chanAddr_out, h2fData_out, h2fValid_out, h2fReady_in, f2hData_in,
           f2hValid_in, f2hReady_out)    
    

if __name__ == '__main__':
    convert()
    
