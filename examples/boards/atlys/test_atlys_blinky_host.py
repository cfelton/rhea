
from __future__ import print_function, division

from random import randint

import myhdl
from myhdl import (Signal, intbv, instance, delay, StopSimulation)

from rhea.system import Global, Clock, Reset
from rhea.models.uart import UARTModel
from rhea.utils.test import run_testbench, tb_args, tb_default_args, tb_convert
from rhea.utils import CommandPacket
from rhea.utils.command_packet import PACKET_LENGTH

from atlys_blinky_host import atlys_blinky_host


def test_ibh(args=None):
    args = tb_default_args(args)
    numbytes = 13

    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=True)
    glbl = Global(clock, reset)
    led = Signal(intbv(0)[8:])
    sw = Signal(intbv(1)[8:])
    pmod = Signal(intbv(0)[8:])
    uart_tx = Signal(bool(0))
    uart_rx = Signal(bool(0))
    uartmdl = UARTModel()

    baudrate = uartmdl.baudrate
    baudticks = int((1/baudrate) / 1e-9)

    @myhdl.block
    def bench_ibh():
        tbclk = clock.gen()
        tbmdl = uartmdl.process(glbl, uart_tx, uart_rx)
        tbdut = atlys_blinky_host(clock, reset, led, sw, pmod, 
                                  uart_tx, uart_rx)

        @instance
        def tbstim():
            yield reset.pulse(33)
            yield delay(1000)

            # test loopback
            for ii in range(5):
                wb = randint(0, 255)
                uartmdl.write(wb)
                # wait for the send (return) 
                yield delay(baudticks*(8+2) + 2*baudticks)
                rb = uartmdl.read()
                assert rb == wb
            sw.next = 0
            yield delay(100)
            
            # send a write that should enable all five LEDs
            pkt = CommandPacket(False, address=0x20, vals=[0xFF])
            for bb in pkt.rawbytes:
                uartmdl.write(bb)
            waitticks = baudticks * 10 * 28
            yield delay(waitticks) 
            timeout = 100
            yield delay(waitticks) 
            # get the response packet
            for ii in range(PACKET_LENGTH):
                rb = uartmdl.read()
                while rb is None and timeout > 0:
                    yield clock.posedge
                    rb = uartmdl.read()
                    timeout -= 1
                if rb is None:
                    raise Exception("TimeoutError")

            # the last byte should be the byte written
            assert rb == 0xFF

            yield delay(1000)
            raise StopSimulation

        return tbclk, tbmdl, tbdut, tbstim

    run_testbench(bench_ibh, args=args)
    inst = atlys_blinky_host(clock, reset, led, sw, pmod, uart_tx, uart_rx)
    tb_convert(inst)


if __name__ == '__main__':
    test_ibh(tb_args())