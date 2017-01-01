
import myhdl
from myhdl import Signal, SignalType, intbv, enum, always_seq

from rhea import Signals, Constants
from rhea.system import Global, ControlStatusObject, MemoryMapped


class ControlStatus(ControlStatusObject):
    def __init__(self):
        """Control and status signals for the eveloop controller.
        This object is a collection of control and status signals to
        the everloop controller.  This object can be used to
        statically or dynamically control the controller.  The
        attributes can also be accessed via a memory-mapped bus.
        """
        self.modes = Constants(
            off=0,      # all LEDs off
            on=1,       # all LEDs on (use colors below)
            chase=2,    # one LED on at a time
            memory=3    # load from memory
        )
        self.mode = Signal(self.modes())

        # when the "on" mode use the following to set the color
        self.red = Signal(intbv(0)[8:0])
        self.green = Signal(intbv(0)[8:0])
        self.blue = Signal(intbv(0)[8:0])
        self.white = Signal(intbv(0)[8:0])

        super(ControlStatus, self).__init__()



def everloop(glbl, led_di, led_do, cso, csb=None, num_leds=34, reset_width=80):
    """Everloop LED ring
    The everloop is a string of SK6812RGBW LEDs.  The LED is controlled
    by a 32bit word. The word is shifted in serially on a single serial
    data line.  The LEDs forward on the additional 32bit words to the
    chained LEDs.

    Args:
        glbl (Global): global signals, clock, reset, etc.
        csb (MemoryMapped): memory-mapped bus (Wishbone, Avalon, etc.).
        cso (ControlStatusObject): control-status-object.
        num_leds (int): the number of LEDs in the loop.
        reset_width (int): active-low time in microseconds, this is
         the reset time before serial transmission.

    """
    assert isinstance(glbl, Global)
    assert isinstance(csb, MemoryMapped)
    assert isinstance(cso, ControlStatusObject)

    clock, reset = glbl.clock, glbl.reset

    # the control-status interface, if
    # create a timer to generate a count to control the


everloop.cso = ControlStatus()


def everloop_p2s(glbl, data_in, start, load, so, si, num_leds=35):
    """Shift out 32 bits (data_in) to the number of chained LEDs.

    Args:
      glbl (Global):
      data_in (Input):
      start (Input):
      load (Output):
      so (Output): serial out
      si (Input): serial in

    The 32bit word is shifted into the LEDs by using a clock with
    different duty cycles:
        0: 0.3us high, 0.9us low (+/- 0.15us)
        1: 0.6us high, 0.6us low (+/- 0.15us)
    The start of the serial transmission starts with an 80us low pulse
    and then the bits follow.

    """
    assert len(data_in) == 32

    clock, reset = glbl.clock, glbl.reset
    ticks_per_usec = clock.frequency/1e6

    zero_lo = int(round(0.3*ticks_per_usec))
    zero_li = int(round(0.9*ticks_per_usec))
    one_lo = int(round(0.6*ticks_per_usec))
    one_hi = int(round(0.6*ticks_per_usec))
    reset_lo = int(round(80*ticks_per_usec))

    bcnt = Signal(intbv(0, min=0, max=32))
    ccnt = Signal(intbv(0, min=0, max=ticks_per_usec))
    lcnt = Signal(intbv(0, min=0, max=num_leds))
    data = Signal(intbv(0)[32:0])

    states = enum(
        'idle',           # wait for a new shift loop
        'start',          # start a new loop
        'reset_pulse',    # reset to the LEDs
        'shift_data',     # shift the data out
        'zero_bit',       # zero bit
        'one_bit',        # one bit
        'next_led_word',  # next word
        'end'
    )
    state = Signal(states.idle)

    @always_seq(clock.posedge, reset=reset)
    def beh_sm():

        # state-machine
        if state == states.idle:
            bcnt.next = 0
            ccnt.next = 0
            lcnt.next = 0
            load.next = False

            if start:
                state.next = states.reset_pulse
                data.next = data_in

        elif state == states.reset_pulse:
            if ccnt >= reset_lo-1:
                so.next = True
                state.next = states.shift_data
                ccnt.next = 0
            else:
                so.next = False
                ccnt.next = ccnt + 1

        elif state == states.shift_data:
            ccnt.next = 0
            if data[bcnt] == 0:
                state.next = states.zero_bit
            else:
                state.next = states.one_bit

        elif state == states.zero_bit:
            pass

        elif state == states.one_bit:
            pass

    return myhdl.instances()
