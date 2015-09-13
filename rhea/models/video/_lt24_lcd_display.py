

from myhdl import Signal, intbv, enum
from PIL import Image


class LT24LCDDisplay(object):
    def __init__(self, frequency, refresh_rate=60, line_rate=31250):
        resolution = res = (240, 320)
        color_depth = (5, 6, 5)

        self.uvmem = [[None for _ in range(res[0])]
                      for _ in range(res[1])]

        self.vvmem = [[None for _ in range(res[0])]
                      for _ in range(res[1])]

        def process(self, glbl, lcd):
            """
            """

            self.states = enum('init')
            