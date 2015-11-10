
from pprint import pprint

import rhea.build as build
from rhea.build.boards import get_board
from test_boards import led_port_pin_map
from blink import blinky


def run_xula():
    brd = get_board('xula')
    brd.add_port_name(**led_port_pin_map['xula'])
    flow = build.flow.ISE(brd=brd, top=blinky)
    flow.run()
    info = flow.get_utilization()
    pprint(info)

    # get a board to implement the design on
    brd = get_board('xula2')
    brd.add_port_name(**led_port_pin_map['xula2'])
    flow = build.flow.ISE(brd=brd, top=blinky)
    flow.run()
    info = flow.get_utilization()
    pprint(info)


if __name__ == '__main__':
    run_xula()
