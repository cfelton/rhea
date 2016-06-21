
import myhdl
from myhdl import Signal, intbv, modbv, always_seq
from .. import assign


@myhdl.block
def led_count(clock, reset, leds, led_rate=333e-3):
    """LED count
    Increment a counter at a rate that is visible on a
    bank of LEDs.

    Arguments:
        clock: system clock
        reset: system reset
        leds (Signal(intbv)): LED bits

    myhdl convertible
    """
    cnt_max = int(clock.frequency * led_rate)
    clk_cnt = Signal(intbv(1, min=0, max=cnt_max))
    rled = Signal(modbv(0)[len(leds):])

    # assign the port LED to the internal register led
    assign(leds, rled)

    # @todo: create a module to select a rate strobe,
    #    the module will return a signal that is from
    #    an existing rate or a generator and signal
    @always_seq(clock.posedge, reset=reset)
    def beh():
        if clk_cnt == 0:
            rled.next = rled + 1
        clk_cnt.next = clk_cnt + 1

    return myhdl.instances()
