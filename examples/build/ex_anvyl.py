

from pprint import pprint

import rhea.build as build
from rhea.build.boards import get_board
from blink import m_blink

def run_anvyl():
    brd = get_board('anvyl')
    brd.add_clock('clock', pins=('D11',), frequency=100e6)
    brd.add_port('toggle', pins=('W3',))
    brd.add_reset('reset', active=0, async=True, pins=('E6',))
    flow = brd.get_flow(top=m_blink)
    flow.run()
    info = flow.get_utilization()
    pprint(info)


if __name__ == '__main__':
    run_anvyl()