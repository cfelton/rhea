

from pprint import pprint

import rhea.build as build
from rhea.build.boards import get_board
from blink import m_blink

def run_mojo():
    brd = get_board('mojo')
    brd.add_clock('clock', pins=(56,), frequency=50)
    brd.add_port('toggle', pins=(134,))
    brd.add_reset('reset', active=0, async=True, pins=('E6',))
    flow = brd.get_flow(top=m_blink)
    flow.run()
    info = flow.get_utilization()
    pprint(info)


if __name__ == '__main__':
    run_mojo()