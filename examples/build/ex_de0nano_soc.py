
from pprint import pprint

import rhea.build as build
from rhea.build.boards import get_board
from blink import blinky


def run_nano():
    brd = get_board('de0nano_soc')
    flow = build.flo.Quartus(brd=brd, top=m_blink)
    flow.run(use='vhdl')
    info = flow.get_utilization()
    pprint(info)
    

if __name__ == '__main__':
    run_nano()