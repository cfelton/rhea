
from myhdl import *
from _clock import Clock
from _reset import Reset

class Global:
    def __init__(self, clock=None, reset=None, frequency=1):
        self.clock = Clock(0, frequency=frequency) if clock is None else clock
        self.reset = Reset(0, active=1, async=False) if reset is None else reset
