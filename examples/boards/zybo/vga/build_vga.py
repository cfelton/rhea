
from rhea.build import get_board
from zybo_vga import zybo_vga


def build():
    brd = get_board('zybo')
    flow = brd.get_flow(zybo_vga)
    flow.run()


if __name__ == '__main__':
    build()
