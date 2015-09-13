
"""
use the yosys toolflow to dummy test all the board 
definitions.  Each board has a mapping to the designs
ports, the board_table contains the mappings
"""

import pytest

import rhea.build as build
from rhea.build.boards import get_board
from rhea.build.boards import get_all_board_names
from blink import m_blink

brd_table = {
    'xula': [('clock', 43), ('reset', 37), ('toggle', 36)],
    'xula2': [('clock', 'A9'), ('reset', 'R15'), ('toggle', 'R7')],
    # @todo: add correct pins for the following
    'pone': [('clock', 1), ('reset', 1), ('toggle', 1)],
    'anvyl': [('clock', 1), ('reset', 1), ('toggle', 1)],
    'mojo': [('clock', 1), ('reset', 1), ('toggle', 1)],
    'de0nano': [('clock', 1), ('reset', 1), ('toggle', 1)],    
    'de0nano_soc': [('clock', 1), ('reset', 1), ('toggle', 1)],
}


def test_boards():
    for brd, pmap in brd_table.items():
        brd = get_board(brd)
        for port, pn in pmap:
            if 'clock' == port:
                brd.add_clock(port, frequency=100e6, pins=(pn,))
            elif 'reset' == port:
                brd.add_reset(port, active=0, async=True, pins=(pn,))
            else:
                brd.add_port(port, pins=(pn,))

        flow = build.flow.Yosys(brd=brd, top=m_blink)
        flow.run()

        # @todo: get the board flow, check if it is installed?
        # @todo: if so run the flow
        # flow = brd.get_flow()
        # if flow.check_installed():
        #     flow.run()


if __name__ == '__main__':
    test_boards()