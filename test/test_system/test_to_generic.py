
from math import ceil, log
from random import randint
import argparse

from myhdl import (instance, delay, StopSimulation)

from rhea.system import Clock, Reset, Global
from rhea.system import Barebone, Wishbone, AvalonMM, AXI4Lite
from rhea.cores.memmap import memmap_peripheral_memory

from rhea.utils.test import run_testbench, tb_args, tb_default_args

busmap = {'barebone': Barebone,
          'wishbone': Wishbone,
          'avalon': AvalonMM,
          'axi': AXI4Lite}


def testbench_to_generic(args=None):
    """ Test memory-mapped bus and the mapping to a generic bus

    :param args:
    :return:
    """
    depth = 16    # number of memory address
    width = 32    # memory-mapped bus data width
    maxval = 2**width
    address_width = int(ceil(log(depth, 2)))

    run = False if args is None else True
    args = tb_default_args(args)

    if not hasattr(args, 'num_loops'):
        args.num_loops = 10

    clock = Clock(0, frequency=100e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)

    if hasattr(args, 'bustype'):
        membus = busmap[args.bustype](glbl, data_width=width,
                                      address_width=address_width)
    else:
        membus = Barebone(glbl, data_width=width,
                          address_width=address_width)

    def _bench_to_generic():
        tbdut = memmap_peripheral_memory(membus, depth=depth)
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
            yield clock.posedge

            for ii in range(args.num_loops):
                randaddr = randint(0, depth-1)
                randdata = randint(0, maxval-1)
                testvals[randaddr] = randdata
                yield membus.writetrans(randaddr, randdata)
            yield clock.posedge

            for addr, data in testvals.items():
                yield membus.readtrans(addr)
                read_data = membus.get_read_data()
                assert read_data == data, "{:08X} != {:08X}".format(read_data, data)
            yield clock.posedge

            yield delay(100)
            raise StopSimulation

        return tbdut, tbclk, tbstim

    if run:
        run_testbench(_bench_to_generic, args=args)


def test_barebone():
    testbench_to_generic(argparse.Namespace(bustype='barebone'))


if __name__ == '__main__':
    args = tb_args()
    testbench_to_generic(args)