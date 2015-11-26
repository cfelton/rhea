
from myhdl import (Signal, modbv, always, always_comb, instances)

from rhea.cores.uart import uartlite
from rhea.cores.memmap import memmap_command_bridge
from rhea.cores.misc import glbl_timer_ticks
from rhea.system import Global
from rhea.system import Barebone
from rhea.system import FIFOBus


def icestick_blinky_host(clock, led, pmod, uart_tx, uart_rx):
    """
    This example is similar to the other examples in this directory but
    the LEDs are controlled externally via command packets sent from a
    host via the UART on the icestick.

    Ports:
      clock:
      led:
      pmod:
      uart_tx:
      uart_rx:
    """

    glbl = Global(clock, None)
    # create the timer tick instance
    tick_inst = glbl_timer_ticks(glbl, include_seconds=True)

    # create the interfaces to the UART
    fbustx = FIFOBus(width=8, size=20)
    fbusrx = FIFOBus(width=8, size=20)

    # create the memmap (CSR) interface
    memmap = Barebone(data_width=32, address_width=28)

    # create the UART instance
    uart_inst = uartlite(glbl, fbustx, fbusrx, uart_tx, uart_rx)

    # create the packet command instance
    cmd_inst = memmap_command_bridge(glbl, fbusrx, fbustx, memmap)

    # @todo: LED memmap control

    # @todo: PMOD OLED memmap control

    return tick_inst, uart_inst, cmd_inst


def build(args):
    pass


def program(args):
    pass


def write_address(address, value):
    pass


def read_address(address):
    pass


def cliparse():
    pass


def main():
    pass


if __name__ == '__main__':
    main()

