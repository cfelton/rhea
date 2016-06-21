
from __future__ import print_function, division

import myhdl
from myhdl import (Signal, intbv, instance, delay, StopSimulation)

from rhea.system import Global, Clock, Reset
from rhea.models.uart import UARTModel
from rhea.utils.test import run_testbench, tb_args, tb_default_args, tb_convert
from rhea.utils import CommandPacket
from rhea.utils.command_packet import PACKET_LENGTH

from icestick_blinky_host import icestick_blinky_host


def test_ibh(args=None):
    args = tb_default_args(args)
    numbytes = 13

    clock = Clock(0, frequency=50e6)
    glbl = Global(clock, None)
    led = Signal(intbv(0)[8:])
    pmod = Signal(intbv(0)[8:])
    uart_tx = Signal(bool(0))
    uart_rx = Signal(bool(0))
    uart_dtr = Signal(bool(0))
    uart_rts = Signal(bool(0))
    uartmdl = UARTModel()

    @myhdl.block
    def bench_ibh():
        tbclk = clock.gen()
        tbmdl = uartmdl.process(glbl, uart_tx, uart_rx)
        tbdut = icestick_blinky_host(clock, led, pmod, 
                                     uart_tx, uart_rx,
                                     uart_dtr, uart_rts)

        @instance
        def tbstim():
            yield delay(1000)
            
            # send a write that should enable all five LEDs
            pkt = CommandPacket(False, address=0x20, vals=[0xFF])
            for bb in pkt.rawbytes:
                uartmdl.write(bb)
            waitticks = int((1/115200.) / 1e-9) * 10 * 28
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
                    raise TimeoutError

            # the last byte should be the byte written
            assert rb == 0xFF

            yield delay(1000)
            raise StopSimulation

        return tbclk, tbmdl, tbdut, tbstim

    run_testbench(bench_ibh, args=args)
    inst = icestick_blinky_host(
        clock, led, pmod,
        uart_tx, uart_rx, uart_dtr, uart_rts
    )
    tb_convert(inst)


if __name__ == '__main__':
    test_ibh(tb_args())