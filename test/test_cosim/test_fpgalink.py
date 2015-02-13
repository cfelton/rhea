

import os
import time
import argparse

from myhdl import *

from mn.models.usbext import FpgaLinkHost
from mn.cores.usbext import fpgalink
from mn.cores.usbext import m_fpgalink_fx2

# Example FPGA logic which interfaces with fpgalink
from _fpgalink_logic_ex1 import m_fpga_logic_ex1

from _test_utils import *

def flcosim(clock, reset, fx2_bus, fl_bus):
    f1 = '../mn/cores/usbext/fpgalink/comm_fpga_fx2_v1.v'
    f2 = '../mn/cores/usbext/fpgalink/comm_fpga_fx2_v2.v'
    f3 = '../mn/cores/usbext/fpgalink/tb_comm_fpga_fx2_m.v'
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
        
        
def test_fpgalink(args):
    """
        flbus1 - MyHDL model
        flbus2 - original fpgalink Verilog
        flbus3 - MyHDL converted Verilog
    """
    # Get the FX2 emulations / host API and busses
    fl = FpgaLinkHost(Verbose=True)
    clock,reset,fx2bus1,flbus1 = fpgalink.get_interfaces()
    c,r,fx2bus2,flbus2 = fpgalink.get_interfaces()

    fx2ext = fl.GetFx2Bus()           # get the FX2 bus
    clock = fx2ext.IFCLK
    reset = fx2ext.RST
    # connect the busses
    gm = map_ext_int(clock, reset, fx2ext, fx2bus1) 
    # only one model driving the bus, connect the busses
    fx2bus2.data_i = fx2bus1.data_i
    fx2bus2.gotdata = fx2bus1.gotdata
    fx2bus2.gotroom = fx2bus1.gotroom

    # get the two HDL versions (MyHDL and Verilog)    
    tb_dut = traceSignals(m_fpgalink_fx2, clock, reset, fx2bus1, flbus1)
    tb_fl1 = m_fpga_logic_ex1(clock, reset, flbus1)
    
    if args.cosim:
        tb_cosim = flcosim(clock, reset, fx2bus2, flbus2)
        tb_fl2 = m_fpga_logic_ex1(clock, reset, flbus2)
    else:
        tb_cosim = ()
        tb_fl2 = ()
        
    g = (tb_dut, tb_cosim, tb_fl1, tb_fl2, gm)

    # Start up the simulaiton using the FpgaLinkHost
    fl.setup(fx2ext, g=g)          # setup the simulation
    fl.start()                      # start the simulation

    assert fx2bus1.data_i is fx2ext.FDO
    
    # ~~~~~~~~~~~~~~~
    # Test stimulus
    fl.Reset()
    assert fx2bus1.data_i is fx2ext.FDO
    
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--cosim', action='store_true', default=False,
                        help='Run cosimulation with verilog version of fpgalink requires icarus')
    args = parser.parse_args()
    tb_clean_vcd('m_fpgalink_fx2')
    test_fpgalink(args)
    
