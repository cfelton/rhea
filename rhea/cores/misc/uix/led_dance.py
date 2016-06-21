
from __future__ import absolute_import

import myhdl
from myhdl import Signal, intbv, modbv, always_seq, concat
from .. import assign


@myhdl.block
def led_dance(clock, reset, leds, led_rate=33e-3):
    """An interesting LED pattern

    Arguments:
        clock: system clock
        reset: system reset
        leds: LED bits

    Parameters:
        led_rate: the rate to blink, in seconds
    """
    cnt_max = int(clock.frequency * led_rate)
    clk_cnt = Signal(intbv(1, min=0, max=cnt_max))
    rled = Signal(modbv(0)[len(leds):])

    # assign the port LED to the internal register led
    assign(leds, rled)

    # @todo: create a module to select a rate strobe,
    #    the module will return a signal that is from
    #    an existing rate or a generator and signal
    mb = len(leds)-1
    d = modbv(0)[len(leds):]

    @always_seq(clock.posedge, reset=reset)
    def beh():
        if clk_cnt == 0:
            d[:] = (rled ^ 0x81) << 1
            rled.next = concat(d, rled[mb])
        clk_cnt.next = clk_cnt + 1

    return myhdl.instances()
