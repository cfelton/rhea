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
 
def fifo_fast(
    clk,        # sync clock
    reset,      # reset fifo
    clr,        # clear fifo
    we,         # write enable
    re,         # read enable
    full,       # FIFO full
    empty,      # FIFO empty
    di,         # data input
    do,         # data out
    cnt,        # Numer of elements in FIFO
    
    C_DSZ = 8,  # Data word size
    C_ASZ = 3   # Size of the FIFO
    ):
    """ Small fast fifo
    """

    mem   = [Signal(intbv(0)[C_DSZ:]) for i in range(2**C_ASZ)]
    wp    = Signal(intbv(0, min=0, max=2**C_ASZ))
    wp_p1 = Signal(intbv(0, min=0, max=2**C_ASZ))
    rp    = Signal(intbv(0, min=0, max=2**C_ASZ))
    rp_p1 = Signal(intbv(0, min=0, max=2**C_ASZ))
    gb    = Signal(False)

    # There appears to be an issue with CVER and the Verilog power operator
    # **.  Precompute the mod values
    MOD_ADDR = int(2**C_ASZ)
    MAX_CNT  = MOD_ADDR
    
    @always(clk.posedge)
    def rtl_wp_reg():
        if reset:
            wp.next = 0
        else:
            if clr:
                wp.next = 0
            elif we and not gb:
                wp.next = wp_p1

    @always_comb
    def rtl_wp():
        wp_p1.next = (wp + 1) % MOD_ADDR        

    @always(clk.posedge)
    def rtl_rp_reg():
        if reset:
            rp.next = 0
        else:
            if clr:
                rp.next = 0
            elif re:
                rp.next = rp_p1

    @always_comb
    def rtl_rp():
        rp_p1.next = (rp + 1) % MOD_ADDR

    @always_comb
    def rtl_mem_output():
        do.next = mem[int(rp)]

    @always(clk.posedge)
    def rtl_mem():
        if we:
            mem[int(wp)].next = di

    @always_comb
    def rtl_assignments():

        if wp == rp and not gb:
            empty.next = True
        else:
            empty.next = False

        if wp == rp and gb:
            full.next = True
        else:
            full.next = False

    @always(clk.posedge)
    def rtl_guard_bit():
        if reset:
            gb.next = False
        else:
            if clr:
                gb.next = False
            elif wp_p1 == rp and we:
                gb.next = True
            elif re:
                gb.next = False

    @always_comb
    def rtl_fifo_cnt():
        if not gb:
            cnt.next = (wp - rp) % MAX_CNT
        else:
            cnt.next = MAX_CNT


    return instances()

                
    
    
