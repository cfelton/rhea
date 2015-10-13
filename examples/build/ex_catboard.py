
import rhea.build as build
from rhea.build.boards import get_board
from blink import blinky


def run_catboard():
    brd = get_board('catboard')
    flow = brd.get_flow(top=blinky)
    flow.run()


if __name__ == '__main__':
    run_catboard()