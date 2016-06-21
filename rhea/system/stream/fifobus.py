#
# Copyright (c) 2013-2015 Christopher L. Felton
# See the licence file in the top directory
#

import myhdl
from myhdl import Signal, intbv, always_comb
from ..clock import Clock
from .streamers import Streamers

_fb_num = 0
_fb_list = {}


def _add_bus(fb, name=''):
    """ globally keep track of all the buses added.
    """
    global _fb_num, _fb_list
    _fb_num += 1
    _fb_list[name] = fb


class FIFOBus(Streamers):
    def __init__(self, width=8):
        """ A FIFO interface
        This interface encapsulates the signals required to interface
        to a FIFO.  This object also contains the configuration
        information of a FIFO: word width and the FIFO size (depth).

        Arguments:
            size (int): The depth of the FIFO, the maximum number of
                elements a FIFO can hold.

            width (int): The width of the elements in the FIFO.
        """
        self.name = "fifobus{0}".format(_fb_num)

        # @todo: add write clock and read clock to the interface!
        self.write_clock = Clock(0)
        self.read_clock = Clock(0)

        # all the data signals are from the perspective
        # of the FIFO being interfaced to. That is , write_data
        # means write_to and read_data means read_from      
        self.clear = Signal(bool(0))                # fifo clear
        self.write = Signal(bool(0))                # write strobe to fifo
        self.write_data = Signal(intbv(0)[width:])  # fifo data in

        self.read = Signal(bool(0))                 # fifo read strobe
        self.read_data = Signal(intbv(0)[width:])   # fifo data out
        self.read_valid = Signal(bool(0))
        self.empty = Signal(bool(1))                # fifo empty
        self.full = Signal(bool(0))                 # fifo full

        # The FIFO instance will attached the FIFO count
        self.count = None

        self.width = width

        # keep track of all the FIFOBus used.
        _add_bus(self, self.name)
        
    def __str__(self):
        s = "wr: {} {:04X}, rd: {} {:04X}, empty {}, full {}".format(
            int(self.write), int(self.write_data),
            int(self.read), int(self.read_data),
            int(self.empty), int(self.full))
        return s

    def writetrans(self, data):
        """ Do a write transaction
        This generator will drive the FIFOBus signals required to
        perform a write.  If the FIFO is full an exception is thrown.
        """
        self._start_transaction(write=True, data=data)
        if not self.full:
            self.write.next = True
            self.write_data.next = data
            yield self.write_clock.posedge
            self.write.next = False
        self._end_transaction(self.write_data)

    def readtrans(self):
        """ Do a read transaction
        This generator will drive the FIFOBus signals required to
        perform a read.  If the FIFO is empty an exception is thrown
        """
        self._start_transaction(write=False)
        if not self.empty:
            self.read.next = True
            yield self.read_clock.posedge
            self.read.next = False
            while not self.valid:
                yield self.read_clock.posedge
            data = int(self.read_data)
        self._end_transaction(data)

    @myhdl.block
    def assign_read_write_paths(self, readpath, writepath):
        """
        Assign the signals from the `readpath` to the read signals
        of this interface and same for write

        Arguments:
            readpath (FIFOBus): user readpath
            writepath (FIFOBus): user writepath

                        +- write -> FIFOBus FIFO -> read
           FIFOBus User |
                        +- read <- FIFOBus FIFO <- write

        The above depicts a common scenario, when a single FIFOBus
        interface is exposed to a user but internally there are two
        FIFOs, internally a FIFOBus is used for each FIFO, the
        internal interfaces need to be mapped to the user FIFOBus
        interface.  When the user drives the write signals the
        write path write signals will mirror the external control,
        when the user reads from the FIFOBus the readpath read
        signals should mirror.

        """
        assert isinstance(readpath, FIFOBus)
        assert isinstance(writepath, FIFOBus)
        
        @always_comb
        def beh_assign():
            # write, from self perspective, self will be writing
            writepath.write.next = self.write
            writepath.write_data.next = self.write_data
            self.full.next = writepath.full

            # read, from self perspective, self will be reading
            readpath.read.next = self.read
            self.read_data.next = readpath.read_data
            self.read_valid.next = readpath.read_valid
            self.empty.next = readpath.empty

        return beh_assign
