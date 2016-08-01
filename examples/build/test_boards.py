
"""
use the yosys toolflow to dummy test all the board 
definitions.  Each board has a mapping to the designs
ports ...
"""

import os

import rhea.build as build
from rhea.build.boards import get_board
from rhea.build.boards import get_all_board_names
from blink import blinky

# The following maps pins to use for test output for boards without an led port.
led_port_pin_map = {
    'xula': dict(name='led', port='chan', slc=[slice(0,2),slice(3,2)]),
    'xula2': dict(name='led', port='chan', slc=slice(0,4)),
    'xula2_stickit_mb': dict(name='led', port='chan', slc=slice(0,4)),
    'pone': dict(name='led', port='winga', slc=slice(0,4)),
    'ppro': dict(name='led', port='winga', slc=slice(0,4)),
    'waxwing45': dict(name='led', port='p1', slc=slice(0,4)),
    'waxwing45carrier': dict(name='led', port='p7', slc=slice(0,4)),
    'de0cv': dict(name='led', port='ledr', slc=slice(0,4))
}



def test_boards():
    for bn in get_all_board_names():
        brd = get_board(bn)

        # map led port for boards without explicit led pins 
        if bn in led_port_pin_map:
            brd.add_port_name(**led_port_pin_map[bn])

        flow = build.flow.Yosys(brd=brd, top=blinky)
        flow.path = os.path.join('output', flow.path)
        flow.run()


if __name__ == '__main__':
    test_boards()
