
from __future__ import absolute_import

from myhdl import *
from ._clock import Clock
from ._reset import Reset

class Global:
    """ global clock, reset, and control signals """

    def __init__(self, clock=None, reset=None, frequency=1):
        if clock is None:
            self.clock = Clock(0, frequency=frequency) 
        else:
            self.clock = clock
        
        if reset is None:            
            self.reset = Reset(0, active=1, async=False) 
        else:
            self.reset = reset

        # global enable signal
        self.enable = Signal(bool(0))

        # timer ticks
        # @todo: future enhancement, tick_user should be a list-of-signals
        # @todo: so more than one custom (tick_user) can be generated.
        self.tick_ms = Signal(bool(0))
        self.tick_sec = Signal(bool(0))
        self.tick_user = Signal(bool(0))
