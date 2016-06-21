
import argparse 
import subprocess

import myhdl
from myhdl import (Signal, intbv, always_seq, always_comb, 
                   concat, ConcatSignal,)

from rhea.cores.uart import uartlite
from rhea.cores.memmap import command_bridge
from rhea.cores.misc import glbl_timer_ticks
from rhea import Global, Clock, Reset
from rhea.system import Barebone, FIFOBus
from rhea.build.boards import get_board


@myhdl.block
def atlys_blinky_host(clock, reset, led, sw, pmod,
                      uart_tx, uart_rx):
    """
    This example is similar to the other examples in this directory but
    the LEDs are controlled externally via command packets sent from a
    host via the UART on the icestick.

    """
    glbl = Global(clock, reset)
    ledreg = Signal(intbv(0)[8:])
    
    # create the timer tick instance
    tick_inst = glbl_timer_ticks(glbl, include_seconds=True)

    # create the interfaces to the UART
    fifobus = FIFOBus(width=8)

    # create the memmap (CSR) interface
    memmap = Barebone(glbl, data_width=32, address_width=32)

    # create the UART instance, cmd_tx is an internal loopback
    # for testing (see below)
    cmd_tx = Signal(bool(0))
    uart_inst = uartlite(glbl, fifobus, uart_rx, cmd_tx)

    # create the packet command instance
    cmd_inst = command_bridge(glbl, fifobus, memmap)

    @always_seq(clock.posedge, reset=reset)
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
    status = [Signal(bool(0)) for _ in range(8)]
    statusbv = ConcatSignal(*reversed(status))

    @always_seq(clock.posedge, reset=reset)
    def beh_assign():
        # status / debug signals
        if glbl.tick_sec:
              status[0].next = not status[0]
        status[1].next = memmap.mem_addr == 0x20
        status[2].next = uart_rx
        status[3].next = uart_tx
        led.next = ledreg | statusbv | sw
            
        pmod.next = 0

        if sw[0]:
            uart_tx.next = uart_rx
        else:
            uart_tx.next = cmd_tx

    # @todo: PMOD OLED memmap control

    return (tick_inst, uart_inst, cmd_inst,
            beh_led_control, beh_led_read, beh_assign)


def build(args):
    brd = get_board('atlys')
    flow = brd.get_flow(top=atlys_blinky_host)
    flow.run()


def program(args):
    pass


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
        atlys_blinky_host(
            Clock(0, frequency=50e6), Signal(intbv(0)[8:]), 
            Signal(intbv(0)[8:]), Signal(bool(0)), Signal(bool(0)) )
    if args.build:
        build(args)


if __name__ == '__main__':
    main()

