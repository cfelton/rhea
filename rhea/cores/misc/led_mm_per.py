
from __future__ import division
from __future__ import absolute_import

from myhdl import Signal, intbv, always_seq

from ...system import RegisterFile
from ...system import Register

from . import assign
from . import led_stroby
from . import led_count
from . import led_dance

# create a simple register file for the "core"
regfile = RegisterFile()
select = Register("select", width=8, access='rw')
regfile.add_register(select)


def led_peripheral(glbl, regbus, leds, base_address=0x8240):
    """ LED memory-map peripheral
    This (rather silly) core will select different LED
    displays based on the memory-mapped select register.
    """

    ndrv = 3  # the number of different drivers
    regfile.base_address = base_address 
    
    clock, reset = glbl.clock, glbl.reset
    rleds = Signal(intbv(0)[len(leds):])

    # assign the LED port to the local register
    gas = assign(leds, rleds)

    # memory-mapped registers
    greg = regbus.add(regfile, 'led')

    # led bus from each driver
    dled = [Signal(intbv(0)[len(leds):]) 
            for _ in range(ndrv)]

    # instantiate different LED drivers
    gl = [None for _ in range(ndrv)]
    gl[0] = led_stroby(clock, reset, dled[0])
    gl[1] = led_count(clock, reset, dled[1])
    gl[2] = led_dance(clock, reset, dled[2])

    @always_seq(clock.posedge, reset=reset)
    def rtl():
        for ii in range(ndrv):
            idx = regfile.select
            rleds.next = dled[idx-1]

    return gas, gl, greg, rtl
