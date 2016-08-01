
from pprint import pprint

import rhea.build as build
from rhea.build.boards import get_board
from test_boards import led_port_pin_map
from blink import blinky


def run_waxwing45carrier():
    brd = get_board('waxwing45carrier')
    brd.add_port_name(**led_port_pin_map['waxwing45carrier'])
    flow = build.flow.ISE(brd=brd, top=blinky)
    flow.run()
    info = flow.get_utilization()
    pprint(info)


if __name__ == '__main__':
    run_waxwing45carrier()
