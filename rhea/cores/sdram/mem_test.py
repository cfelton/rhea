
from __future__ import absolute_import

import myhdl
from myhdl import Signal, enum, always_seq
# from ..misc import random_generator


def mem_test(glbl, memmap, progress, error, done,
        start_address=0x00000000, end_address=0xFFFFFFFF):
    """
    This module performs a memory test over the memory-map bus
    """
    if end_address > memmap.addr.max:
        end_address = memmap.addr.max

    States = enum('init', 'write', 'write_ack', 'compare_read',
                  'compare', 'end')
    state = Signal(States.init)

    clock, reset = glbl.clock, glbl.reset

    rglbl, randgen = random_generator.portmap.values()
    randgen.data = Signal(memmap.wdata.val)
    rglbl.clock, rglbl.reset = clock, reset
    rand_inst = random_generator(glbl, randgen)

    @always_seq(clock.posedge, reset=reset)
    def beh():

        # defaults
        randgen.load.next = False
        randgen.enable.next = False

        if state == States.init:
            randgen.load.next = True
            randgen.enable.next = True
            error.next = False
            progress.next = 0
            memmap.addr.next = start_address

        elif state == States.write:
            progress.next = 1
            memmap.write.next = True
            memmap.wdata.next = randgen.data
            state.next = States.write.ack
            randgen.enable.next = True

        elif state == States.write_ack:
            memmap.write.next = False
            if memmap.addr == end_address-1:
                randgen.load.next = True
                state.next = States.compare_read
                memmap.addr.next = start_address
            else:
                memmap.addr.next = memmap.addr + 1
                state.next = States.write

        elif state == States.compare_read:
            progress.next = 2
            memmap.read.next = True

        elif state == States.compare:
            memmap.read.next = False
            randgen.enable.next = True
            if memmap.rdata != randgen.data:
                error.next = True

            if memmap.addr == end_address-1:
                state.next = States.end
            else:
                memmap.addr.next = memmap.addr + 1
                state.next = States.compare.read

        elif state == States.end:
            pass

        else:
            assert False, "Invalid state %s" % (state,)

    return myhdl.instances()
