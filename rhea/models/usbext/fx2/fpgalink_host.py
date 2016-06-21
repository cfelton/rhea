#
# Copyright (c) 2011-2013 Christopher L. Felton
#

from __future__ import print_function, absolute_import


import time
from myhdl import now
from .fx2_model import Fx2Model

    
class FpgaLinkHost(Fx2Model):
    """
    """
    
    def __init__(self, verbose=False, trace=False):
        self.commOut = self.EP2
        self.commIn = self.EP6
        # @todo: use super
        Fx2Model.__init__(self, fifo_size=1024, config=1,
                          verbose=verbose, trace=trace)

    def isrunning(self):
        """ Is the FPGA running        
        """
        # @todo : complete
        return True

    def _wait_empty(self, ep, timeout=100):
        ok = False
        to = timeout * 1e6
        te = now() + to
        for ii in range(timeout):
            if self.isempty(ep):
                ok = True
                break
            time.sleep(1)
            if now() > te:
                break
        return ok

    def _wait_data(self, ep, num=1, timeout=100):
        ok = False
        to = timeout * 1e6
        te = now() + to
        for ii in range(timeout):
            if self.isdata(ep, num=num):
                ok = True
                break
            time.sleep(1)
            if now() > te:
                break
        return ok
    
    def read_channel(self, chan, count=1, timeout=100):
        """ Read one or more values from the specific channel
        Read /count/ bytes from the FPGA channel /chan/ to the data /array/,
        with the supplied /timeout/ in milleseconds.

          chan : The FPA channel to read
          count : The number of bytes to read
          timeout : The time to wait (in milliseconds) for the read to
            complete before giving up.

          This is a generator, it needs to be called:
             yield fl.ReadChannel(...)
        """
        wbuf = [0 for ii in range(5)]
        # 0 : chan,
        # 1,2,3,4 (MSB in 4, LSB in 1)
        wbuf[0] = 0x80 | chan
        wbuf[1] = (count >> 24) & 0xFF
        wbuf[2] = (count >> 16) & 0xFF
        wbuf[3] = (count >> 8) & 0xFF
        wbuf[4] = (count >> 0) & 0xFF
        self.trace_print(str(wbuf))
        self.write(wbuf, self.commOut)
        self._wait_empty(self.commOut, timeout=timeout)
        self._wait_data(self.commIn, num=count, timeout=timeout)
        
        # write the command
        # read the number of bytes asked for
        return self.read(self.commIn, num=count)
    
    def write_channel(self, chan, values, timeout=100):
        """ Write one or more bytes to the specified channel
        Write /count/ bytes from the /data/ list/array to the FPGA
        channel /chan/, with the given /timeout/ in milleseconds.  In
        the event of a timeout.
        """
        assert isinstance(values, (list, tuple))
        dlen = len(values)
        wbuf = [0 for _ in range(dlen+5)]
        wbuf[0] = chan & 0x7F
        wbuf[1] = (dlen >> 24) & 0xFF
        wbuf[2] = (dlen >> 16) & 0xFF
        wbuf[3] = (dlen >> 8) & 0xFF
        wbuf[4] = (dlen >> 0) & 0xFF
        wbuf[5:] = values
        print(wbuf)
        self.write(wbuf, self.commOut)
        self._wait_empty(self.commOut)

    def append_write_channel_command(chan, count, data):
        """ Append a write command to the end of the write buffer
        """
        raise NotImplementedError("Not Implemented")

    def play_write_buffer(chan, count, data):
        """ Play the write buffer into the FPGALink device immediately
        """
        raise NotImplementedError("Not Implemented")

    def clean_write_buffer(self):
        """ Clean the write buffer (if any)
        """
        raise NotImplementedError("Not Implemented")


def test_simple():
    # The Host interface can start the sim engine
    print('1')
    # get the host interface
    fl = FpgaLinkHost(verbose=True, trace=True)
    print('2')
    fl.setup(fl.get_bus())  # simulation setup
    print('3')
    fl.start()                # start simulation
    print('4')

    print('   reset')
    fl.reset()
    print('   write channel')
    fl.write_channel(1, [1, 2, 3, 4])
    # print('   read channel')
    # bb = fl.ReadChannel(1, 4)

    # stop the simulation
    fl.stop()


if __name__ == '__main__':
    test_simple()
