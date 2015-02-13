

from myhdl import *

def fpga_logic_ex1(clock, reset, fl_bus):
    """
    Some simple logic to emulate FPGA logic which interfaces
    with the fpgalink module.

       fl_bus1 - MyHDL model
       fl_bus2 - original fpgalink Verilog
       fl_bus3 - MyHDL converted Verilog
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~
    # The following is a simple FPGA logic which interfaces with
    # the fpgalink module
    freg = [Signal(intbv(0)[8:]) for ii in range(4)]
    checksum = Signal(intbv(0)[16:])
    
    # local bus reference (work around until @always_comb attribute
    # bug is fixed.
    f2hValid_in = fl_bus.valid_i
    h2fReady_in = fl_bus.ready_i
    h2fValid_out = fl_bus.valid_o
    chanAddr_out = fl_bus.chan_addr
    f2hData_in = fl_bus.data_i
    h2fData_out = fl_bus.data_o
    
    @always_comb
    def tb_assigns():
        f2hValid_in.next = True
        h2fReady_in.next = True

        if chanAddr_out == 0:
            f2hData_in.next = 0xCE 
        elif chanAddr_out == 1:
            f2hData_in.next = freg[0]
        elif chanAddr_out == 2:
            f2hData_in.next = freg[1]
        elif chanAddr_out == 3:
            f2hData_in.next = freg[2]
        elif chanAddr_out == 4:
            f2hData_in.next = freg[3]
        elif chanAddr_out == 5:
            f2hData_in.next = checksum[16:8]
        elif chanAddr_out == 6:
            f2hData_in.next = checksum[8:0]
        else:
            f2hData_in.next = 0

    
    @always(clock.posedge, reset.negedge)
    def tb_checksum():
        if not reset:
            checksum.next = 0
            for ii in range(4):
                freg[ii].next = 0
        else:
            if h2fValid_out:
                if chanAddr_out >= 1 and chanAddr_out < 5:
                    freg[chanAddr_out-1].next = h2fData_out
                    #print('    setting chanAddr %d to %d' % (chanAddr_out, h2fData_out))
                    

    return tb_assigns, tb_checksum
