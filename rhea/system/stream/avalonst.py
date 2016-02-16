
from math import ceil, log
from myhdl import Signal, intbv
from . import Streamers


class AvalonStream(Streamers):
    def __init__(self, width=32):
        """ Interface for Avalon streaming protocol """
        numwords = int(ceil(log(width//8, 2)))
        self.data = Signal(intbv(0)[width:])
        self.empty = Signal(intbv(0)[numwords:])
        self.sop = Signal(bool(0))
        self.eop = Signal(bool(0))
        self.valid = Signal(bool(0))
        self.ready = Signal(bool(0))
        self.error = Signal(bool(0))

    def register(self, upstream):
        sti = upstream

    def assign_port(self, pobj):
        return []
