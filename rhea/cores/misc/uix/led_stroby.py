#
# Copyright (c) 2011-2013 Christopher Felton
# See the licence file in the top directory
#

"""
Full tutorial available at:
http://www.fpgarelated.com/showarticle/25.php
"""

import myhdl
from myhdl import Signal, intbv, always_seq, always_comb


@myhdl.block
def led_stroby(clock, reset, leds, led_rate=333e-3, num_dumb=4):
    """ strobe the LED
    This module will create an LED blink pattern that moves a
    single on LED across a bank of LEDs.

    Arguments:
        clock: system clock
        reset: system reset
        leds: LED bits

    Parameters:
        led_rate: the rate, in seconds, to blink the LEDs
        num_dumb: the number of dummy LEDs on each side
    """

    # Number of LEDs
    led_bank = len(leds)
    
    # Need to calculate some constants.  Want the value to
    # be an integer (non-fractional value only whole number)
    cnt_max = int(clock.frequency * led_rate)   
    
    # Some useful definitions (constants)
    mb = led_bank + 2*num_dumb
    lsb, msb = (0, mb-1,)
    msb_reverse_val = (1 << mb-2)
    lsb_reverse_val = 2
    
    # Declare the internal Signals in our design
    led_bit_mem = Signal(intbv(1)[mb:])
    left_not_right = Signal(True)
    clk_cnt = Signal(intbv(0, min=0, max=cnt_max))
    strobe = Signal(False)

    @always_seq(clock.posedge, reset=reset)
    def beh():
        # Generate the strobe event, use the "greater
        # than" for initial condition cases.  Count the
        # number of clock ticks that equals the LED strobe rate
        if clk_cnt >= cnt_max-1:
            clk_cnt.next = 0
            strobe.next = True
        else:
            clk_cnt.next = clk_cnt + 1
            strobe.next = False
        
        # The following always changes direction and "resets" when
        # either the lsb or msb is set.  This handles our initial 
        # condition as well.
        if strobe:
            if led_bit_mem[msb]:
                led_bit_mem.next = msb_reverse_val
                left_not_right.next = False
            elif led_bit_mem[lsb]:
                led_bit_mem.next = lsb_reverse_val
                left_not_right.next = True
            else:
                if left_not_right:
                    led_bit_mem.next = led_bit_mem << 1
                else:
                    led_bit_mem.next = led_bit_mem >> 1

    @always_comb
    def beh_map_output():
        leds.next = led_bit_mem[led_bank+num_dumb:num_dumb]
        
    return myhdl.instances()
