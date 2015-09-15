

from pprint import pprint

import rhea.build as build
from rhea.build.boards import get_board
from blink import blinky


def run_mojo():
    brd = get_board('mojo')
    flow = brd.get_flow(top=m_blink)
    flow.run()
    info = flow.get_utilization()
    pprint(info)


if __name__ == '__main__':
    run_mojo()