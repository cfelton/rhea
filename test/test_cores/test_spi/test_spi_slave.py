
import pytest

import myhdl
from myhdl import (Signal, intbv, instance, always_comb, delay,
                   StopSimulation)

from rhea.system import Global, Clock, Reset, FIFOBus, Signals
from rhea.cores.spi import SPIBus, spi_slave_fifo
from rhea.utils.test import run_testbench, tb_default_args, tb_args


@pytest.mark.xfail()
def test_spi_slave(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    spibus, fifobus = SPIBus(), FIFOBus()

    # monitor the FIFOBus signals
    data = Signal(intbv(0)[8:])
    rd, wr, full, empty = Signals(bool(0), 4)

    @myhdl.block
    def bench_spi_slave():
        tbdut = spi_slave_fifo(glbl, spibus, fifobus)
        tbclk = clock.gen()

        @instance
        def tbstim():
            yield reset.pulse(40)
            yield delay(1000)
            yield clock.posedge

            # @todo: make generic
            # @todo: random_sequence = [randint(0, fifobus.write_data.max) for _ in range(ntx)]
            yield spibus.writeread(0x55)
            yield spibus.writeread(0xAA)
            yield spibus.writeread(0xCE)
            assert spibus.get_read_data() == 0x55
            yield spibus.writeread(0x01)
            assert spibus.get_read_data() == 0xAA
            yield spibus.writeread(0x01)
            assert spibus.get_read_data() == 0xCE

            raise StopSimulation

        @always_comb
        def tb_fifo_loopback():
            if not fifobus.full:
                fifobus.write.next = not fifobus.empty
                fifobus.read.next = not fifobus.empty
            fifobus.write_data.next = fifobus.read_data

        # monitors
        @always_comb
        def tbmon():
            data.next = fifobus.read_data
            rd.next = fifobus.read
            wr.next = fifobus.write
            full.next = fifobus.full
            empty.next = fifobus.empty

        return tbdut, tbclk, tbstim, tb_fifo_loopback, tbmon

    run_testbench(bench_spi_slave, args=args)


if __name__ == '__main__':
    args = tb_args()
    test_spi_slave(args)
