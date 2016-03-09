
from myhdl import (Signal, always, instance, delay, StopSimulation)

from rhea.system import Global, Clock, Reset, FIFOBus
from rhea.cores.spi import SPIBus, spi_slave_fifo
from rhea.utils.test import run_testbench, tb_default_args, tb_args


def test_spi_slave(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    spibus = SPIBus()
    fifobus = FIFOBus()

    def bench_spi_slave():
        tbdut = spi_slave_fifo(glbl, spibus, fifobus)
        tbclk = clock.gen()

        @instance
        def tbstim():
            yield reset.pulse(40)
            yield clock.posedge

            yield spibus.writeread(0x55)
            yield spibus.writeread(0xAA)
            assert spibus.get_read_data() == 0x55

            raise StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(bench_spi_slave, args=args)


if __name__ == '__main__':
    args = tb_args()
    test_spi_slave(args)