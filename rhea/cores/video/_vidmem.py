
import math
from myhdl import *


class VideoMemory:
    def __init__(self, resolution=(640, 480,), color_depth=(8, 8, 8)):

        self.size = resolution[0] * resolution[1]
        self.aw = math.ceil(math.log(self.size, 2))  # address width
        self.width = sum(color_depth)           # width of each memory element

        self.wr = Signal(bool(0))
        self.hpxl = Signal(intbv(0, min=0, max=resolution[0]))  # column
        self.vpxl = Signal(intbv(0, min=0, max=resolution[1]))  # row

        # @todo: hpxl and vplx read

        self.red = Signal(intbv(0)[color_depth[0]:])
        self.green = Signal(intbv(0)[color_depth[1]:])
        self.blue = Signal(intbv(0)[color_depth[2]:])

        # the memory, if large, eternal required
        # @todo: check the size, if larger than ??
        self.mem = [Signal(intbv(0)[width:]) for _ in range(size)]

        # @todo: create an actual memory (dual port
        # def memory(self):
        #     """
        #        vin : v
        #     """
        #


def video_memory(glbl, vidmem_write, vidmem_read):
    """
    """
    assert vidmem_write.width == vidmem_write.width
    vmem = vidmem_write
    res = vmem.resolution
    mem = [Signal(intbv(0)[vmem.width:]) for _ in range(vmem.size)]

    clock, reset = glbl.clock, glbl.reset

    # address translation
    addr = Signal(intbv(0, min=0, max=vmem.size))

    @always_comb
    def rtl_addr():
        # @todo: this will be expensive, shortcut/hack ???
        addr.next = vmem.hpxl + (vmem.vpxl * vmem.resolution[0])

    # write
    @always(clock.posedge)
    def rtl():
        if vidmem_write.wr:
            mem