
class ControlStatus(ControlStatusObject):
    def __init__(self):
        """Control and status signals for the eveloop controller.
        This object is a collection of control and status signals to
        the everloop controller.  This object can be used to
        statically or dynamically control the controller.  The
        attributes can also be accessed via a memory-mapped bus.
        """
        self.modes = enum('on', 'off', 'chase', 'memory')
        self.mode = Signal(self.modes)
        super(ControlStatus, self).__init__()


def everloop(glbl, csb, cso, num_leds=34, reset_width=80):
    """Everloop LED ring
    The everloop is a string of SK6812RGBW LEDs.  The LED is controlled
    by a 32bit word. The word is shifted in serially on a single serial
    data line.  The LEDs forward on the additional 32bit words to
    chained LEDs.

    Args:
        glbl (Global): global signals, clock, reset, etc.
        csb (MemoryMapped): memory-mapped bus (Wishbone, Avalon, etc.).
        cso (ControlStatusObject): control-status-object.
        num_leds (int): the number of LEDs in the loop.
        reset_width (int): active-low time in microseconds, this is
         the reset time before serial transmission.

    The 32bit word is shifted into the LEDs by using a clock with
    different duty cycles:
        0: 0.3us high, 0.9us low (+/- 0.15us)
        1: 0.6us high, 0.6us low (+/- 0.15us)

    """
    clock, reset = glbl.clock, glbl.reset

    # if the global ticks is not present create a local counter
    # and determine the number of ticks.


everloop.cso = ControlStatus()