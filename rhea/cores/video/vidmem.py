
import math
import myhdl
from myhdl import Signal, intbv, always_comb, always, concat


class VideoMemory:
    def __init__(self, resolution=(640, 480,), color_depth=(8, 8, 8)):

        self.size = resolution[0] * resolution[1]
        self.aw = math.ceil(math.log(self.size, 2))  # address width
        self.width = sum(color_depth)           # width of each memory element

        # write port strobe for write port
        self.wr = Signal(bool(0))

        # pixel address, for the read and write port
        self.hpxl = Signal(intbv(0, min=0, max=resolution[0]))  # column
        self.vpxl = Signal(intbv(0, min=0, max=resolution[1]))  # row

        self.red = Signal(intbv(0)[color_depth[0]:])
        self.green = Signal(intbv(0)[color_depth[1]:])
        self.blue = Signal(intbv(0)[color_depth[2]:])


@myhdl.block
def video_memory(glbl, vidmem_write, vidmem_read):
    """
    """
    assert vidmem_write.width == vidmem_read.width
    vmem = vidmem_write
    res = vmem.resolution
    mem = [Signal(intbv(0)[vmem.width:]) for _ in range(vmem.size)]

    clock, reset = glbl.clock, glbl.reset

    # address translation
    waddr = Signal(intbv(0, min=0, max=vmem.size))

    @always_comb
    def beh_addr():
        # @todo: this will be expensive, shortcut/hack ???
        waddr.next = vmem.hpxl + (vmem.vpxl * vmem.resolution[0])

    # write
    @always(clock.posedge)
    def beh_write():
        if vidmem_write.wr:
            mem[waddr].next = concat(vmem.red, vmem.green, vmem.blue)

    return myhdl.instances()