
from __future__ import print_function

from random import randint
import argparse

import myhdl
from myhdl import (instance, always, always_comb, delay, StopSimulation)

from rhea.system import Global, Clock, Reset
from rhea.system.stream import AXI4StreamLite
from rhea.system.stream import AXI4StreamLitePort
from rhea.system.stream import AvalonStream
from rhea.utils import keep_port_names
from rhea.utils.test import run_testbench, tb_default_args, tb_args, tb_convert


busmap = {
    'axi': AXI4StreamLitePort,
    'avalon': AvalonStream
}


@myhdl.block
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
    # gens.append(upstream.assign_port(upstreamport))
    # gens.append(downstream.assign_port(downstreamport))

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

    # The following is included in the top-level (kinda a pain) to preserve
    # the top-level port names and to utilize nested interfaces internally.
    # This is a current limitation and will be enhanced in the future.
    @always_comb
    def beh_upstream_assign():
        upstream.aw.valid.next = upstreamport.awvalid
        upstream.aw.data.next = upstreamport.awdata
        upstreamport.awaccept.next = upstream.aw.accept

        upstream.w.valid.next = upstreamport.wvalid
        upstream.w.data.next = upstreamport.wdata
        upstreamport.waccept.next = upstream.w.accept

        upstream.ar.valid.next = upstreamport.arvalid
        upstream.ar.data.next = upstreamport.ardata
        upstreamport.araccept.next = upstream.ar.accept

        upstreamport.rvalid.next = upstream.r.valid
        upstreamport.rdata.next = upstream.r.data
        upstream.r.accept.next = upstreamport.raccept

        upstreamport.bvalid.next = upstream.b.valid
        upstreamport.bdata.next = upstream.b.data
        upstream.b.accept.next = upstreamport.baccept

    @always_comb
    def beh_downstream_assign():
        downstreamport.awvalid.next = downstream.aw.valid
        downstreamport.awdata.next = downstream.aw.data
        downstream.aw.accept.next = downstreamport.awaccept

        downstreamport.wvalid.next = downstream.w.valid
        downstreamport.wdata.next = downstream.w.data
        downstream.w.accept.next = downstreamport.waccept

        downstreamport.arvalid.next = downstream.ar.valid
        downstreamport.ardata.next = downstream.ar.data
        downstream.ar.accept.next = downstreamport.araccept

        downstream.r.valid.next = downstreamport.rvalid
        downstream.r.data.next = downstreamport.rdata
        downstreamport.raccept.next = downstream.r.accept

        downstream.b.valid.next = downstreamport.bvalid
        downstream.b.data.next = downstreamport.bdata
        downstreamport.baccept.next = downstream.b.accept

    return gens, beh_upstream_assign, beh_downstream_assign


def testbench_streamer(args=None):

    args = tb_default_args(args)
    if not hasattr(args, 'keep'):
        args.keep = False
    if not hasattr(args, 'bustype'):
        args.bustype = 'barebone'

    clock = Clock(0, frequency=100e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)

    # @todo: support all stream types ...
    upstream = AXI4StreamLitePort(data_width=32)
    downstream = AXI4StreamLitePort(data_width=32)

    @myhdl.block
    def bench_streamer():
        tbdut = streamer_top(clock, reset, upstream, downstream, keep=args.keep)
        tbclk = clock.gen()

        dataout = []

        @instance
        def tbstim():
            yield reset.pulse(42)
            downstream.awaccept.next = True
            downstream.waccept.next = True
            data = [randint(0, (2**32)-1) for _ in range(10)]
            for dd in data:
                upstream.awvalid.next = True
                upstream.awdata.next = 0xA
                upstream.wvalid.next = True
                upstream.wdata.next = dd
                yield clock.posedge
            upstream.awvalid.next = False
            upstream.wvalid.next = False

            # @todo: wait the appropriate delay given the number of
            # @todo: streaming registers
            yield delay(100)
            print(data)
            print(dataout)
            assert False not in [di == do for di, do in zip(data, dataout)]
            raise StopSimulation

        @always(clock.posedge)
        def tbcap():
            if downstream.wvalid:
                dataout.append(int(downstream.wdata))

        return tbdut, tbclk, tbstim, tbcap

    run_testbench(bench_streamer, args=args)

    inst = streamer_top(clock, reset, upstream, downstream)
    tb_convert(inst)


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
