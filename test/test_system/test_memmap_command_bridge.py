
from __future__ import print_function
from __future__ import division

"""
Test and verify the memory-mapped command bridge (memmap_command_bridge).

Unlike the actual designs this test does not use a generic peripheral
but instead a specific peripheral / slave is used for each bus type,
other tests verify the generic ability.
"""

from random import randint
import traceback
from pprint import pprint

from myhdl import (always_seq, always_comb, instance, delay,
                   StopSimulation,)

from rhea.system import Global, Clock, Reset
from rhea.system import Barebone, FIFOBus
from rhea.cores.memmap import memmap_command_bridge
from rhea.cores.fifo import fifo_fast
from rhea.utils import CommandPacket
from rhea.utils.test import run_testbench, tb_args, tb_default_args


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
    fbtx, fbrx = FIFOBus(), FIFOBus()
    memmap = Barebone(glbl, data_width=32, address_width=28)

    fbtx.clock = clock
    fbrx.clock = clock

    def _bench_command_bridge():
        tbclk = clock.gen()
        tbdut = memmap_command_bridge(glbl, fbtx, fbrx, memmap)
        tbfii = fifo_fast(clock, reset, fbtx)
        tbfio = fifo_fast(clock, reset, fbrx)
        # @todo: add other bus types
        tbmem = memmap_peripheral_bb(clock, reset, memmap)

        # save the data read ...
        read_value = []

        @instance
        def tbstim():
            yield reset.pulse(32)

            try:
                # test a single address
                pkt = CommandPacket(True, 0x0000)
                yield pkt.put(fbtx)
                yield pkt.get(fbrx, read_value, [0])
                pkt = CommandPacket(False, 0x0000, [0x5555AAAA])
                yield pkt.put(fbtx)
                yield pkt.get(fbrx, read_value, [0x5555AAAA])

                # test a bunch of random addresses
                for ii in range(nloops):
                    randaddr = randint(0, (2**20)-1)
                    randdata = randint(0, (2**32)-1)
                    pkt = CommandPacket(False, randaddr, [randdata])
                    yield pkt.put(fbtx)
                    yield pkt.get(fbrx, read_value, [randdata])

            except Exception as err:
                print("Error: {}".format(str(err)))
                traceback.print_exc()

            yield delay(2000)
            raise StopSimulation

        return tbclk, tbdut, tbfii, tbfio, tbmem, tbstim

    run_testbench(_bench_command_bridge, args=args)


if __name__ == '__main__':
    test_memmap_command_bridge(tb_args())
