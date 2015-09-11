
from pprint import pprint

import rhea.build as build
from rhea.build.boards import get_board
from blink import m_blink


def run_pone():
    brd = get_board('pone')
    brd.add_port_name('toggle', 'wingC', 7, drive=6)
    flow = build.flow.ISE(brd=brd, top=m_blink)
    flow.run()
    info = flow.get_utilization()
    pprint(info)


if __name__ == '__main__':
    run_pone()