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
SPI interface
-------------

This module is controlled / configured from the register bus.
data can either be transferred from the register bus or
it can be transferred from the streaming interface.

This module is register compatible with the Xilinx OPB SPI
controller.  The interrupt register has been removed and replaced
with a clock divide register.
"""

from myhdl import *

from ..fifo import m_fifo_fast
from ...system import FIFOBus

from _regfile_def import regfile

def m_spi(
    # ---[ Module Ports]---
    clock,
    reset,   
    regbus,  # memory-mapped register bus
    rxfb,    # streaming interface, receive fifo bus
    txfb,    # streaming inteface, transmit fifo bus
    spibus,  # external SPI bus

    tstpts = None,
    
    # ---[ Module Parameters ]---
    base_address = 0x0400,  # base address (memmap register bus)
    include_fifo = True     # inclde aan 8 byte deep FIFO
    ):
    """ SPI (Serial Peripheral Interface) module

      This is an implementation of an SPI controller that is wishbone
      enabled.  The control registers have common SPI names and are
      similar to the registers in the Xilinx OCB SPI controller.

    """
    # -- local signals --
    ena    = Signal(False)
    clkcnt = Signal(modbv(0, min=0, max=2**12))
    bcnt   = Signal(intbv(0, min=0, max=8))
    treg   = Signal(intbv(0)[8:])
    rreg   = Signal(intbv(0)[8:])
    
    x_sck   = Signal(False)
    x_ss    = Signal(False)
    x_mosi  = Signal(False)
    x_miso  = Signal(False)    

    xfb = FIFOBus(args=txfb.args)
    fb = FIFOBus(args=rxfb.args)
    
    States = enum('IDLE','WAIT_HCLK','DATA_IN','DATA_CHANGE',
                  'WRITE_FIFO','END')
    state  = Signal(States.IDLE)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # memory- mapped registers
    # get the register file for this core/peripheral
    g_regbus = regfile.m_per_interface(clock,reset,regbus,
                                       base_address=base_address)
        
    # FIFO for the wishbone data transfer
    if include_fifo:
        g_rx_fifo = m_fifo_fast(clock, reset, rxfb)
        
        g_tx_fifo = m_fifo_fast(clock, reset, txfb)

    @always_comb
    def rtl_assign():
        regfile.sptc.next = txfb.count
        regfile.sprc.next = rxfb.count

        if clkcnt > 0:
            ena.next = False
        else:
            ena.next = True


    @always(regbus.clock.posedge)
    def rtl_clk_div():
        if regfile.spcr.spe and clkcnt != 0 and state != States.IDLE:
            clkcnt.next = (clkcnt - 1)
        else:
            if   regfile.spxx == 0:   clkcnt.next = 0    # 2
            elif regfile.spxx == 1:   clkcnt.next = 1    # 4
            elif regfile.spxx == 2:   clkcnt.next = 3    # 8
            elif regfile.spxx == 3:   clkcnt.next = 7    # 16
            elif regfile.spxx == 4:   clkcnt.next = 15   # 32 
            elif regfile.spxx == 5:   clkcnt.next = 31   # 64
            elif regfile.spxx == 6:   clkcnt.next = 63   # 128
            elif regfile.spxx == 7:   clkcnt.next = 127  # 256
            elif regfile.spxx == 8:   clkcnt.next = 255  # 512
            elif regfile.spxx == 9:   clkcnt.next = 511  # 1024
            elif regfile.spxx == 10:  clkcnt.next = 1023 # 2048
            elif regfile.spxx == 11:  clkcnt.next = 2047 # 4096
            else: clkcnt.next = 4095
            
    
    @always_seq(regbus.clock.posedge, reset=regbus.reset)
    def rtl_state_and_more():
        """
        Designed to the following timing diagram

        SCK   CPOL=0 ______/---\___/---\___/---\___/---\___/---\___/---\___/---\___/---\___/---\ 
              CPOL=1 ------\___/---\___/---\___/---\___/---\___/---\___/---\___/---\___/---\___/ 
        SS           ---\_______________________________________________________________________ 
        CPHA=0 MOSI  ...|.0....|.1.....|.2.....|.3.....|.4.....|.5.....|.6.....|.7.....|.0.....| 
               MISO  ...|.0....|.1.....|.2.....|.3.....|.4.....|.5.....|.6.....|.7.....|.0.....| 
        CPHA=1 MOSI  ...|....0.....|.1.....|.2.....|.3.....|.4.....|.5.....|.6.....|.7.....|.0...
               MISO  ......|.0.....|.1.....|.2.....|.3.....|.4.....|.5.....|.6.....|.7.....|.0...
        """
        if not regfile.spcr.spe:
            state.next = States.IDLE
            bcnt.next  = 0
            treg.next  = 0
            
            xfb.rd.next  = False
            xfb.wr.next  = False

            x_sck.next = False
            x_ss.next  = False
        else:
            if not regfile.freeze:
                # ~~~~ Idle state ~~~~
                if state == States.IDLE:
                    bcnt.next = 7
                    treg.next = xfb.rdata
                    x_sck.next = regfile.spcr.cpol
                    xfb.wr.next = False
                    
                    if not xfb.empty and not xfb.full:
                        xfb.rd.next = True
                        x_ss.next = False
                        if regfile.spcr.cpha: # Clock in on second phase 
                            state.next = States.WAIT_HCLK
                        else: # Clock in on first phase
                            state.next = States.DATA_IN
                    else:
                        xfb.rd.next = False
                        x_ss.next  = True

                # ~~~~ Wait half clock period for cpha=1 ~~~~
                elif state == States.WAIT_HCLK:
                    if ena:
                        x_sck.next  = not x_sck
                        state.next = States.DATA_IN
                        xfb.rd.next = False
                        xfb.wr.next = False
                    else:
                        xfb.rd.next = False
                        xfb.wr.next = False

                # ~~~~ Clock Data In State ~~~~
                elif state == States.DATA_IN:
                    if ena: # clk div
                        x_sck.next  = not x_sck
                        rreg.next  = concat(rreg[7:0], x_miso)
                        
                        if regfile.spcr.cpha and bcnt == 0:
                            xfb.wr.next = True
                            if xfb.empty or xfb.full:
                                state.next = States.END
                            else:
                                state.next = States.DATA_CHANGE
                                #bcnt.next  = 7
                                #x_fifo_rd.next = True
                                #treg.next = x_fifo_do
                        else:                            
                            state.next = States.DATA_CHANGE
                    else:
                        xfb.rd.next = False
                        xfb.wr.next = False
                        
                # ~~~~ Change Data State ~~~~
                elif state == States.DATA_CHANGE:
                    if ena:
                        x_sck.next  = not x_sck
                        if bcnt == 0:  
                            if not regfile.spcr.cpha:
                                xfb.wr.next = True
                                
                            if xfb.empty or xfb.full:
                                state.next = States.END
                            else: # more data to transfer
                                bcnt.next = 7
                                state.next = States.DATA_IN
                                xfb.rd.next = True
                                treg.next = xfb.rdata
                                    
                        else:
                            treg.next = concat(treg[7:0], intbv(0)[1:])
                            bcnt.next = bcnt - 1                        
                            state.next = States.DATA_IN
                    else:
                        xfb.rd.next = False
                        xfb.wr.next = False

                # ~~~~ End State ~~~~
                elif state == States.END:
                    if ena: # Wait half clock cycle go idle
                        state.next = States.IDLE
                    else:
                        xfb.rd.next = False
                        xfb.wr.next = False

                
                # Shouldn't happen, error in logic
                else:
                    state.next = States.IDLE
                    assert False, "SPI Invalid State"

    @always_comb
    def rtl_fifo_sigs():
        txfb.wdata.next = regfile.sptx
        regfile.sprx.next = rxfb.rdata

        
    @always_comb
    def rtl_fifo_sel():
        if regfile.spcr.rdata:
            xfb.empty.next = txfb.empty
            xfb.full.next  = rxfb.full
            xfb.rdata.next = txfb.rdata
            
            txfb.rd.next = xfb.rd
            rxfb.wr.next = xfb.wr            
            rxfb.wdata.next = rreg
            txfb.wr.next = regfile.sptx.wr
            rxfb.rd.next = regfile.sprx.rd      
            
            fb.rd.next    = False
            fb.wr.next    = False
            fb.wdata.next    = 0  # or'd bus must be 0
        else:
            xfb.empty.next = fb.empty
            xfb.full.next  = fb.full
            xfb.rdata.next = fb.rdata
            
            txfb.rd.next = False
            rxfb.wr.next = False
            rxfb.wdata.next = 0  # or'd bus must be 0
            txfb.wr.next = False
            rxfb.rd.next = False

            fb.rd.next    = xfb.rd
            fb.wr.next    = xfb.wr
            fb.wdata.next    = treg


    @always_comb
    def rtl_x_mosi():
        # @todo lsbf control signal
        x_mosi.next  = treg[7]


    #@always_comb
    @always(regbus.clock.posedge)
    def rtl_spi_sigs():
        spibus.sck.next   = x_sck

        if regfile.spcr.loop:
            spibus.mosi.next  = False
            x_miso.next = x_mosi
        else:
            spibus.mosi.next  = x_mosi
            x_miso.next = spibus.mosi

        if regfile.spcr.msse:
            spibus.ss.next = ~regfile.spss
        else:
            if x_ss:
                spibus.ss.next = 0xFF
            else:
                spibus.ss.next = ~regfile.spss


    #if tst_pts is not None:
    #    if isinstance(tst_pts.val, intbv) and len(tst_pts) == 8:
    #        @always_comb    
    #        def rtl_tst_pts():
    #            tst_pts.next[0] = SS[0]
    #            tst_pts.next[1] = SCK
    #            tst_pts.next[2] = MOSI
    #            tst_pts.next[3] = MISO
    #            
    #            tst_pts.next[4] = cr_wb_sel    # wishbone feeds Tx/Rx fifos
    #            tst_pts.next[5] = cr_spe       # SPI enable
    #            tst_pts.next[6] = x_fifo_empty # 
    #            tst_pts.next[7] = tx_fifo_wr   # 
    #    else:
    #        print "WARNING: SPI tst_pts is not None but is not an intbv(0)[8:]"

                
    return instances()
