

from myhdl import Signal, intbv, modbv, always_seq
from . import assign


def led_count(
  # ~~~[Ports]~~~
  clock,             # input : system sync clock
  reset,             # input : reset (level determined by RST_LEVEL)
  leds,              # output : to IO ports drive LEDs

  # ~~~[Parameters]~~~
  led_rate=333e-3,   # strobe change rate of 333ms
):
    """
    """
    gens = []  # get all the generators

    cnt_max = int(clock.frequency * led_rate)
    clk_cnt = Signal(intbv(1, min=0, max=cnt_max))
    rled = Signal(modbv(0)[len(leds):])

    # assign the port LED to the internal register led
    gas = assign(leds, rled)

    # @todo: create a module to select a rate strobe,
    #    the module will return a signal that is from
    #    an existing rate or a generator and signal
    @always_seq(clock.posedge, reset=reset)
    def rtl():
        if clk_cnt == 0:
            rled.next = rled + 1
        clk_cnt.next = clk_cnt + 1

    gens += (rtl,)
    return gas, rtl
