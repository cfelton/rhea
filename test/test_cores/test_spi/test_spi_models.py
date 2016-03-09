
from myhdl import (Signal, ResetSignal, always, instance, delay,
                   StopSimulation)

from rhea.system import Global, Barebone
from rhea.utils.test import run_testbench, tb_default_args

from rhea.cores.spi import SPIBus
from rhea.cores.spi import spi_controller_model
from rhea.cores.spi import SPISlave


def test_spi_models(args=None):
    args = tb_default_args(args)
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=1, async=False)
    ibus = Barebone(clock, reset)
    spibus = SPIBus()

    def bench():

        tbdut = spi_controller_model(clock, reset, ibus, spibus)
        tbspi = SPISlave().process(spibus)

        @always(delay(3))
        def tbclk():
            clock.next = not clock

        @instance
        def tbstim():
            reset.next = reset.active
            yield delay(33)
            yield clock.posedge
            reset.next = not reset.active
            yield delay(13)
            yield clock.posedge

            yield ibus.write(0xBE)
            yield delay(100)
            yield ibus.read()

            raise StopSimulation

        return tbdut, tbspi, tbclk, tbstim

    run_testbench(bench, args=args)


if __name__ == '__main__':
    test_spi_models()
