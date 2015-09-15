
import rhea.build as build
from rhea.build.boards import get_board
from blink import m_blink


def run_icestick():
    brd = get_board('icestick')
    brd.add_port('toggle', pins=(99,))
    flow = brd.get_flow(top=m_blink)
    flow.run()


if __name__ == '__main__':
    run_icestick()
