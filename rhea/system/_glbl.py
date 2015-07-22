
from myhdl import *
from _clock import Clock
from _reset import Reset

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

        self.enable = Signal(bool(0))