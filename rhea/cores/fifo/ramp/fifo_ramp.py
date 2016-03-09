#
# Copyright (c) 2006-2013 Christopher L. Felton
#


from __future__ import absolute_import

from myhdl import *
from rhea.system import Global
from ._regfile_def import regfile


def fifo_ramp(
    # --[ports]--
    # @todo: use glbl for clock and reset
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
    glbl = Global(clock=clock, reset=reset)
    regfile.base_address = base_address
    g_regbus = regbus.add(regfile, 'fifo_ramp')
    
    enable = Signal(False)
    ramp = Signal(intbv(0)[fifobus.width:])
    wcnt = Signal(intbv(0x3FF)[32:])
    div = Signal(intbv(0)[32:])
    rcnt = Signal(intbv(0)[32:])

    # ?? not sure if this makes sense ??
    ramp_mod = int(2**fifobus.width)

    @always_comb
    def rtl_assign():
        regfile.cnt3.next = (rcnt >> 24) & 0xFF
        regfile.cnt2.next = (rcnt >> 16) & 0xFF
        regfile.cnt1.next = (rcnt >> 8) & 0xFF
        regfile.cnt0.next = rcnt & 0xFF
        
    @always_seq(clock.posedge, reset=reset)
    def rtl_reg():
        enable.next = regfile.enable
        div.next = ((regfile.div3 << 24) | 
                    (regfile.div2 << 16) |
                    (regfile.div1 << 8) |
                     regfile.div0)
        
    @always_seq(clock.posedge, reset=reset)
    def rtl_ramp():
        if regfile.enable and not fifobus.full:
            if wcnt == 0:
                fifobus.write.next = True
                fifobus.write_data.next = ramp
                if ramp+1 == ramp_mod:
                    rcnt.next = rcnt + 1
                ramp.next = (ramp + 1) % ramp_mod
                wcnt.next = div
            else:
                fifobus.write.next = False
                wcnt.next = wcnt - 1
        else:
            fifobus.write.next = False
            fifobus.write_data.next = 0
            wcnt.next = div
    
    return instances()
