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
  This module is the USB interface.  It contains the FX2 slave FIFO
  interface.  This module is the bridge between the USB fifos, the internal
  wishbone bus, and the streaming FIFO interface.
  
  This module is also designed to translate between 2 different clock
  domains if needed.  The FX2 slave FIFO interface runs on the IFCLK (48MHz)
  clock.  The interal system clock can be a different clock rate.\
  
"""

import sys,os
from myhdl import *
from _wb_master import wb_master
from _fx2_sfifo import fx2_sfifo
from ...fifo import fifo_two_port_sync

#
class usbp(object):

    def __init__(self, *sigs, **parameters):

        # usbp internal registers
        self.C_VER_ADDR   = C_BASE_ADDR          # Version register
        self.C_CTL_ADDR   = C_BASE_ADDR + 4      # Control register, upto 4 bytes
        self.C_STS_ADDR   = C_BASE_ADDR + 8      # Status register, upto 4 bytes
        self.C_UFW_E_ADDR = C_BASE_ADDR + 0x10   # USB in FIFO write error
        self.C_LFW_E_ADDR = C_BASE_ADDR + 0x14   # Logic in FIFO write error
        self.C_LFR_E_ADDR = C_BASE_ADDR + 0x18   # Logic out FIFO read error
        self.C_UFR_E_ADDR = C_BASE_ADDR + 0x1C   # USB out FIFO read error

        

    def RTL(self, *sigs, **parameters):
        """usbp RTL definition
        """
        return usbp_wb(sigs, parameters)


# Standard HDL Function
def usbp_wb(
    reset,             # System reset    
    ifclk,             # IFCLK from FX2
    sys_clk,           # Internal FPGA clk,
    
    # ---- FX2 FIFO Interface ----
    FLAGA,             # EP2(OUT) Empty
    FLAGB,             # EP4(OUT) Empty
    FLAGC,             # EP6(IN)  Full
    FLAGD,             # EP8(IN)  Full
    SLOE,              # Output Enable, Slave FIFO
    SLRD,              # Read Signal
    SLWR,              # Write Signal
    FIFOADR,           # Which of the 4 FIFO currently interfacing with.                       
    PKTEND,            # Packet End, Tell FX2 to send data without FIFO Full
    FDI,               # Fifo Data In
    FDO,               # Fifo Data Out 
 
    # ---- Wishbone Bus ----
    #  Note clk_i signal has been excluded.  Using sys_clk input
    wb_clk_o,          # Sync clock == sys_clk
    wb_rst_o,          # Wishbone Reset
    wb_dat_o,          # Data bus out
    wb_dat_i,          # Data bus in
    wb_adr_o,          # Address bus out
    wb_cyc_o,          # Bus cycle in process
    wb_ack_i,          # Normal termination of bus cycle
    wb_err_i,          # Bus cycle ended in error
    wb_lock_o,         # Non interruptable bus cycle, == cyc_o
    wb_rty_i,          # Retry bus cycle
    wb_sel_o,          # Valid bytes, only byte bus
    wb_stb_o,          # Strobe output
    wb_we_o,           # Write Enable
    
    #  Wishbone signals not used.
    # wb_tgd_o,wb_tdg_i,wb_tga_o,wb_tgc_o
    
    # ---- Async FIFO Interface ----
    fifo_rd,           # Read Strobe
    fifo_do,           # FIFO data output
    fifo_do_vld,       # FIFO data output valid
    fifo_empty,        # Empty control signal
    fifo_wr,           # Write Strobe
    fifo_di,           # FIFO data input    
    fifo_full,         # Full control signal
    fifo_hold,         # Wait, enables complete packet etc.
    fifo_clr,          # Reset the data fifo
    loopback,          # Loopback, status to the top
    dbg = None,        # Run-time debug signals

    # ---- Parameters ----
    C_REVISION  = 0x12345678, # Revision  32 bit value
    C_WB_DAT_SZ = 8,          # Wishbone data width
    C_WB_ADR_SZ = 16,         # Wishbone address width
    C_BASE_ADDR = 0,          # Base Wishbone Address for internal regs
    C_INC_ERR_STAT = True     # Include error and status counters
    ):
    """USB (FX2 USB Controller) Interface
    
    """    

    # Async FIFO signals from FX2 interface, FX2 perspective
    # "di" data-in to FX2, "do" data-out from FX2
    fx2_wb_di      = Signal(intbv(0)[C_WB_DAT_SZ:])
    fx2_wb_di_vld  = Signal(False)
    fx2_wb_do      = Signal(intbv(0)[C_WB_DAT_SZ:])
    fx2_wb_full    = Signal(False)
    fx2_wb_empty   = Signal(True)
    fx2_wb_wr      = Signal(False)
    fx2_wb_rd      = Signal(False)
    
    fx2_fifo_di    = Signal(intbv(0)[C_WB_DAT_SZ:])
    fx2_fifo_di_vld = Signal(False)
    fx2_fifo_do    = Signal(intbv(0)[C_WB_DAT_SZ:])
    fx2_fifo_full  = Signal(False)
    fx2_fifo_empty = Signal(True)
    fx2_fifo_wr    = Signal(False)
    fx2_fifo_rd    = Signal(False)
        
    # External and looback async FIFO signals
    lp_fifo_di      = Signal(intbv(0)[C_WB_DAT_SZ:])
    lp_fifo_do      = Signal(intbv(0)[C_WB_DAT_SZ:])
    lp_fifo_do_vld  = Signal(False)
    lp_fifo_full    = Signal(False)
    lp_fifo_empty   = Signal(True)
    lp_fifo_wr      = Signal(False)
    lp_fifo_rd      = Signal(False)
    _lp_fifo_wr     = Signal(False)
    _lp_fifo_rd     = Signal(False)
    
    i_fifo_di      = Signal(intbv(0)[C_WB_DAT_SZ:])
    i_fifo_do      = Signal(intbv(0)[C_WB_DAT_SZ:])
    i_fifo_do_vld  = Signal(False)
    i_fifo_full    = Signal(False)
    i_fifo_empty   = Signal(True)
    i_fifo_wr      = Signal(False)
    i_fifo_rd      = Signal(False)

    
    fifo_rst = Signal(False)
    fifo_hwm = Signal(False)
    hwma = Signal(False)


    # Some debug registers counters
    err_wr_fxfifo      =  Signal(intbv(0)[32:])
    err_rd_fxfifo      =  Signal(intbv(0)[32:])
    err_wr_ififo       =  Signal(intbv(0)[32:])
    err_rd_ififo       =  Signal(intbv(0)[32:])
    d_in_cnt           =  Signal(intbv(0)[64:])
    d_out_cnt          =  Signal(intbv(0)[64:])
    wb_in_cnt          =  Signal(intbv(0)[64:])
    wb_out_cnt         =  Signal(intbv(0)[64:])
    
    # Fake out the conversion so that the collection of registers
    # looks like a memory.  Thought the ShadowSignals would make this OK??
    #  status_regs = [err_wr_fxfifo[32:24], err_wr_fxfifo[24:16], err_wr_fxfifo[16:8], err_wr_fxfifo[8:0],
    #                 err_rd_fxfifo[32:24], err_rd_fxfifo[24:16], err_rd_fxfifo[16:8], err_rd_fxfifo[8:0],
    #                 err_wr_ififo[32:24], err_wr_ififo[24:16], err_wr_ififo[16:8], err_wr_ififo[8:0],
    #                 err_rd_ififo[32:24], err_rd_ififo[24:16], err_rd_ififo[16:8], err_rd_ififo[8:0]]
    fake_mem = [Signal(intbv(0)[8:]) for ii in range(0x20)]
    status_regs = fake_mem
    
    wb_cmd_in_prog     = Signal(False)
    fx2_dbg            = Signal(intbv(0)[8:])
    ireset             = Signal(False)

    if dbg is not None:
        @always_comb
        def debug_sigs():
            dbg.next[0] = ireset
            dbg.next[1] = FLAGC
            dbg.next[2] = FLAGD
            dbg.next[3] = wb_cmd_in_prog
            dbg.next[4] = fx2_wb_empty
            dbg.next[5] = fx2_fifo_empty
            dbg.next[6] = fx2_wb_wr
            dbg.next[7] = 0
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Keep this module in reset until the FX2 is ready, the software
    # will have to make sure the IN endpoints are empty.
    @always(ifclk.posedge)
    def rtl1():
        if reset:
            ireset.next = True
        else:
            # FLAGD is not always cleared, not 100% reliable
            if not FLAGC: #and not FLAGD:
                ireset.next = False

   
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Slave FIFO Interface
    fx2 = fx2_sfifo(reset, ifclk,
                    # FX2 slave fifo control and data signals
                    FLAGA, FLAGB, FLAGC, FLAGD, SLOE,
                    SLRD, SLWR, FIFOADR, PKTEND, FDI, FDO,
                    # Wishbone data fifo signals
                    fx2_wb_di, fx2_wb_di_vld, fx2_wb_do, fx2_wb_full,
                    fx2_wb_empty, fx2_wb_wr, fx2_wb_rd,
                    # Stream data fifo signals
                    fx2_fifo_di, fx2_fifo_di_vld, fx2_fifo_do, fx2_fifo_full,
                    fx2_fifo_empty, fx2_fifo_wr, fx2_fifo_rd, fifo_hold, fifo_hwm,
                    # misc
                    wb_cmd_in_prog, fx2_dbg)
   
        
    wb_controller = wb_master(sys_clk, ireset, wb_clk_o, wb_rst_o, wb_dat_o, wb_dat_i,
                              wb_adr_o, wb_cyc_o, wb_ack_i, wb_err_i, wb_lock_o, wb_rty_i,
                              wb_sel_o, wb_stb_o, wb_we_o,
                              # From/To FX2
                              ifclk,
                              fx2_wb_wr, fx2_wb_full, fx2_wb_do,
                              fx2_wb_rd, fx2_wb_empty, fx2_wb_di, fx2_wb_di_vld,
                              FLAGA, wb_cmd_in_prog, loopback, status_regs,
                              C_REVISION  = C_REVISION,
                              C_WB_DAT_SZ = C_WB_DAT_SZ,
                              C_WB_ADR_SZ = C_WB_ADR_SZ,
                              C_BASE_ADDR = C_BASE_ADDR)

    
    # Nk external FIFO, streaming data FIFO
    #ex_fifo  = fifo_two_port_sync(fifo_rst, ifclk,
    #                              # A channel FX2 write -- internal read
    #                              fx2_fifo_wr, i_fifo_rd,
    #                              fx2_fifo_full, i_fifo_empty,
    #                              fx2_fifo_do, i_fifo_do, i_fifo_do_vld,
    #                              # B channel internal write -- FX2 read
    #                              i_fifo_wr, fx2_fifo_rd,
    #                              i_fifo_full, fx2_fifo_empty, 
    #                              i_fifo_di, fx2_fifo_di, fx2_fifo_di_vld,
    #                              hwma=hwma, hwmb=fifo_hwm,
    #                              # @todo flush?
    #                              DSZ=8, ASZ=10, C_HWMA=0, C_HWMB=512)


    @always_comb
    def rtl_fifo_rst():
        fifo_rst.next = ireset or fifo_clr
        

    # Data path error counters, because external modules interface with the
    # FIFO and many more corner cases error counters included for debug
    # and run-time info.  The wishbone interface is much more controlled
    # and consistent with the FIFO interface.
    @always(ifclk.posedge)
    def rtl2():
        if reset:
            err_wr_fxfifo.next = 0
            err_rd_fxfifo.next = 0
            err_wr_ififo.next  = 0
            err_rd_ififo.next  = 0
        else:
            if fx2_fifo_wr and fx2_fifo_full:
                err_wr_fxfifo.next = err_wr_fxfifo +1

            if fx2_fifo_rd and fx2_fifo_empty:
                err_rd_fxfifo.next = err_rd_fxfifo + 1

            if i_fifo_wr and i_fifo_full:
                err_wr_ififo.next = err_wr_ififo + 1

            if i_fifo_rd and i_fifo_empty:
                err_rd_ififo.next = err_rd_ififo + 1

            # @todo add FX2 external FIFO counters, FLAGB and FLAGD


    @always(ifclk.posedge)
    def rtl_data_counters():
        if reset:
            wb_in_cnt.next  = 0    # Data in to FPGA
            wb_out_cnt.next = 0    # Data out of FPGA
            d_in_cnt.next   = 0    # Data in to FPGA (opposite of USB perspective)
            d_out_cnt.next  = 0    # Data out of FPGA
        else:
            if fx2_fifo_rd:
                d_out_cnt.next = d_out_cnt + 1

            if fx2_fifo_wr:
                d_in_cnt.next = d_in_cnt + 1

            
            if fx2_wb_rd:
                wb_out_cnt.next = wb_out_cnt + 1

            if fx2_wb_wr:
                wb_in_cnt.next = wb_in_cnt + 1

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Error and Status Counters
    # Offset (C_BASE_ADDR + 0x10)
    #   0-3    :   FX2 -> Internal FIFO error
    #   4-7    :   Internal FIFO -> FX2 error
    #   8-11   :   External Logic -> Internal FIFO error
    #   12-15  :   Internal FIFO -> External Logic error
    #   16-23  :   Wishbone bytes in
    #   24-31  :   Wishbone bytes out
    #   32-39  :   Data stream bytes in
    #   40:47  :   Data stream bytes out
    @always_comb
    def rtl_fake_ram():
        fake_mem[0].next = err_wr_fxfifo[32:24]; fake_mem[1].next = err_wr_fxfifo[24:16];
        fake_mem[2].next = err_wr_fxfifo[16:8];  fake_mem[3].next = err_wr_fxfifo[8:0];

        fake_mem[4].next = err_rd_fxfifo[32:24]; fake_mem[5].next = err_rd_fxfifo[24:16];
        fake_mem[6].next = err_rd_fxfifo[16:8];  fake_mem[7].next = err_rd_fxfifo[8:0];

        fake_mem[8].next = err_wr_ififo[32:24]; fake_mem[9].next = err_wr_ififo[24:16];
        fake_mem[10].next = err_wr_ififo[16:8]; fake_mem[11].next = err_wr_ififo[8:0];

        fake_mem[12].next = err_rd_ififo[32:24]; fake_mem[13].next = err_rd_ififo[24:16];
        fake_mem[14].next = err_rd_ififo[16:8];  fake_mem[15].next = err_rd_ififo[8:0];

        # @todo byte counters
                
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Built in loop back
    @always_comb
    def rtl3():
        if loopback:
            i_fifo_di.next      = lp_fifo_di
            i_fifo_wr.next      = lp_fifo_wr
            i_fifo_rd.next      = lp_fifo_rd
            lp_fifo_do.next     = i_fifo_do
            lp_fifo_do_vld.next = i_fifo_do_vld
            lp_fifo_full.next   = i_fifo_full
            lp_fifo_empty.next  = i_fifo_empty
            
            fifo_do.next     = 0
            fifo_do_vld.next = False
            fifo_full.next   = False
            fifo_empty.next  = False
            
        else:
            i_fifo_di.next   = fifo_di
            i_fifo_wr.next   = fifo_wr
            i_fifo_rd.next   = fifo_rd
            fifo_do.next     = i_fifo_do
            fifo_do_vld.next = i_fifo_do_vld
            fifo_full.next   = i_fifo_full
            fifo_empty.next  = i_fifo_empty

            lp_fifo_do.next     = 0
            lp_fifo_do_vld.next = False
            lp_fifo_full.next   = False
            lp_fifo_empty.next  = True


    @always_comb
    def rtl4():
        lp_fifo_di.next  = lp_fifo_do
        lp_fifo_rd.next  = _lp_fifo_rd and not lp_fifo_full and not lp_fifo_empty 
        lp_fifo_wr.next  = _lp_fifo_wr and not lp_fifo_full and not lp_fifo_empty and lp_fifo_do_vld


    @always(sys_clk.posedge)
    def rtl5():
        if ireset:
            _lp_fifo_wr.next = False
            _lp_fifo_rd.next = False
        else:
            if not lp_fifo_empty and not lp_fifo_full:
                _lp_fifo_rd.next = True
                _lp_fifo_wr.next = True
            else:
                _lp_fifo_rd.next = False
                _lp_fifo_wr.next = False

                
    return instances()


