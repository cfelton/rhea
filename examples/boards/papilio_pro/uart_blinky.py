import argparse
import subprocess

import myhdl
from myhdl import Signal, intbv, always_seq, always_comb
from myhdl import always, ResetSignal

from rhea.cores.uart import uartlite
from rhea.cores.memmap import command_bridge
from rhea.cores.misc import glbl_timer_ticks
from rhea import Global, Clock, Reset
from rhea.system import Barebone
from rhea.system import FIFOBus
from rhea.build.boards import get_board


@myhdl.block
def uart_blinky(clock, led, uart_tx, uart_rx):
    """
    Uses UART module to control LEDs while blinking the first LED.
    LEDs used are pins 0-7 on wing A.
    Expected behavior after upload is that LED[0] blinks on/off.
    When sending 
    0xDE 0x02 0x00 0x00 0x00 0x20 0x04 0xCA 0x00 0x00 0x00 0xFF
    via serial connection, all LEDs should turn on.
    For details about the message format see
    /rhea/cores/memmap/command_bridge.py
    """
    reset = ResetSignal(0, active=0, isasync=True)

    glbl = Global(clock, reset)
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
    tone = Signal(intbv(0)[8:])
    reset_dly_cnt = Signal(intbv(0)[5:])

    @always_seq(clock.posedge, reset=None)
    def beh_assign():
        if glbl.tick_sec:
            tone.next = (~tone) & 0x1
        led.next = ledreg | tone[5:] 
    
    @always(clock.posedge)
    def reset_tst():
        '''
        For the first 4 clocks the reset is forced to lo
        for clock 6 to 31 the reset is set hi
        then the reset is lo
        '''
        if (reset_dly_cnt < 31):
			reset_dly_cnt.next = reset_dly_cnt + 1
			if (reset_dly_cnt <= 4):
				reset.next = 1
			if (reset_dly_cnt >= 5):
				reset.next = 0
        else:
            reset.next = 1
            
    return (tick_inst, cmd_inst, uart_inst,
            beh_led_control, beh_led_read, beh_assign, reset_tst)


def build(args):
    brd = get_board('ppro')
    brd.add_port_name('uart_tx', 'tx')                           
    brd.add_port_name('uart_rx', 'rx')
    brd.add_port_name('led', 'winga', slc=slice(0,8))
    flow = brd.get_flow(top=uart_blinky)
    flow.run()


def program(args):
    subprocess.check_call(["papilio-prog", "-f", "./xilinx/pprov.bit"])


def cliparse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", default=False, action='store_true')
    parser.add_argument("--test", default=False, action='store_true')
    parser.add_argument("--program", default=False, action='store_true')
    args = parser.parse_args()
    return args


def test_instance():    
    # check for basic syntax errors, use test_ice* to test
    # functionality
    uart_blinky(
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

if __name__ == '__main__':
    main()

