
import rhea.build as build
from rhea.build.boards import get_board
from blink import blinky


def run_icestick():
    brd = get_board('icestick')
    flow = brd.get_flow(top=m_blink)
    flow.run()


if __name__ == '__main__':
    run_icestick()
