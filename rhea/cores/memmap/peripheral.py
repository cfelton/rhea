
from __future__ import absolute_import

import myhdl
from myhdl import Signal, intbv, always, always_comb
from rhea.system.memmap import MemoryMapped, MemorySpace


@myhdl.block
def peripheral_memory(memmap, depth=32):
    """
    Example mapping a memory-mapped (csr) bus to an internal memory
    buffer.

    (arguments == ports)
    Arguments:
        memmap: memory-mapped interface

    """
    width = 32
    mem = [Signal(intbv(0)[width:]) for _ in range(depth)]
    memspace = MemorySpace()
    memmap.add(memspace)
    per_addr = memspace.base_address
    print("memmap_peripheral_memory base address {:08X}".format(per_addr))

    # @todo: add MemorySpace to the memmap bus, so the memmap object
    # @todo: knows the address space occupied by this peripheral
    inprog = Signal(bool(0))
    newtrans = Signal(bool(0))

    assert isinstance(memmap, MemoryMapped)
    clock = memmap.clock
    mm = memmap.get_generic()
    conv_inst = memmap.map_to_generic(mm)

    @always(clock.posedge)
    def beh_write():
        if newtrans and not inprog and mm.per_addr == per_addr:
            if mm.write or mm.read:
                inprog.next = True
            if mm.write:
                mem[mm.mem_addr].next = mm.write_data
        elif inprog and mm.write:
            mem[mm.mem_addr].next = mm.write_data
        else:
            # clear wait once other strobes are cleared, not burst writes
            if not mm.write and not mm.read:
                inprog.next = False

    @always_comb
    def beh_read():
        if mm.per_addr == per_addr and not mm.done:
            mm.read_data.next = mem[mm.mem_addr]
        else:
            mm.read_data.next = 0

    @always_comb
    def beh_newtrans():
        newtrans.next = (mm.write or mm.read) and not inprog

    @always_comb
    def beh_done():
        mm.done.next = not newtrans and not inprog

    return conv_inst, beh_write, beh_read, beh_newtrans, beh_done


@myhdl.block
def peripheral(memmap):
    # @todo: move regfilesys to here!
    memspace = MemorySpace()
    memmap.add(memspace)
    mm = memmap.get_generic()
    placeholder = Signal(bool(0))

    @always_comb
    def beh_todo():
        if mm.write:
            placeholder.next = True
        else:
            placeholder.next = False

    return beh_todo
