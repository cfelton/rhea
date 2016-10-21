
from __future__ import division

from random import randint

import myhdl
from myhdl import (Signal, always_comb, instance, delay, StopSimulation, )

from rhea.cores.uart import uartlite
from rhea.models.uart import UARTModel

from rhea import Global, Clock, Reset
from rhea.system import FIFOBus

from rhea.utils.test import run_testbench, tb_args
from rhea.utils.test import skip_long_sim_test


def test_uart_model(args=None):
    # @todo: get numbytes from args
    numbytes = 7
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=True)
    glbl = Global(clock, reset)
    si, so = Signal(bool(1)), Signal(bool(1))
    uartmdl = UARTModel()

    @myhdl.block
    def bench_uart_model():
        tbdut = uartmdl.process(glbl, si, so)
        tbclk = clock.gen()

        @always_comb
        def tblpbk():
            si.next = so

        @instance
        def tbstim():
            yield reset.pulse(33)
            yield delay(1000)
            yield clock.posedge

            for ii in range(numbytes):
                wb = randint(0, 255)
                print("send {:02X}".format(wb))
                uartmdl.write(wb)
                timeout = ((clock.frequency/uartmdl.baudrate) * 20)
                rb = uartmdl.read()
                while rb is None and timeout > 0:
                    yield clock.posedge
                    rb = uartmdl.read()
                    timeout -= 1
                if rb is None:
                    raise TimeoutError
                print("received {:02X}".format(rb))
                assert rb == wb, "{:02X} != {:02X}".format(rb, wb)

            yield delay(100)

            raise StopSimulation

        return tbdut, tbclk, tblpbk, tbstim

    run_testbench(bench_uart_model, args=args)


@skip_long_sim_test
def test_uart(args=None):
    # @todo: get numbytes from args
    numbytes = 13
    clock = Clock(0, frequency=12e6)
    reset = Reset(0, active=0, async=True)
    glbl = Global(clock, reset)
    mdlsi, mdlso = Signal(bool(1)), Signal(bool(1))
    uartmdl = UARTModel()
    fifobus = FIFOBus()

    @myhdl.block
    def bench_uart():
        tbmdl = uartmdl.process(glbl, mdlsi, mdlso)
        tbdut = uartlite(glbl, fifobus, mdlso, mdlsi)
        tbclk = clock.gen()

        @always_comb
        def tblpbk():
            fifobus.read.next = not fifobus.empty
            fifobus.write.next = fifobus.read_valid
            fifobus.write_data.next = fifobus.read_data

        @instance
        def tbstim():
            yield reset.pulse(33)
            yield delay(1000)
            yield clock.posedge

            for ii in range(numbytes):
                wb = randint(0, 255)
                print("send {:02X}".format(wb))
                uartmdl.write(wb)
                timeout = ((clock.frequency/uartmdl.baudrate) * 40)
                rb = uartmdl.read()
                while rb is None and timeout > 0:
                    yield clock.posedge
                    rb = uartmdl.read()
                    timeout -= 1
                if rb is None:
                    raise TimeoutError
                print("received {:02X}".format(rb))
                assert rb == wb, "{:02X} != {:02X}".format(rb, wb)

            yield delay(100)

            raise StopSimulation

        return tbdut, tbmdl, tbclk, tblpbk, tbstim
 
    run_testbench(bench_uart, args=args)


if __name__ == '__main__':
    args = tb_args(tests=['model', 'uart'])
    if args.test == 'model' or args.test == 'all':
        test_uart_model(args)
    if args.test == 'uart' or args.test == 'all':
        test_uart(args)
