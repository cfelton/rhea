
"""
use the yosys toolflow to dummy test all the board 
definitions.  Each board has a mapping to the designs
ports ...
"""

import pytest

import rhea.build as build
from rhea.build.boards import get_board
from rhea.build.boards import get_all_board_names
from board_build_example import led_port_pin_map
from blink import blinky


def test_boards():
    for bn in get_all_board_names():
        brd = get_board(bn)
        
        # map led port for boards without explicit led pins 
        if bn in led_port_pin_map:
            brd.add_port(**led_port_pin_map[bn])

        flow = build.flow.Yosys(brd=brd, top=blinky)
        flow.run()


if __name__ == '__main__':
    test_boards()