
import argparse
import subprocess

import myhdl
from myhdl import Signal, intbv, always_seq, always_comb

from rhea.cores.uart import uartlite
from rhea.cores.memmap import command_bridge
from rhea.cores.misc import glbl_timer_ticks
from rhea import Global, Clock
from rhea.system import Barebone
from rhea.system import FIFOBus
from rhea.build.boards import get_board


@myhdl.block
def catboard_blinky_host(clock, led, uart_tx, uart_rx):
    """
    The LEDs are controlled from the RPi over the UART
    to the FPGA.
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
    uart_inst = uartlite(
        glbl, fifobus, serial_in=uart_rx, serial_out=uart_tx,
        fifosize=4
    )

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
            
    return (tick_inst, uart_inst, cmd_inst,
            beh_led_control, beh_led_read, beh_assign)


def build(args):
    brd = get_board('catboard')
    brd.add_port_name('uart_rx', 'bcm14_txd')                           
    brd.add_port_name('uart_tx', 'bcm15_rxd')
    flow = brd.get_flow(top=catboard_blinky_host)
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


def test_instance():    
    # check for basic syntax errors, use test_ice* to test
    # functionality
    catboard_blinky_host(
        clock=Clock(0, frequency=50e6),
        led=Signal(intbv(0)[8:]), 
        uart_tx=Signal(bool(0)),
        uart_rx=Signal(bool(0)), )

    
def main():
    args = cliparse()
    if args.test:
        test_instance()
        
    if args.build:
        build(args)

    if args.program:
        program(args)

    # @todo: add walk function


if __name__ == '__main__':
    main()

