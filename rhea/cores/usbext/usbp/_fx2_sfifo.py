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
 This module contains the logic to interface with the FX2 Slave
 FIFO Interface.
 
 The FX2 Endpoints are a conduit between the USB bus and the FPGA.
 
 The data is sent directly to the FPGA with no interaction from
 the USB controllers embedded processor.
 
 The port listing will match the defined FIFO interface exactly
 and the signals will be assigned to signal names that match
 the actual functionality.  Also the FX2 has an 8bit (or 16bit)
 bi-dir interface.  The actual inout tristate logic has to be
 inferred at the top level of the design. 
 
 FYI - The FX2 Registers associate with programming the FIFOs to 
       slave FIFO.  Endpoints 2-6, 4-8 will expected to be programmed
       as slave FIFO to the FPGA.
     
     # IFCONFIG         - Bits 1:0 Must be set to 2'b11
     # PINFLAGAB        -
     # PINFLAGCD        -
     # FIFORESET        -
     # FIFOPINPOLAR     -
     # EPxCFG           -
     # EPxFIFOCFG       -
     # EPxAUTOINLENH:L  -
     # EPxFIFOPFH:L     -
     # PORTACFG         -
     # INPKTEND         -
     # EPxFLAGIE        -
     # EPxFLAGIRQ       -
     # EPxFIFOBCH:L     -
     # EPxFLAGS         -
     # EPxBUF           - 
     
     Syncronous Mode, Data clocks in on the rising edge of IFCLK.
     8-bit mode (low pin count controllers), WORDWIDE=0 8bit mode.
     
     The FIFO Flags will be setup to use the Empty flags for the OUT FIFOS
     and Full for the IN FIFOS.
     FIFOADR[1:0]
       00 - EP2 OUT
       01 - EP4 OUT
       10 - EP6 IN 
       11 - EP8 IN
"""

from myhdl import *
from _fx2_arb import fx2_arb
from _fx2_iobuf import fx2_iobuf

def fx2_sfifo(
    reset,           # syncronous system reset
    # ----[ FX2 FIFO Interface ]----
    IFCLK,           # USB controller sync clock @ 48MHz
    FLAGA,           # EP2 (Out) Empty
    FLAGB,           # EP4 (Out) Empty    
    FLAGC,           # EP4 (In)  Full
    FLAGD,           # EP8 (In)  Full

    SLOE,            # Output Enable, Slave FIFO
    SLRD,            # Read Strobe
    SLWR,            # Write Strobe

    FIFOADR,         # FIFO select signals
    PKTEND,          # Packet end, inform FX2 to send data without FIFO full
    FDI,             # Fifo data in
    FDO,             # Fifo data out

    # ----[ Internal Bus ]----
    bus_di,          # input, data to FX2 from wb bus
    bus_di_vld,      # input, data valid strobe
    bus_do,          # To Bus_FIFO Port A
    bus_full,        #
    bus_empty,       #
    bus_wr,          #
    bus_rd,          #

    # ----[ Internal data stream FIFO ] ----
    fifo_di,         # input, data to FX2
    fifo_di_vld,     # input, data valid strobe
    fifo_do,         #
    fifo_full,       #
    fifo_empty,      #
    fifo_wr,         #
    fifo_rd,         #
    fifo_hold,       #
    fifo_hwm,        # 

    # @todo rename to be more generic, example hold_off
    cmd_in_prog,     # Wishbone command in progress
    dbg
    ):
    """FX2 Slave FIFO interface
    """  

    
    ep2_read   = Signal(False)
    ep6_write  = Signal(False)
    ep4_read   = Signal(False)
    ep8_write  = Signal(False)
    
    ep2_empty  = Signal(False)
    ep6_full   = Signal(False)
    ep4_empty  = Signal(False)
    ep8_full   = Signal(False)

    ep2_din    = Signal(intbv(0)[8:])
    ep2_din_vld = Signal(False)
    ep4_din    = Signal(intbv(0)[8:])
    ep4_din_vld = Signal(False)    
    ep6_dout   = Signal(intbv(0)[8:])
    ep6_dout_vld = Signal(False)
    ep8_dout   = Signal(intbv(0)[8:])
    ep8_dout_vld = Signal(False)    

    _slwr      = Signal(False)
    _slrd      = Signal(False)
    _sloe      = Signal(False)
    _pktend    = Signal(False)
    _fifoadr   = Signal(intbv(0)[2:])

        
    @always_comb
    def rtl_assignments():
        bus_do.next  = ep2_din
        bus_wr.next  = ep2_din_vld
        bus_rd.next  = ep6_write        
        
        fifo_do.next = ep4_din
        fifo_wr.next = ep4_din_vld
        fifo_rd.next = ep8_write
        
        dbg.next     = 0

        ep6_dout.next     = bus_di
        ep6_dout_vld.next = bus_di_vld

        ep8_dout.next     = fifo_di
        ep8_dout_vld.next = fifo_di_vld

        
    # IOBUFs for the FX2 interface.  All FX2 signals are regiester in
    # this module
    iobuf = fx2_iobuf(reset, IFCLK, FLAGA, FLAGB, FLAGC, FLAGD,
                      SLOE, SLRD, SLWR, FIFOADR, PKTEND, FDI, FDO,
                      ep2_empty, ep2_din, ep2_din_vld,
                      ep4_empty, ep4_din, ep4_din_vld,
                      ep6_full, ep6_dout, ep6_dout_vld,
                      ep8_full, ep8_dout, ep8_dout_vld,
                      _fifoadr, _slrd, _sloe, _pktend)

    
    # arbitration module, determine with FX2 FIFO to move data to or from
    # The arb module drives some of the wr/rd signals since it determines
    # which endpoints are being read/written
    arb = fx2_arb(reset, IFCLK,
                  ep2_empty, ep6_full, ep4_empty, ep8_full,
                  _sloe, _slrd, _slwr, _pktend, _fifoadr,
                  bus_full, bus_empty, bus_di_vld,
                  fifo_full, fifo_empty, fifo_di_vld, fifo_hwm,
                  # the individual read/write strobes not used
                  # any more
                  ep2_read, ep6_write, ep4_read, ep8_write,
                  fifo_hold, cmd_in_prog)



    return instances()

