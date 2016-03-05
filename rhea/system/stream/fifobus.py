#
# Copyright (c) 2013-2015 Christopher L. Felton
#

from myhdl import Signal, intbv


_fb_num = 0
_fb_list = {}


def _add_bus(fb, name=''):
    """ globally keep track of all the buses added.
    """
    global _fb_num, _fb_list
    _fb_num += 1
    _fb_list[name] = fb


class FIFOBus(object):
    def __init__(self, size=16, width=8):
        """
        """
        self.name = "fifobus{0}".format(_fb_num)

        # @todo: add write clock and read clock to the interface!
        # @todo: use longer names read, read_valid, read_data,
        # @todo: write, write_data, etc.!

        # all the data signals are from the perspective
        # of the FIFO being interfaced to.        
        self.clear = Signal(bool(0))           # fifo clear
        #self.wclk = None                      # write side clock
        self.write = Signal(bool(0))              # write strobe to fifo
        self.write_data = Signal(intbv(0)[width:])  # fifo data in

        #self.rclk = None                      # read side clock
        self.read = Signal(bool(0))              # fifo read strobe
        self.read_data = Signal(intbv(0)[width:])  # fifo data out
        self.read_valid = Signal(bool(0))
        self.empty = Signal(bool(1))           # fifo empty
        self.full = Signal(bool(0))            # fifo full
        self.count = Signal(intbv(0, min=0, max=size+1))

        self.width = width
        self.size = size

        _add_bus(self, self.name)
        
    def __str__(self):
        s = "wr: {} {:04X}, rd: {} {:04X}, empty {}, full {}".format(
            int(self.write), int(self.write_data), int(self.read), int(self.read_data),
            int(self.empty), int(self.full))
        return s

    def writetrans(self, data):
        pass

    def readtrans(self):
        pass

    # @todo: get the separate buses
    # def get_upstream()    
    #     """ write bus, into the FIFO """
    #
    # def get_downstream()
    #     """ 