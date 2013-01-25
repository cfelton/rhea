

import os
import time

from myhdl import *

from mn.cores.usb_ext import FpgaLinkHost
from mn.cores.usb_ext import fl_fx2
from mn.cores.usb_ext import fpgalink_fx2

# Example FPGA logic which interfaces with fpgalink
from fpgalink_logic_ex1 import fpga_logic_ex1

def flcosim(clock, reset, fx2_bus, fl_bus):
    f1 = '../mn/cores/usb_ext/fpgalink/comm_fpga_fx2_v1.v'
    f2 = '../mn/cores/usb_ext/fpgalink/comm_fpga_fx2_v2.v'
    f3 = '../mn/cores/usb_ext/fpgalink/tb_comm_fpga_fx2_m.v'
    assert os.path.isfile(f1)
    assert os.path.isfile(f2)    
    assert os.path.isfile(f3)

    cmd = 'iverilog -o fpgalink %s %s %s' % (f1, f2, f3)
    os.system(cmd)
    cmd = 'vvp -m ./myhdl.vpi fpgalink'
    cg = Cosimulation(cmd,
                      clk_in=clock,
                      reset_in=reset,
                      fx2FifoSel_out=fx2_bus.fifosel,
                      fx2Data_in=fx2_bus.data_i,
                      fx2Data_out=fx2_bus.data_o,
                      fx2Data_sel=fx2_bus.data_t,
                      fx2Read_out=fx2_bus.read,
                      fx2GotData_in=fx2_bus.gotdata,
                      fx2Write_out=fx2_bus.write,
                      fx2GotRoom_in=fx2_bus.gotroom,
                      fx2PktEnd_out=fx2_bus.pktend,
                      chanAddr_out=fl_bus.chan_addr,
                      h2fData_out=fl_bus.data_o,
                      h2fValid_out=fl_bus.valid_o,
                      h2fReady_in=fl_bus.ready_i,
                      f2hData_in=fl_bus.data_i,
                      f2hValid_in=fl_bus.valid_i,
                      f2hReady_out=fl_bus.ready_o
                     )

    return cg


def map_ext_int(clock, reset, fx2_ext, fx2_bus):
    """ Map the FX2 signals to the internally defined FX2 bus
    """
    fx2_bus.data_i = fx2_ext.FDO
    fx2_bus.data_o = fx2_ext.FDI
    fx2_bus.read = fx2_ext.SLRD
    fx2_ext.SLOE = fx2_ext.SLRD
    fx2_bus.gotdata = fx2_ext.FLAGC
    fx2_bus.write = fx2_ext.SLWR
    fx2_bus.gotroom = fx2_ext.FLAGB
    #fx2_bus.pktend = fx2_ext.PKTEND

    faddr = fx2_ext.ADDR
    fsel = fx2_bus.fifosel
    @always_comb
    def tb_assign():
        faddr.next[0] = 0
        faddr.next[1] = int(fsel)

    sFDO = Signal(intbv(0)[8:])
    FDO = fx2_ext.FDO
    @always(clock.posedge)
    def tb_monitor():
        if sFDO != FDO:
            #print(" FDO %x data_i %x" % (fx2_ext.FDO, fx2_bus.data_i))
            sFDO.next = FDO

        #if fx2_ext.FDO != 0 or fx2_bus.data_i != 0:
        #    print('%8d FDO %x data_i %x' % (now(), fx2_ext.FDO, fx2_bus.data_i))
            
    return tb_assign, tb_monitor
        
    
    
def test_fpgalink():

    # Get the FX2 emulations / host API and busses
    fl = FpgaLinkHost(Verbose=True)
    clock,reset,fx2_bus1,fl_bus1 = fl_fx2.get_interfaces()
    c,r,fx2_bus2,fl_bus2 = fl_fx2.get_interfaces()

    fx2_ext = fl.GetFx2Bus()           # get the FX2 bus
    clock = fx2_ext.IFCLK
    reset = fx2_ext.RST
    # connect the busses
    gm = map_ext_int(clock, reset, fx2_ext, fx2_bus1) 
    # only one model driving the bus, connect the busses
    fx2_bus2.data_i = fx2_bus1.data_i
    fx2_bus2.gotdata = fx2_bus1.gotdata
    fx2_bus2.gotroom = fx2_bus1.gotroom

    # get the two HDL versions (MyHDL and Verilog)
    tb_dut = traceSignals(fpgalink_fx2, clock, reset, fx2_bus1, fl_bus1)
    tb_cosim = flcosim(clock, reset, fx2_bus2, fl_bus2)
    tb_fl1 = fpga_logic_ex1(clock, reset, fl_bus1)
    tb_fl2 = fpga_logic_ex1(clock, reset, fl_bus2)
    g = (tb_dut, tb_cosim, tb_fl1, tb_fl2, gm)

    # Start up the simulaiton using the FpgaLinkHost
    fl.setup(fx2_ext, g=g)          # setup the simulation
    fl.start()                      # start the simulation

    assert fx2_bus1.data_i is fx2_ext.FDO
    
    # ~~~~~~~~~~~~~~~
    # Test stimulus
    fl.Reset()
    assert fx2_bus1.data_i is fx2_ext.FDO
    
    fl.WriteChannel(1, [9])
    fl.WriteChannel(2, [8])
    fl.WriteChannel(3, [7])
    fl.WriteChannel(4, [6])
    bb = [ii for ii in (0xFE, 0xED, 0xFA, 0xCE)]
    bb[0] = fl.ReadChannel(1, 1)
    bb[1] = fl.ReadChannel(2, 1)
    bb[2] = fl.ReadChannel(3, 1)
    bb[3] = fl.ReadChannel(4, 1)
    print(bb)

    # ~~~~~~~~~~~~~~~
    # Stop simulation
    fl.stop()
    time.sleep(1)

if __name__ == '__main__':
    test_fpgalink()
    
