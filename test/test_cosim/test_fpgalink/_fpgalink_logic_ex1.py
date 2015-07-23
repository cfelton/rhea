#
# Copyright (c) 2006-2013 Christopher L. Felton
#

from myhdl import *

def m_fpga_logic_ex1(clock, reset, flbus):
    """
    Some simple logic to emulate FPGA logic which interfaces
    with the fpgalink module.
    """
    # ~~~~~~~~~~~~~~~~~~~~~~~~
    # The following is a simple FPGA logic which interfaces with
    # the fpgalink module
    freg = [Signal(intbv(0)[8:]) for ii in range(4)]
    checksum = Signal(intbv(0)[16:])
        
    @always_comb
    def tb_assigns():
        flbus.valid_i.next = True
        flbus.ready_i.next = True

        if flbus.chan_addr == 0:
            flbus.data_i.next = 0xCE 
        elif flbus.chan_addr == 1:
            flbus.data_i.next = freg[0]
        elif flbus.chan_addr == 2:
            flbus.data_i.next = freg[1]
        elif flbus.chan_addr == 3:
            flbus.data_i.next = freg[2]
        elif flbus.chan_addr == 4:
            flbus.data_i.next = freg[3]
        elif flbus.chan_addr == 5:
            flbus.data_i.next = checksum[16:8]
        elif flbus.chan_addr == 6:
            flbus.data_i.next = checksum[8:0]
        else:
            flbus.data_i.next = 0
    
    @always(clock.posedge, reset.negedge)
    def tb_checksum():
        if not reset:
            checksum.next = 0
            for ii in range(4):
                freg[ii].next = 0
        else:
            if flbus.valid_o:
                if flbus.chan_addr >= 1 and flbus.chan_addr < 5:
                    freg[flbus.chan_addr-1].next = flbus.data_o
                    #print('    setting chanAddr %d to %d' % (chanAddr_out, h2fData_out))
                    

    return tb_assigns, tb_checksum
