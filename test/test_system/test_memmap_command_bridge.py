
"""
Test and verify the memory-mapped command bridge (memmap_command_bridge).

Unlike the actual designs this test does not use a generic peripheral
but instead a specific peripheral / slave is used for each bus type,
other tests verify the generic ability.
"""

from __future__ import print_function, division

from random import randint
import traceback

import myhdl
from myhdl import (Signal, intbv, always_seq, always_comb,
                   instance, delay, StopSimulation,)

from rhea import Global, Clock, Reset, Signals
from rhea.system import Barebone, FIFOBus
from rhea.cores.memmap import command_bridge
from rhea.cores.fifo import fifo_fast
from rhea.utils import CommandPacket
from rhea.utils.test import run_testbench, tb_args, tb_default_args


@myhdl.block
def memmap_peripheral_bb(clock, reset, bb):
    """ Emulate Barebone memory-mapped reads and writes"""
    assert isinstance(bb, Barebone)
    mem = {}

    @always_seq(clock.posedge, reset=reset)
    def beh_writes():
        addr = int(bb.address)
        bb.done.next = not (bb.write or bb.read)
        if bb.write:
            mem[addr] = int(bb.write_data)

    @always_comb
    def beh_reads():
        addr = int(bb.address)
        if bb.read:
            if addr not in mem:
                mem[addr] = 0
            bb.read_data.next = mem[addr]
        else:
            bb.read_data.next = 0

    return beh_writes, beh_reads


def test_memmap_command_bridge(args=None):
    nloops = 37
    args = tb_default_args(args)
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    fifobus = FIFOBus()
    memmap = Barebone(glbl, data_width=32, address_width=28)

    fifobus.clock = clock

    @myhdl.block
    def bench_command_bridge():
        tbclk = clock.gen()
        tbdut = command_bridge(glbl, fifobus, memmap)

        readpath, writepath = FIFOBus(), FIFOBus()
        readpath.clock = writepath.clock = clock
        tbmap = fifobus.assign_read_write_paths(readpath, writepath)
        tbftx = fifo_fast(glbl, writepath)   # user write path
        tbfrx = fifo_fast(glbl, readpath)    # user read path

        # @todo: add other bus types
        tbmem = memmap_peripheral_bb(clock, reset, memmap)

        # save the data read ...
        read_value = []

        @instance
        def tbstim():
            yield reset.pulse(32)
            fifobus.read.next = False
            fifobus.write.next = False
            assert not fifobus.full
            assert fifobus.empty
            assert fifobus.read_data == 0
            fifobus.write_data.next = 0

            try:
                # test a single address
                pkt = CommandPacket(True, 0x0000)
                yield pkt.put(readpath)
                yield pkt.get(writepath, read_value, [0])

                pkt = CommandPacket(False, 0x0000, [0x5555AAAA])
                yield pkt.put(readpath)
                yield pkt.get(writepath, read_value, [0x5555AAAA])

                # test a bunch of random addresses
                for ii in range(nloops):
                    randaddr = randint(0, (2**20)-1)
                    randdata = randint(0, (2**32)-1)
                    pkt = CommandPacket(False, randaddr, [randdata])
                    yield pkt.put(readpath)
                    yield pkt.get(writepath, read_value, [randdata])

            except Exception as err:
                print("Error: {}".format(str(err)))
                traceback.print_exc()

            yield delay(2000)
            raise StopSimulation

        wp_read, wp_valid = Signals(bool(0), 2)
        wp_read_data = Signal(intbv(0)[8:])
        wp_empty, wp_full = Signals(bool(0), 2)

        @always_comb
        def tbmon():
            wp_read.next = writepath.read
            wp_read_data.next = writepath.read_data
            wp_valid.next = writepath.read_valid
            wp_full.next = writepath.full
            wp_empty.next = writepath.empty

        return tbclk, tbdut, tbmap, tbftx, tbfrx, tbmem, tbstim, tbmon

    run_testbench(bench_command_bridge, args=args)


if __name__ == '__main__':
    test_memmap_command_bridge(tb_args())
