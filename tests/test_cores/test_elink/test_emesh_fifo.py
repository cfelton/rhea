
from __future__ import print_function, division

import pytest

import myhdl
from myhdl import (Signal, ResetSignal, intbv, modbv,
                   always, instance, delay,)

from rhea.cores.elink import EMesh
from rhea.cores.elink import EMeshSnapshot
from rhea.cores.elink import emesh_fifo

from rhea.utils.test import run_testbench, tb_args, tb_default_args


@pytest.mark.xfail(reason="started failing in 2.7, fifo changes?")
def test_emesh_fifo(args=None):
    """
    """
    args = tb_default_args(args)

    clock_a, clock_b = Signal(bool(0)), Signal(bool(0))
    reset = ResetSignal(0, active=1, async=False)
    emesh_a, emesh_b = EMesh(clock_a), EMesh(clock_b)
    input_data, output_data = [], []

    @always(delay(2500))
    def tbclka():
        clock_a.next = not clock_a

    @always(delay(1300))
    def tbclkb():
        clock_b.next = not clock_b

    @myhdl.block
    def bench_emesh_fifo():
        tbdut = emesh_fifo(reset, emesh_a, emesh_b)

        @instance
        def tbstim():
            yield delay(1111)
            for _ in range(5):
                yield clock_a.posedge

            # push a single packet and verify receipt on the other side
            yield emesh_a.write(0xDEEDA5A5, 0xDECAFBAD, 0xC0FFEE)
            input_data.append(EMeshSnapshot(emesh_a))

            for _ in range(10):
                yield clock_b.posedge

            assert len(output_data) == 1
            assert output_data[0] == input_data[0]

            raise myhdl.StopSimulation

        @always(clock_b.posedge)
        def tbcap():
            if emesh_b.txwr.access or emesh_b.txrd.access or emesh_b.txrr.access:
                print("output packet: {}".format(emesh_b))
                output_data.append(EMeshSnapshot(emesh_b))

            if emesh_a.txwr.access or emesh_a.txwr.data != 0:
                print("{}".format(emesh_a))

        # monitor an emesh (interface tracing limitations)
        emesh_a_access = Signal(bool(0))
        emesh_a_data = Signal(intbv(0)[32:0])

        emesh_b_access = Signal(bool(0))
        emesh_b_data = Signal(intbv(0)[32:0])

        cm = Signal(modbv(0)[8:])

        @always(emesh_b.clock.posedge)
        def tbmon():
            cm.next = cm + 1

            emesh_a_access.next = emesh_a.txwr.access
            emesh_a_data.next = emesh_a.txwr.data

            emesh_b_access.next = emesh_b.txwr.access
            emesh_b_data.next = emesh_b.txwr.data

        return tbclka, tbclkb, tbcap, tbmon, tbdut, tbstim

    run_testbench(bench_emesh_fifo, timescale='1ps', args=args)


if __name__ == '__main__':
    args = tb_args()
    test_emesh_fifo(args)
