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

from myhdl import *

S_BYTE0  = 0
S_BYTE1  = 1
S_CMD    = 2
S_ADDRH  = 3
S_ADDRL  = 4
S_LEN    = 5
S_BYTE6  = 6
S_BYTE7  = 7
S_WB_BUS = 8

S_GET_BYTE0  = 0
S_GET_BYTE1  = 1
S_GET_CMD    = 2
S_GET_ADDRH  = 3
S_GET_ADDRL  = 4
S_GET_LEN    = 5
S_GET_BYTE6  = 6
S_GET_BYTE7  = 7
S_DO_WB_BUS  = 8
S_DO_WB_ACK  = 9
S_DO_WB_END  = 10


CMD_WRITE = 1
CMD_READ  = 2

def wb_master_cmd(
    clk,
    reset,
    fifo_do,
    fifo_do_vld,
    fifo_empty,
    wb_go,
    wb_rd,
    wb_wr,
    wb_addr,
    wb_dat_o,
    wb_ack,
    wb_cmd_in_prog,
    to_ack
    ):
    """Wishbone command packet decoder

    """

    wb_len   = Signal(intbv(0)[8:])
    wb_cnt   = Signal(intbv(0)[8:])
    wb_cmd   = Signal(intbv(0)[8:])

    wb_iaddr = Signal(intbv(0)[16:])
    wb_idat  = Signal(intbv(0)[8:])


    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Misc Registers
    addr_lo = Signal(intbv(0)[8:])
    addr_hi = Signal(intbv(0)[8:])

    to_cnt  = Signal(intbv(0)[8:])
    
    # @todo Re-Write this state-machine!!!  Currently too cryptic, simply read
    #       read command, bus cycle, etc.  First implemenation tried to leverage
    #       index counter and state, keep them separate.
    # Update:
    #       The state-machine has been update but still can use some work.
    state = Signal(intbv(0)[4:])
    @always(clk.posedge)
    def rtl_state_machine():
        if reset:
            state.next    = S_GET_BYTE0
            wb_len.next   = 1
            wb_cnt.next   = 0
            wb_idat.next  = 0xCC
            addr_lo.next  = 0xFF
            addr_hi.next  = 0xFF
            wb_iaddr.next = 0xAAAA
            to_cnt.next   = 0
            to_ack.next   = False
        else:
            if state == S_GET_BYTE0:
                if fifo_do_vld:
                    state.next = S_GET_BYTE1
                    
            elif state == S_GET_BYTE1:
                if fifo_do_vld:
                    state.next = S_GET_CMD

            elif state == S_GET_CMD:
                if fifo_do_vld:
                    wb_cmd.next = fifo_do
                    state.next = S_GET_ADDRH

            elif state == S_GET_ADDRH:
                if fifo_do_vld:
                    addr_hi.next = fifo_do
                    state.next = S_GET_ADDRL

            elif state == S_GET_ADDRL:
                if fifo_do_vld:
                    addr_lo.next = fifo_do
                    state.next = S_GET_LEN

            elif state == S_GET_LEN:
                if fifo_do_vld:
                    # ?? don't need another register for wb_iaddr ??
                    wb_iaddr.next = concat(addr_hi, addr_lo)
                    if fifo_do == 0:
                        wb_len.next = 1
                    else:
                        wb_len.next = fifo_do

                    state.next = S_GET_BYTE6

            elif state == S_GET_BYTE6:
                if fifo_do_vld:
                    state.next = S_GET_BYTE7

            elif state == S_GET_BYTE7:
                if fifo_do_vld:
                    state.next = S_DO_WB_BUS

            elif state == S_DO_WB_BUS:
                if wb_cnt < wb_len-1:
                    wb_idat.next = fifo_do
                    wb_cnt.next  = wb_cnt + 1
                    # @todo validate length vs. number of bytes!
                else:
                    state.next = S_DO_WB_ACK
                    to_cnt.next = 0
                    
            elif state == S_DO_WB_ACK:
                if wb_ack:
                    state.next = S_DO_WB_END
                else:
                    if to_cnt > 16:
                        to_ack.next = True
                        state.next = S_DO_WB_END
                        to_cnt.next = 0
                    else:
                        to_cnt.next = to_cnt + 1

            elif state == S_DO_WB_END:
                to_ack.next = False
                if not wb_ack:
                    state.next = S_GET_BYTE0
                                            
        
    @always_comb
    def rtl_addr():
        wb_addr.next  = wb_iaddr + wb_cnt

    @always_comb
    def rtl_data():
        # will fifo_do be hi fan out?? need to register?? then
        # write logic needs to change
        wb_dat_o.next = fifo_do #wb_idat


    @always_comb
    def rtl_go():
        if state >= S_GET_BYTE7:
            wb_go.next = True
        else:
            wb_go.next = False

    @always_comb
    def rtl_control():
        
        if wb_cmd == CMD_WRITE and state == S_DO_WB_BUS:
            wb_wr.next = True
        else:
            wb_wr.next = False
        
        if wb_cmd == CMD_READ and state == S_DO_WB_BUS:
            wb_rd.next = True
        else:
            wb_rd.next = False

        if state > S_GET_BYTE0:
            wb_cmd_in_prog.next = True
        else:
            wb_cmd_in_prog.next = False

    return instances()
