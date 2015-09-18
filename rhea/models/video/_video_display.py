
import os
from array import array
from copy import deepcopy

from PIL import Image


class VideoDisplay(object):
    def __init__(self, 
                 resolution=(640,480,), 
                 refresh_rate = 60,
                 line_rate = 31250,
                 color_depth=(10, 10, 10,)
             ):
        """
        """
        self.resolution = res = resolution
        self.num_hpxl, self.num_vpxl = self.resolution
        self.name = 'unknown'
        self.update_cnt = 0
        self._col, self._row = 0, 0

        if max(color_depth) <= 8:
            arraytype = 'B'
        elif max(color_depth) <= 16:
            arraytype = 'H'
        elif max(color_depth) <= 32:
            arraytype = 'L'

        # create a container to emulate the video display
        # in the process of updating image
        #self.uvmem = [array(arraytype, [0 for _ in range(res[0])])
        #              for _ in range(res[1])]
        self._uvmem = [[None for _ in range(res[0])]
                        for _ in range(res[1])]
        # static image
        #self.vvmem = [array(arraytype, [0 for _ in range(res[0])])
        #              for _ in range(res[1])]
        self._vvmem = [[None for _ in range(res[0])]
                        for _ in range(res[1])]

    def reset_cursor(self):
        self._col, self._row = 0, 0

    def update_next_pixel(self, val):
        col, row = self._col, self._row
        assert col < self.num_hpxl
        assert row < self.num_vpxl

        self._uvmem[row][col] = int(val)

        col += 1
        if col == self.num_hpxl:
            col = 0
            row += 1
        if row == self.num_vpxl:
            row = 0

        if col == 0 and row == 0:
            self.update_cnt += 1

        self._col, self._row = col, row

    def set_pixel(self, col, row, val):
        """
        :param col:
        :param row:
        :return:
        """
        assert col < self.num_hpxl
        assert row < self.num_vpxl
        self._uvmem[row][col] = int(val)

        # assume a frame is updated sequentially, once the end
        # is reached a frame update is incremented

    def create_save_image(self, framen, frame):
        """ 
        :param framen: frame number
        :param frame: 2D frame container (list, array)
        """
        im = Image.new('RGB', self.resolution)
        for rr, row in enumerate(frame):
            for cc, rgb in enumerate(row):
                im.putpixel((cc, rr), tuple(rgb))
                
        if not os.path.isdir("output"):
            os.makedirs("output")
        imgpath = os.path.join("output/", "{}_frame_{}.png".format(
            self.name, framen))
        im.save(imgpath)

    def process(self, glbl, vga):
        """ emulate the behavior of the display """
        raise NotImplemented

