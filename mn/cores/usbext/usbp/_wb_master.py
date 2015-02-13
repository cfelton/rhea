#
# Copyright (c) 2006-2013 Christopher L. Felton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module is the master interface to the wishbone bus.  This module receives
a command packet from an external interface (USB VCOM, UART, etc).

The flow is always a single command packe received and ACK'd with a command
packet response.  Only 1 command should be issued at a time.

"""

from myhdl import *
from _wb_master_cmd import wb_master_cmd
from ...fifo import fifo_async



def wb_master(
    clk,             # system sync clock (system / wishbone side)
    reset,           # system reset (FPGA sync reset)

    # ---- Wishbone Bus ----
    wb_clk_o,        # wishbone sync clock == clk
    wb_rst_o,        # wishbone reset, active low
    wb_dat_o,        # data bus out
    wb_dat_i,        # data bus in
    wb_adr_o,        # address bus out
    wb_cyc_o,        # bus cycle in process
    wb_ack_i,        # normal termination of bus cycle
    wb_err_i,        # bus cycle ended in error
    wb_lock_o,       # non interruptable bus cycle, == cyc_o
    wb_rty_i,        # retry bus cycle
    wb_sel_o,        # valid bytes, only byte bus
    wb_stb_o,        # strobe output
    wb_we_o,         # write enable

    # FIFO interface, FIFO perspective
    exti_clk,        # external interface clock        
    
    wb_fifo_wr,      # input  FIFO write strobe
    wb_fifo_full,    # output FIFO status
    wb_fifo_di,      # input  FIFO data out from external interface
    
    wb_fifo_rd,      # input  FIFO read strobe
    wb_fifo_empty,   # output FIFO status
    wb_fifo_do,      # output Data to external interface
    wb_fifo_do_vld,  # output Data valid strobe

    wb_efifo_empty,  #
    wb_cmd_in_prog,  # output currently receiving a command
    loopback,        # output 
    status_regs,

    C_REVISION   = 0,   # Current revision (saved to a register)
    C_WB_DAT_SZ  = 8,   # Wishbone data bus size (8 bit only tested)
    C_WB_ADR_SZ  = 16,  # Wishbone address bus size (16 bits only tested)
    C_BASE_ADDR  = 0    # Base address for the internal registers.
    ):
    """Wishbone master controller
    
    """    

    wb_go    = Signal(False)
    wb_rd    = Signal(False)
    wb_wr    = Signal(False)
    to_ack   = Signal(False)    # from wb_master_cmd

    fifo_rd    = Signal(False)
    fifo_wr    = Signal(False)
    fifo_empty = Signal(False)
    fifo_full  = Signal(False)
    i_fifo_rd  = Signal(False)
    i_fifo_wr  = Signal(False)

    fifo_di  = Signal(intbv(0)[C_WB_DAT_SZ:])
    fifo_do  = Signal(intbv(0)[C_WB_DAT_SZ:])
    
    wb_addr  = Signal(intbv(0)[C_WB_ADR_SZ:])
    wb_dat   = Signal(intbv(0)[C_WB_DAT_SZ:])
    
    i_dat_i  = Signal(intbv(0)[C_WB_DAT_SZ:])  # internal or'd bus
    i_ack_i  = Signal(False)
    
    cs_dat_i = Signal(intbv(0)[C_WB_DAT_SZ:])  # internal register read bus
    cs_ack_i = Signal(False)
    
    wb_ctrl0 = Signal(intbv(0)[8:])
    wb_stat0 = Signal(intbv(0)[8:])
    wb_stat1 = Signal(intbv(0)[8:])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Two FIFOs exist, the FIFOs are only 32 byes
    #   1. Ext.Write --> | FIFO | --> Internal.Read
    #   2. Ext.Read  --> | FIFO | --> Internal.Write
    wb_pempty   = Signal(False)
    fifo_pempty = Signal(False)
    fifo_do_vld = Signal(False)
        
    FIFO_A = fifo_async(reset,  
                        exti_clk, wb_fifo_wr, wb_fifo_full, wb_fifo_di,
                        clk, i_fifo_rd, fifo_empty, fifo_pempty, fifo_do, fifo_do_vld,
                        C_DSZ=8, C_ASZ=4)

    FIFO_B = fifo_async(reset,  
                        clk, i_fifo_wr, fifo_full, fifo_di,
                        exti_clk, wb_fifo_rd, wb_fifo_empty, wb_pempty, wb_fifo_do, wb_fifo_do_vld,
                        C_DSZ=8, C_ASZ=4)

    # Wishbone bus controller
    wb_cmd_ready = Signal(False)
    @always_comb
    def rtl_cmd_ready():
        wb_cmd_ready.next = not fifo_empty and wb_efifo_empty # (not empty)

    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Get data from FIFO
    # if data in the FIFO, read the data out, or if data is being
    # read from, echo back the complete command.  In the write case the
    # exact same data will be echo'd back.  In the read case the byte data
    # will be replaced with the data read from the wishbone bus.

    @always_comb
    def rtl1():
        wb_clk_o.next    = clk         
        wb_rst_o.next    = not reset  
        wb_adr_o.next    = wb_addr
        wb_dat_o.next    = wb_dat
        
        i_dat_i.next     = wb_dat_i | cs_dat_i
        i_ack_i.next     = wb_ack_i or cs_ack_i
        i_fifo_rd.next  = fifo_rd and not fifo_empty

    @always_comb
    def rtl2():
        if i_ack_i or to_ack: 
            i_fifo_wr.next = fifo_wr and not fifo_full
            if wb_rd:
                fifo_di.next   = i_dat_i
            else:
                fifo_di.next   = wb_dat_o
        elif not wb_rd and not wb_wr:
            i_fifo_wr.next  = fifo_wr and not fifo_empty and fifo_do_vld
            fifo_di.next    = fifo_do
        else:
            i_fifo_wr.next  = False

    @always(clk.posedge)
    def rtl3():
        if reset:
            fifo_wr.next = False
            fifo_rd.next = False
        else:
            # @todo this should be simplified
            if wb_cmd_ready or wb_go :
                if not wb_go:
                    fifo_rd.next = True
                    fifo_wr.next = True
                elif wb_go and wb_stb_o:
                    fifo_rd.next = True
                    fifo_wr.next = True

            else:
                fifo_rd.next = False
                fifo_wr.next = False


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    wb_cmd = wb_master_cmd(clk, reset, fifo_do, fifo_do_vld, fifo_empty,
                           wb_go, wb_rd,
                           wb_wr, wb_addr, wb_dat, i_ack_i, wb_cmd_in_prog,
                           to_ack)


    @always_comb
    def rtl4():
        if wb_go and (wb_wr or wb_rd):
            wb_cyc_o.next   = True
            wb_lock_o.next  = False
            wb_stb_o.next   = True
            wb_we_o.next    = wb_wr

        else:
            wb_cyc_o.next  = False
            wb_lock_o.next = False
            wb_stb_o.next  = False
            wb_we_o.next   = False

        # byte select
        if wb_addr[1:0] == 0:
            wb_sel_o.next  = 1
        elif wb_addr[1:0] == 1:
            wb_sel_o.next  = 2
        elif wb_addr[1:0] == 2:
            wb_sel_o.next  = 4
        elif wb_addr[1:0] == 3:
            wb_sel_o.next  = 8

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Internal Wishbone Accessible Registers
    #  Offset      Description
    #   0-3        Revision
    #   4-7        Control
    #   8-11       Status
    
    # Control Register
    @always(clk.posedge)
    def rtl5():
        if reset:
            wb_ctrl0.next = 0
        else:
            if wb_addr == C_BASE_ADDR+4 and wb_we_o:
                wb_ctrl0.next = wb_dat_o


    base_sel = Signal(False)
    wb_acc   = Signal(False)
    end      = len(status_regs)

    MIN_ADDR = C_BASE_ADDR
    MAX_ADDR = C_BASE_ADDR + end
    
    @always(wb_clk_o.posedge)
    def rtl6():        
        # Revision Value (32-bits)
        if wb_addr == C_BASE_ADDR:
            cs_dat_i.next = (C_REVISION >> 24) & 0xFF
        elif wb_addr == C_BASE_ADDR+1:
            cs_dat_i.next = (C_REVISION >> 16) & 0xFF
        elif wb_addr == C_BASE_ADDR+2:
            cs_dat_i.next = (C_REVISION >> 8)  & 0xFF
        elif wb_addr == C_BASE_ADDR+3:
            cs_dat_i.next = (C_REVISION >> 0)  & 0xFF
        # Control Register (32 bits)
        elif wb_addr == C_BASE_ADDR+4:
            cs_dat_i.next = wb_ctrl0
        # Status Register (32 bits)
        elif wb_addr == C_BASE_ADDR+8:
            cs_dat_i.next = wb_stat0
        elif wb_addr == C_BASE_ADDR+9:
            cs_dat_i.next = wb_stat1

        # Misc status and count registers
        elif wb_addr >= C_BASE_ADDR+0x10 and wb_addr < C_BASE_ADDR+0x10+end:
            for ii in range(end):
                if wb_addr == C_BASE_ADDR+10+ii:
                    cs_dat_i.next = status_regs[ii]
                else:
                    # @todo Need something for the else!! 
                    cs_dat_i.next = 0
        else:
            cs_dat_i.next = 0

        loopback.next = wb_ctrl0[0]


    @always_comb
    def rtl_wb1():
        wb_acc.next = wb_cyc_o & wb_stb_o

        if wb_addr >= MIN_ADDR and wb_addr < MAX_ADDR:
            base_sel.next = True
        else:
            base_sel.next = False


    @always(wb_clk_o.posedge)
    def rtl_wb2():
        if not wb_rst_o:
            cs_ack_i.next = False
        else:
            if base_sel:
                cs_ack_i.next = wb_acc
            else:
                cs_ack_i.next = False

            
    @always_comb
    def rtl_status():
        wb_stat0.next[0] = wb_fifo_empty
        wb_stat0.next[1] = wb_fifo_full
        wb_stat0.next[2] = wb_fifo_wr
        wb_stat0.next[3] = wb_fifo_rd
        wb_stat0.next[4] = wb_fifo_do_vld
        wb_stat0.next[5] = wb_cmd_ready
        wb_stat0.next[6] = wb_cmd_in_prog


    return instances()

