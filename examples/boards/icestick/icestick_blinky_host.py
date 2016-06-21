
import argparse
import subprocess

import myhdl
from myhdl import Signal, intbv, always_seq, always_comb


from rhea.cores.uart import uartlite
from rhea.cores.memmap import command_bridge
from rhea.cores.misc import glbl_timer_ticks
from rhea.system import Global, Clock
from rhea.system import Barebone
from rhea.system import FIFOBus
from rhea.build.boards import get_board


@myhdl.block
def icestick_blinky_host(clock, led, pmod, uart_tx, uart_rx,
                         uart_dtr, uart_rts):
    """
    This example is similar to the other examples in this directory but
    the LEDs are controlled externally via command packets sent from a
    host via the UART on the icestick.

    (arguments == ports)
    Arguments:
      clock:
      led:
      pmod:
      uart_tx:
      uart_rx:
    """

    glbl = Global(clock, None)
    ledreg = Signal(intbv(0)[8:])

    # create the timer tick instance
    tick_inst = glbl_timer_ticks(glbl, include_seconds=True)

    # create the interfaces to the UART
    fifobus = FIFOBus(width=8)

    # create the memmap (CSR) interface
    memmap = Barebone(glbl, data_width=32, address_width=32)

    # create the UART instance.
    uart_inst = uartlite(glbl, fifobus, uart_rx, uart_tx)

    # create the packet command instance
    cmd_inst = command_bridge(glbl, fifobus, memmap)

    @always_seq(clock.posedge, reset=None)
    def beh_led_control():
        memmap.done.next = not (memmap.write or memmap.read)
        if memmap.write and memmap.mem_addr == 0x20:
            ledreg.next = memmap.write_data

    @always_comb
    def beh_led_read():
        if memmap.read and memmap.mem_addr == 0x20:
            memmap.read_data.next = ledreg
        else:
            memmap.read_data.next = 0

    # blink one of the LEDs
    tone = Signal(intbv(0)[8:])

    @always_seq(clock.posedge, reset=None)
    def beh_assign():
        if glbl.tick_sec:
            tone.next = (~tone) & 0x1
        led.next = ledreg | tone[5:] 
            
        pmod.next = 0

    # @todo: PMOD OLED memmap control

    return myhdl.instances()


def build(args):
    brd = get_board('icestick')
    flow = brd.get_flow(top=icestick_blinky_host)
    flow.run()


def program(args):
    subprocess.check_call(["iceprog", "iceriver/icestick.bin"])


def cliparse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", default=False, action='store_true')
    parser.add_argument("--test", default=False, action='store_true')
    parser.add_argument("--program", default=False, action='store_true')
    parser.add_argument("--walk", default=False, action='store_true')
    args = parser.parse_args()
    return args


def main():
    args = cliparse()
    if args.test:
        # check for basic syntax errors, use test_ice* to test
        # functionality
        icestick_blinky_host(
            clock=Clock(0, frequency=50e6),
            led=Signal(intbv(0)[8:]), 
            pmod=Signal(intbv(0)[8:]),
            uart_tx=Signal(bool(0)),
            uart_rx=Signal(bool(0)),
            uart_dtr=Signal(bool(0)),
            uart_rts=Signal(bool(0)) )
        
    if args.build:
        build(args)

    if args.program:
        program(args)

    # @todo: add walk function


if __name__ == '__main__':
    main()

