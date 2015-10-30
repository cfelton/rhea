
from pprint import pprint

import rhea.build as build
from rhea.build.boards import get_board
from blink import blinky


def run_nano():
    brd = get_board('de0cv')
    brd.add_port_name('led','ledr')
    flow = build.flow.Quartus(brd=brd, top=blinky)
    flow.run()
    info = flow.get_utilization()
    pprint(info)
    flow.program()
    

if __name__ == '__main__':
    run_nano()
