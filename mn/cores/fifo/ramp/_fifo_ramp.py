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
from _regfile_def import regfile

def m_fifo_ramp(
    # --[ports]--
    clock,
    reset,
    regbus,
    fifobus,
    
    # --[parameters]--
    base_address = 0x00
):
    """ FIFO Ramp module
    This module provides a simple 8-bit counter that will generate
    a ramp.  This ramp is fed to the USB fifo.  This can be used
    to validate the usb connection and the device to host (IN) data
    rates.
    """

    g_regbus = regfile.m_per_interface(clock,reset,regbus,
                                       base_address=base_address)
    
    
    enable = Signal(False)
    ramp  =  Signal(intbv(0)[fifobus.width:])
    wcnt    = Signal(intbv(0x3FF)[32:])
    div     = Signal(intbv(0)[32:])
    rcnt    = Signal(intbv(0)[32:])

    # ?? not sure if this makes sense ??
    ramp_mod = int(2**fifobus.width)

    @always_comb
    def rtl_assign():
        regfile.cnt3.next = (rcnt >> 24) & 0xFF
        regfile.cnt2.next = (rcnt >> 16) & 0xFF
        regfile.cnt1.next = (rcnt >> 8) & 0xFF
        regfile.cnt0.next = (rcnt >> 0) & 0xFF
        
    @always_seq(clock.posedge, reset=reset)
    def rtl_reg():
        enable.next = regfile.enable
        div.next = ((regfile.div3 << 24) | 
                    (regfile.div2 << 16) |
                    (regfile.div1 << 8) |
                    (regfile.div0))
        
    @always_seq(clock.posedge, reset=reset)
    def rtl_ramp():
        if regfile.enable and not fifobus.full:
            if wcnt == 0 :
                fifobus.wr.next = True
                fifobus.di.next = ramp
                if ramp+1 == ramp_mod:
                    rcnt.next = rcnt + 1
                ramp.next = (ramp + 1) % ramp_mod
                wcnt.next = div
            else:
                fifobus.wr.next = False
                wcnt.next = wcnt - 1
        else:
            fifobus.wr.next = False
            fifobus.di.next = 0
            wcnt.next = div
    
    return instances()
