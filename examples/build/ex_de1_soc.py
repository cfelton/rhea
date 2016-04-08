
from pprint import pprint

import rhea.build as build
from rhea.build.boards import get_board
from blink import blinky


def run_de1():
    brd = get_board('de1_SoC')
    flow = build.flow.Quartus(brd=brd, top=blinky)
    flow.run(use='verilog')
    # info = flow.get_utilization()
    # pprint(info)
    

if __name__ == '__main__':
    run_de1()
