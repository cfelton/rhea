
from pprint import pprint

import rhea.build as build
from rhea.build.boards import get_board
from blink import blinky


def run_zybo():
    # get a board to implement the design on
    brd = get_board('zybo')
    flow = build.flow.Vivado(brd=brd, top=m_blink)
    flow.run()
    info = flow.get_utilization()
    pprint(info)
    

if __name__ == '__main__':
    run_zybo()