
from myhdl import Signal, intbv


class VideoStream(object):
    def __init__(self):
        self.valid = Signal(bool(0))
        self.red = Signal(intbv(0)[8:0])
        self.green = Signal(intbv(0)[8:0])
        self.blue = Signal(intbv(0)[8:0])