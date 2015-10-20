
from __future__ import print_function

from random import randint
import argparse

import myhdl
from myhdl import (instance, always, delay, StopSimulation)

from rhea.system import Global, Clock, Reset
from rhea.system.stream import AXI4StreamLite
from rhea.system.stream import AXI4StreamLitePort
from rhea.system.stream import AvalonStream
from rhea.utils import keep_port_names
from rhea.utils.test import run_testbench, tb_default_args, tb_args


busmap = {
    'axi': AXI4StreamLitePort,
    'avalon': AvalonStream
}


def streamer_top(clock, reset, upstreamport, downstreamport,
                 num_registers=3, keep=True):

    if isinstance(upstreamport, AXI4StreamLitePort):
        streamtype = AXI4StreamLite
    elif isinstance(downstreamport, AvalonStream):
        streamtype = AvalonStream
    else:
        raise TypeError

    glbl = Global(clock, reset)
    upstream = streamtype(glbl, upstreamport.data_width)
    downstream = streamtype(glbl, downstreamport.data_width)

    gens = []
    gens.append(upstream.assign_port(upstreamport))
    gens.append(downstream.assign_port(downstreamport))

    if keep:
        keep_inst = keep_port_names(upstreamport=upstreamport,
                                    downstreamport=downstreamport)
        gens.append(keep_inst)

    # create a bunch of streaming registers
    up = upstream
    for ii in range(num_registers-1):
        down = streamtype(glbl, up.data_width)
        gens.append(down.register(up))
        up = down

    gens.append(downstream.register(up))

    return gens


def testbench_streamer(args=None):

    args = tb_default_args(args)

    clock = Clock(0, frequency=100e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)

    # @todo: support all stream types ...
    upstream = AXI4StreamLitePort(data_width=32)
    downstream = AXI4StreamLitePort(data_width=32)

    def _bench_streamer():
        tbdut = streamer_top(clock, reset, upstream, downstream, keep=args.keep)
        tbclk = clock.gen()

        dataout = []

        @instance
        def tbstim():
            yield reset.pulse(42)
            downstream.waccept.next = True
            downstream.awaccept.next = True
            data = [randint(0, (2**32)-1) for _ in range(10)]
            for dd in data:
                upstream.awvalid.next = True
                upstream.awdata.next = 0
                upstream.wvalid.next = True
                upstream.wdata.next = dd
                yield clock.posedge
            upstream.awvalid.next = False
            upstream.wvalid.next = False

            yield delay(100)
            print(data)
            print(dataout)
            raise StopSimulation

        @always(clock.posedge)
        def tbcap():
            if downstream.wvalid:
                dataout.append(int(downstream.wdata))

        return tbdut, tbclk, tbstim

    run_testbench(_bench_streamer, args=args)

    myhdl.toVerilog.name = "{}".format(streamer_top.__name__)
    if args.keep:
        myhdl.toVerilog.name += '_keep'
    myhdl.toVerilog.directory = 'output'
    myhdl.toVerilog(streamer_top, clock, reset, upstream, downstream)


def tb_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bustype', type=str, choices=busmap.keys(),
                        default='barebone',
                        help="The memory-mapped bus type to test")
    parser.add_argument('--keep', action='store_true', default=False,
                        help="include keeper generator")
    return parser


if __name__ == '__main__':
    # @todo add args for test, args.data_width, args.bustype, etc
    args = tb_args(parser=tb_parser())
    testbench_streamer(args)
