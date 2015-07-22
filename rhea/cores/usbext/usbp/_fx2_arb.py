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

import sys,os
from myhdl import *

EP2_ADDR = 0
EP4_ADDR = 1
EP6_ADDR = 2
EP8_ADDR = 3

# Why do enums need to be global?
tState = enum(
    'IDLE',
    'EP2_START',
    'EP2_READ',
    'EP2_END',
    'EP4_START',
    'EP4_READ',
    'EP4_END',
    'EP6_START',
    'EP6_WRITE',
    'EP6_END',
    'EP8_START',
    'EP8_WRITE',
    'EP8_END',
    'EP8_END_NF',
    # 2 clock delay at the end of each IO
    'IO_END1',
    'IO_END2' )


def fx2_arb(
    reset,
    # FX2 signals
    ifclk,
    ep2_empty,
    ep6_full,
    ep4_empty,
    ep8_full,
    sloe,             #
    slrd,             #
    slwr,             #
    pktend,           #
    fifoaddr,         #
    
    # Interfnal FIFOs
    bus_full,         #
    bus_empty,        #
    bus_vld,          #

    data_full,        # data fifo full
    data_empty,       # data fifo empty
    data_vld,         # data fifo out valid
    data_hwm,         # at least 512 bytes
    
    # Internal Control Signals
    ep2_read,         #
    ep6_write,        #
    #ep6_hold
    ep4_read,         #
    ep8_write,        #
    ep8_hold,         #
    
    cmd_in_prog,      #
    ):
    """FX2 arbitration.    
    """

    C_FX2_FIFO_SZ = 512
    
    state   = Signal(tState.IDLE)  
    _slwr6  = Signal(False)
    _slwr8  = Signal(False)
    _slwr2  = Signal(False)
    _slwr4  = Signal(False)
    _slrd6  = Signal(False)
    _slrd8  = Signal(False)
    _slrd2  = Signal(False)
    _slrd4  = Signal(False)
    _sloe   = Signal(False)
    _pktend = Signal(False)

    _cnt    = Signal(intbv(0, max=C_FX2_FIFO_SZ, min=0))
    
    @always_comb
    def rtl_assignments():
        sloe.next = _sloe
        slrd.next = (_slrd2 & ~ep2_empty & ~bus_full) | (_slrd4 & ~ep4_empty & ~data_full)
        slwr.next = (_slwr6 & ~ep6_full & ~bus_empty) | \
                    (_slwr8 & ~ep8_full & ~data_empty)

        pktend.next    = _pktend

        ep2_read.next  = _slrd2  #(state == tState.EP2_READ)
        ep6_write.next = _slwr6  #(state == tState.EP6_WRITE)
        ep4_read.next  = _slrd4  #(state == tState.EP4_READ)
        ep8_write.next = _slwr8  #(state == tState.EP8_WRITE)


    @always(ifclk.posedge)
    def rtl1():
        if reset:
            state.next = tState.IDLE
            _cnt.next  = 0
            _sloe.next = True
        else:
            if state == tState.IDLE:
                # @todo Add method to prevent starvation
                if not ep2_empty and not bus_full:
                    state.next = tState.EP2_START
                    _sloe.next = True
                elif not bus_empty and not ep6_full and not cmd_in_prog:
                    state.next = tState.EP6_START
                    _sloe.next = False

                elif not ep4_empty and not data_full:
                    state.next = tState.EP4_START
                    _sloe.next = True
                elif data_hwm and not ep8_hold and not ep8_full:                    
                    state.next = tState.EP8_START
                    _cnt.next = 0
                    _sloe.next = False

            elif state == tState.EP2_START:
                state.next = tState.EP2_READ
            elif state == tState.EP2_READ:
                if ep2_empty or bus_full:
                    state.next = tState.EP2_END   # cf 6/5/10 stream read
            elif state == tState.EP2_END:
                state.next = tState.IO_END1
                
            elif state == tState.EP4_START:
                state.next = tState.EP4_READ
            elif state == tState.EP4_READ:
                if (ep4_empty or data_full): 
                    state.next = tState.EP4_END
            elif state == tState.EP4_END:
                state.next = tState.IO_END1


            elif state == tState.EP6_START:
                state.next = tState.EP6_WRITE
            elif state == tState.EP6_WRITE:
                if (bus_empty or ep6_full): 
                    state.next = tState.EP6_END
            elif state == tState.EP6_END:
                state.next = tState.IO_END1

            elif state == tState.EP8_START:
                state.next = tState.EP8_WRITE
            elif state == tState.EP8_WRITE:
                if _cnt == C_FX2_FIFO_SZ-1:
                    state.next = tState.EP8_END
                elif data_empty and not ep8_full:
                    # @todo increment pktend count, usually error
                    state.next = tState.EP8_END_NF
                elif ep8_full:
                    state.next = tState.EP8_END
                elif _slwr8 and data_vld:
                    _cnt.next = _cnt + 1
                    
            elif state == tState.EP8_END:
                state.next = tState.IO_END1
                # @todo if _cnt != C_FX2_FIFO_SZ-1 increment counter
            elif state == tState.EP8_END_NF:
                # not full case, hit packet end
                state.next = tState.IO_END1

            elif state == tState.IO_END1:
                state.next = tState.IO_END2

            elif state == tState.IO_END2:
                state.next = tState.IDLE
                
            else:
                assert False, "fx2_arb: Error incorrect state %s" % (state)
                state.next = tState.IDLE

                
    @always_comb
    def rtl2():
        if state == tState.EP4_START or state == tState.EP4_READ or state ==  tState.EP4_END:
            fifoaddr.next = EP4_ADDR
        elif state == tState.EP8_START or state == tState.EP8_WRITE or state ==  tState.EP8_END or state == tState.EP8_END_NF:
            fifoaddr.next = EP8_ADDR
        elif state == tState.EP2_START or state == tState.EP2_READ or state ==  tState.EP2_END:
            fifoaddr.next = EP2_ADDR
        elif state == tState.EP6_START or state == tState.EP6_WRITE or state ==  tState.EP6_END:
            fifoaddr.next = EP6_ADDR
        else:
            fifoaddr.next = EP4_ADDR


    # NOTE: The address setup is min of 25ns, according to the datasheet.
    #       Need an additional clock cycle on the first read or write.
    #       For a block of data each subsequest byte (word) can be
    #       read/written on each clock cycle, 48/96 MB/sec.
    @always_comb
    def rtl3():
        if state ==  tState.EP2_READ:
            _slrd2.next = True
        else:
            _slrd2.next = False

        if state == tState.EP4_READ:
            _slrd4.next = True
        else:
            _slrd4.next = False

        #if state == tState.EP6_START or state == tState.EP6_WRITE or \
        #   state == tState.EP8_START or state == tState.EP8_WRITE:
        #    _sloe.next = False
        #elif state == :
        #    _sloe.next = True

        if state == tState.EP6_WRITE:
            _slwr6.next =  True
        else:
            _slwr6.next = False

        if state == tState.EP8_WRITE:
            _slwr8.next = True
        else:
            _slwr8.next = False

        if state == tState.EP6_END: # or state == tState.EP8_END_NF:
            _pktend.next = True
        else:
            _pktend.next = False

        # @todo add assertsion
        # assert not (full and wr_en and wr_cs)
        # assert not (empty and rd_en and rd_cs)
        
              
    return instances()
