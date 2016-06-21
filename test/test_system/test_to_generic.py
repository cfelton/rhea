
from math import ceil, log
from random import randint
import argparse

import pytest
import myhdl
from myhdl import (instance, delay, StopSimulation)

from rhea.system import Clock, Reset, Global
from rhea.system import Barebone, Wishbone, AvalonMM, AXI4Lite
from rhea.cores.memmap import peripheral_memory

from rhea.utils.test import run_testbench, tb_args, tb_default_args

busmap = {'barebone': Barebone,
          'wishbone': Wishbone,
          'avalon': AvalonMM,
          'axi': AXI4Lite}


pytest.skip(msg="simulator crashes, duplicate error, causes next to fail")
def testbench_to_generic(args=None):
    """ Test memory-mapped bus and the mapping to a generic bus

    :param args:
    :return:
    """
    depth = 16    # number of memory address
    width = 32    # memory-mapped bus data width
    maxval = 2**width

    run = False if args is None else True
    args = tb_default_args(args)

    if not hasattr(args, 'num_loops'):
        args.num_loops = 10

    clock = Clock(0, frequency=100e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)

    if hasattr(args, 'bustype'):
        address_width = 18
        membus = busmap[args.bustype](glbl, data_width=width,
                                      address_width=address_width)
    else:
        address_width = int(ceil(log(depth, 2))) + 4
        membus = Barebone(glbl, data_width=width,
                          address_width=address_width)

    @myhdl.block
    def bench_to_generic():
        tbdut = peripheral_memory(membus, depth=depth)
        tbitx = membus.interconnect()
        tbclk = clock.gen()
        testvals = {}

        @instance
        def tbstim():
            yield reset.pulse(42)
            yield clock.posedge

            # only testing one peripheral, set the peripheral/slave
            # address to the first ...
            if isinstance(membus, Barebone):
                membus.per_addr.next = 1
                peraddr = 0
            else:
                peraddr = 0x10000

            yield clock.posedge

            for ii in range(args.num_loops):
                randaddr = randint(0, depth-1) | peraddr
                randdata = randint(0, maxval-1)
                testvals[randaddr] = randdata
                yield membus.writetrans(randaddr, randdata)
            yield clock.posedge

            for addr, data in testvals.items():
                yield membus.readtrans(addr)
                read_data = membus.get_read_data()
                assert read_data == data, "{:08X} != {:08X}".format(
                    read_data, data)
            yield clock.posedge

            yield delay(100)
            raise StopSimulation

        return tbdut, tbitx, tbclk, tbstim

    if run:
        run_testbench(bench_to_generic, args=args)


def test_barebone():
    testbench_to_generic(argparse.Namespace(bustype='barebone'))


pytest.skip(msg="simulator crashes, duplicate error, causes next to fail")
def test_wishbone():
    testbench_to_generic(argparse.Namespace(bustype='wishbone'))


def tb_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bustype', type=str, choices=busmap.keys(),
                        default='barebone',
                        help="The memory-mapped bus type to test")
    return parser


if __name__ == '__main__':
    args = tb_args(parser=tb_parser())
    testbench_to_generic(args)
