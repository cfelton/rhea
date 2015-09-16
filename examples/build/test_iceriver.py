
import rhea.build as build
from rhea.build.boards import get_board
from blink import blinky

def test_iceriver():
    """
    This test is identical to ex_icestick but it is 
    automatically run by the py.test test runner.
    This test verifies the flow completes without
    error.
    """
    brd = get_board('icestick')
    flow = brd.get_flow(top=blinky)
    flow.run()

