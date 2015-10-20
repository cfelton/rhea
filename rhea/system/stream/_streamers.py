

class Streamers:
    def __init__(self, glbl, data_width=32):
        self.clock = glbl.clock
        self.reset = glbl.reset
        self.data_width = data_width

    def register(self, upstream):
        """ register (capture) the upstream interface to this interface
        :param upstream: upstream interface
        :return:
        """
        raise NotImplementedError

    def fifo(self):
        raise NotImplementedError
