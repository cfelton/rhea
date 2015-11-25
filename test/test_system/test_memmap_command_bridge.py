
from __future__ import print_function
from __future__ import division

import traceback

from myhdl import (instance, delay, StopSimulation,)

from rhea.system import Global, Clock, Reset
from rhea.system import Barebone, FIFOBus
from rhea.cores.memmap import memmap_command_bridge
from rhea.cores.fifo import fifo_fast
from rhea.utils import CommandPacket
from rhea.utils.test import run_testbench, tb_args, tb_default_args


def test_memmap_command_bridge(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    fbtx, fbrx = FIFOBus(), FIFOBus()
    memmap = Barebone(glbl)

    fbtx.clock = clock
    fbrx.clock = clock

    def _bench_command_bridge():
        tbdut = memmap_command_bridge(glbl, fbtx, fbrx, memmap)
        tbfii = fifo_fast(clock, reset, fbtx)
        tbfio = fifo_fast(clock, reset, fbrx)
        tbclk = clock.gen()

        @instance
        def tbstim():
            yield reset.pulse(32)

            try:
                pkt = CommandPacket(True, 0x0000)
                yield pkt.put(fbtx)
                yield pkt.get(fbrx)
            except Exception as err:
                print("Error: {}".format(str(err)))
                traceback.print_exc()

            yield delay(2000)
            raise StopSimulation

        return tbdut, tbfii, tbfio, tbclk, tbstim

    run_testbench(_bench_command_bridge, args=args)


if __name__ == '__main__':
    test_memmap_command_bridge(tb_args())
