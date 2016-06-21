#
# Copyright (c) 2006-2013 Christopher L. Felton
#

from __future__ import absolute_import

import myhdl
from myhdl import Signal, intbv, always_comb, always_seq
from rhea.system import Global, FIFOBus
from ._regfile_def import regfile


@myhdl.block
def fifo_ramp(glbl, regbus, fifobus, base_address=0x00):
    """ FIFO Ramp module
    This module provides a simple 8-bit counter that will generate
    a ramp.  This ramp is fed to the USB fifo.  This can be used
    to validate the usb connection and the device to host (IN) data
    rates.
    """
    assert isinstance(glbl, Global)
    assert isinstance(fifobus, FIFOBus)
    clock, reset = glbl.clock, glbl.reset
    regfile.base_address = base_address
    regbus_inst = regbus.add(regfile, 'fifo_ramp')
    
    enable = Signal(False)
    ramp = Signal(intbv(0)[fifobus.width:])
    wcnt = Signal(intbv(0x3FF)[32:])
    div = Signal(intbv(0)[32:])
    rcnt = Signal(intbv(0)[32:])

    # ?? not sure if this makes sense ??
    ramp_mod = int(2**fifobus.width)

    @always_comb
    def beh_assign():
        regfile.cnt3.next = (rcnt >> 24) & 0xFF
        regfile.cnt2.next = (rcnt >> 16) & 0xFF
        regfile.cnt1.next = (rcnt >> 8) & 0xFF
        regfile.cnt0.next = rcnt & 0xFF
        
    @always_seq(clock.posedge, reset=reset)
    def beh_reg():
        enable.next = regfile.enable
        div.next = ((regfile.div3 << 24) | 
                    (regfile.div2 << 16) |
                    (regfile.div1 << 8) |
                     regfile.div0)
        
    @always_seq(clock.posedge, reset=reset)
    def beh_ramp():
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
    
    return myhdl.instances()
