
from __future__ import division, absolute_import

import myhdl
from myhdl import Signal, intbv, always
from rhea.system import Register, RegisterFile
from . import led_stroby, led_count, led_dance


# create a register file
regfile = RegisterFile()

# create a status register and add it to the register file
reg = Register('status', width=8, access='ro', default=0)
regfile.add_register(reg)

# create a control register with named bits and add
reg = Register('control', width=8, access='rw', default=1)
reg.add_namedbits('enable', bits=0, comment="enable the compoent")
reg.add_namedbits('pause', bits=1, comment="pause current operation")
reg.add_namedbits('mode', bits=(4, 2), comment="select mode")
regfile.add_register(reg)


@myhdl.block
def led_blinker(glbl, membus, leds):
    clock = glbl.clock
    # instantiate the register interface module and add the 
    # register file to the list of memory-spaces
    regfile.base_address = 0x8240
    regfile_inst = membus.add(glbl, regfile)    
    
    # instantiate different LED blinking modules
    led_modules = (led_stroby, led_dance, led_count,)
    led_drivers = [Signal(leds.val) for _ in led_modules]
    mod_inst = []
    for ii, ledmod in enumerate(led_modules):
        mod_inst.append(ledmod(glbl, led_drivers[ii]))
        
    @always(clock.posedge)
    def beh_led_assign():
        leds.next = led_drivers[regfile.mode]
        
    return regfile_inst, mod_inst, beh_led_assign
