
from pprint import pprint

import rhea.build as build
from rhea.build.boards import get_board
from blink import blinky
from board_build_example import led_port_pin_map


def run_pone():
    brd = get_board('pone')
    #brd.add_port_name('toggle', 'wingC', 7, drive=6)
    brd.add_port(**led_port_pin_map['pone'])
    flow = build.flow.ISE(brd=brd, top=blinky)
    flow.run()
    info = flow.get_utilization()
    pprint(info)


if __name__ == '__main__':
    run_pone()