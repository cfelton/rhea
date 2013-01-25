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
This provides the IO interface to the external FX2 USB controller.
All signals need to be in an IOB register to simplify timing.

"""

from myhdl import *

def fx2_iobuf(
    reset,
    
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
    
    # ----[ ]----
    ep2_empty,      # 
    ep2_din,        # ep2 data in bus
    ep2_din_vld,    # The data coming in is valid
    
    ep4_empty,      # 
    ep4_din,        # ep4 data in bus, stream EP
    ep4_din_vld,    # ep4 data valid
    
    ep6_full,       #
    ep6_dout,       # ep6 data out, bus commands
    ep6_dout_vld,   #
    
    ep8_full,       # 
    ep8_dout,       # ep8 data out, stream EP
    ep8_dout_vld,   #
    
    fifoaddr,       # Which fifo to read or write
    rd,             # read the selected fifo
    oe,             # output enable
    pktend          # commit a non-512 byte buffer
        
    ):
    """
    This interface has some assumptions that need to be known:
      1.  When writing data it is assumed that no more than 512 bytes
          will be streamed.  When the FX2 FIFO goes FULL it does so on
          the last byte being written.  Because the interface is highly
          registered (pipelined) if the FIFO goes full data will be stuck
          in between the internal FIFO and external FIFO.  The logic controlling
          the write (*_vld).  The *full* signal is register coming
          in so the last pipeline stage won't know to halt.

          <optional> the full signals can *gate* the clock for the last pipeline
                     preventing the data lost and keeping the fanout small of the
                     incoming signals.

      2.  The read data should be read in 512 blocks as well.  Data won't be lost
          on the incoming data because the empty signal will clear the read and the
          data valid.  Even though the incoming control signal will be active the
          data will not be valid

      Read
        To read from EP2 or EP4, check that the FIFO is not empty (empty delay 2 clocks),
        read till empty or 512 bytes.  Wait 2 clocks see and check empty again.  Reading
        till empty ok even though empty is delayed becase the incoming data has a valid
        signal that will qualify the data.  If the external FIFO goes empty before
        the data is read the valid will not be active.
        
      Write
        To write to EP6 or EP8, check that the fifo is not FULL.  Start writing data max
        of 512 bytes.  If less than 512 bytes is written pulse pktend (1 clock).  Wait
        2 clock cycles and check not full.  No explicit write signal is used (into this module).
        The data valid signals will be used to drive the write.
    """
        

    _ep2_empty = Signal(False)
    _ep2_vld   = Signal(False)

    _ep4_empty = Signal(False)
    _ep4_vld   = Signal(False)

    _ep6_full  = Signal(False)
    _ep8_full  = Signal(False)

    _fdi       = Signal(intbv(0)[8:])
    _fdo       = Signal(intbv(0)[8:])
    _slrd      = Signal(False)
    #_slwr      = Signal(False)

    _empty     = Signal(False)
    
    
    _ovld = Signal(False)

    
    @always(IFCLK.posedge)
    def rtl_fx2_io_regs():
        _ep2_empty.next = FLAGA
        _ep4_empty.next = FLAGB
        _ep6_full.next  = FLAGC
        _ep8_full.next  = FLAGD
        
        _fdi.next = FDI
        FDO.next  = _fdo

        SLWR.next = _ovld
        SLOE.next = oe
        PKTEND.next = pktend
        FIFOADR.next = fifoaddr

        _slrd.next = rd
        #_slwr.next = _ovld


    @always_comb
    def rtl_empty():
        if fifoaddr == 0:
            _empty.next = FLAGA
        elif fifoaddr == 1:
            _empty.next = FLAGB
        else:
            _empty.next = True


    # Unlike write, where the state machine (arb) can
    # count the number of bytes going out, we don't know
    # how many bytes are coming in.  To keep all FX2 signals
    # in IOB registers the empty signal is delayed to the state-machine.
    # To prevent from reading when empty the SLRD will be reset when
    # empty and will not activate again till the ARB (state-machine) as
    # de-activated the read control signal.
    rd_st = Signal(False)
    @always(IFCLK.posedge, _empty.posedge)
    def rtl_slrd():
        if _empty:
            SLRD.next  = False
            rd_st.next = False
        else:
            if not rd:
                rd_st.next = True

            if rd_st:
                SLRD.next = rd


    @always(IFCLK.posedge)
    def rtl_in_vld():
        _ep2_vld.next = _slrd #and not _ep2_empty
        _ep4_vld.next = _slrd #and not _ep4_empty

        
    @always(IFCLK.posedge)
    def rtl_out_to_fpga():
        # A mux here isn't really required, could easily fanout to the
        # two output registers.  But it is useful for debugging.
        if fifoaddr == 0:
            ep2_din.next = _fdi
        elif fifoaddr == 1:
            ep4_din.next = _fdi
        else:
            ep2_din.next = 0
            ep4_din.next = 0

        ep2_din_vld.next = _ep2_vld and not _ep2_empty and (fifoaddr == 0)
        ep2_empty.next = _ep2_empty
        
        ep4_din_vld.next = _ep4_vld and not _ep2_empty and (fifoaddr == 1)
        ep4_empty.next = _ep4_empty


    # First register delay
    @always(IFCLK.posedge)
    def rtl_in_from_fpga():
        if fifoaddr == 2:
            _fdo.next  = ep6_dout
            _ovld.next = ep6_dout_vld
        elif fifoaddr == 3:
            _fdo.next  = ep8_dout
            _ovld.next = ep8_dout_vld
        else:
            _fdo.next  = 0
            _ovld.next = False

        ep6_full.next = _ep6_full
        ep8_full.next = _ep8_full


    # Add some checking :
    #  -- assert SLRD or SLWR only acitve max 512 continuous IFCLK
    #  -- at least 2 clock cycles between
    #        1. low read to high read
    #        2. low ep6_dout_vld to high ep6_dout_vld
    #        3. low ep8_dout_vld to high ep8_dout_vld
    
        
    return instances()
