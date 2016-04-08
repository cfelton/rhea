

class Streamers(object):
    def __init__(self, glbl, data_width=32):
        """ Base class for the streaming interfaces
        """
        # @todo: need upstream and downstream clocks and resets
        self.clock = glbl.clock
        self.reset = glbl.reset
        self.data_width = data_width

        # transaction variables
        self._write = False    # write command in progress
        self._read = False     # read command in progress
        self._write_data = -1  # holds the last data written
        self._read_data = -1   # holds the last read data

    # ~~~~ transaction methods ~~~~

    @property
    def is_write(self):
        return self._write

    @property
    def is_read(self):
        return self._read

    def get_write_data(self):
        return self._write_data

    def get_read_data(self):
        return self._read_data

    def _start_transaction(self, write=False, data=None):
        self._write = write
        self._read = not write
        if write:
            self._write_data = data
        else:
            self._read_data = data

    def _end_transaction(self, data=None):
        if self._read and data is None:
            self.read_data = int(data)
        self._write = False
        self._read = False

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # public transactor API
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def writetrans(self, data):
        """ Write transaction """
        raise NotImplementedError

    def readtrans(self):
        """ Read transaction """
        raise NotImplementedError

    # ~~~~ common blocks associated with streaming buses ~~~~

    def register(self, upstream):
        """ register (capture) the upstream interface to this interface
        :param upstream: upstream interface
        :return:
        """
        raise NotImplementedError

    def fifo(self):
        raise NotImplementedError
