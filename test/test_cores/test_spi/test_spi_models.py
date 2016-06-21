
import myhdl
from myhdl import instance, delay, StopSimulation

from rhea.system import Global, Clock, Barebone
from rhea.utils.test import run_testbench, tb_default_args

from rhea.cores.spi import SPIBus
from rhea.cores.spi import spi_controller_model
from rhea.cores.spi import SPISlave


def test_spi_models(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=125e6)
    glbl = Global(clock)
    ibus = Barebone(glbl)
    spibus = SPIBus()

    @myhdl.block
    def bench_spi_models():

        tbdut = spi_controller_model(clock, ibus, spibus)
        tbspi = SPISlave().process(spibus)
        tbclk = clock.gen()

        @instance
        def tbstim():
            yield clock.posedge

            yield ibus.writetrans(0x00, 0xBE)
            yield delay(100)
            yield ibus.readtrans(0x00)

            raise StopSimulation

        return tbdut, tbspi, tbclk, tbstim

    run_testbench(bench_spi_models, args=args)


if __name__ == '__main__':
    test_spi_models()
