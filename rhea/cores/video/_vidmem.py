
import math
from myhdl import *

class VideoMemory:
    def __init__(self, size=128, res=(640,480,), width=10):
        aw = math.ceil(math.log(size,2))
        width = width * 3
        # write port
        #self.wr = Signal(bool(0))
        #self.wdat = Signal(intbv(0)[width:])
        #self.wadr = Signal(intbv(0)[aw:])
        
        self.wr = Signal(bool(0))
        self.hpxl = Signal(intbv(0, min=0, max=res[0])) # column
        self.vpxl = Signal(intbv(0, min=0, max=res[1])) # row
        self.red = Signal(intbv(0)[width:])
        self.green = Signal(intbv(0)[width:])
        self.blue = Signal(intbv(0)[width:])

        # the memory, if large, eternal required
        # @todo: check the size, if larger than??
        #self.mem = [Signal(intbv(0)[width:]) for _ in range(size)]
