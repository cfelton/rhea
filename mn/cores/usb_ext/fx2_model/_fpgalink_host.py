#
# Copyright (c) 2011-2013 Christopher L. Felton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from array import array
import struct
import time

from myhdl import now

from _fx2_model import Fx2Model

    
class FpgaLinkHost(Fx2Model):
    """
    """
    
    def __init__(self, Verbose=False, Trace=False):
        self.commOut = self.EP2
        self.commIn = self.EP6
        Fx2Model.__init__(self, FifoSize=1024, Config=1,
                          Verbose=Verbose, Trace=Trace)

    def IsRunning(self):
        """ Is the FPGA running        
        """
        # @todo : complete
        return True

    def _wait_empty(self, ep, timeout=100):
        ok = False
        to = timeout * 1e6
        te = now() + to
        for ii in range(timeout):
            if self.IsEmpty(ep):
                ok = True
                break
            time.sleep(1)
            if now() > te:
                break
        return ok

    def _wait_data(self, ep, Num=1, timeout=100):
        ok = False
        to = timeout * 1e6
        te = now() + to
        for ii in range(timeout):
            if self.IsData(ep, Num=Num):
                ok = True
                break
            time.sleep(1)
            if now() > te:
                break
        return ok
    
    def ReadChannel(self, chan, count=1, timeout=100):
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
        wbuf[0]  = 0x80 | chan
        wbuf[1] = (count >> 24) & 0xFF
        wbuf[2] = (count >> 16) & 0xFF
        wbuf[3] = (count >> 8) & 0xFF
        wbuf[4] = (count >> 0) & 0xFF
        self.TracePrint(str(wbuf))
        self.Write(wbuf, self.commOut)
        self._wait_empty(self.commOut, timeout=timeout)
        self._wait_data(self.commIn, Num=count, timeout=timeout)
        
        # write the command
        # read the number of bytes asked for
        return self.Read(self.commIn, Num=count)
    
    def WriteChannel(self, chan, values, timeout=100):
        """ Write one or more bytes to the specified channel
        Write /count/ bytes from the /data/ list/array to the FPGA
        channel /chan/, with the given /timeout/ in milleseconds.  In
        the event of a timeout.
        """
        assert isinstance(values, (list, tuple))
        dlen = len(values)
        wbuf = [0 for ii in range(dlen+5)]
        wbuf[0] = chan & 0x7F
        wbuf[1] = (dlen >> 24) & 0xFF
        wbuf[2] = (dlen >> 16) & 0xFF
        wbuf[3] = (dlen >> 8) & 0xFF
        wbuf[4] = (dlen >> 0) & 0xFF
        wbuf[5:] = values
        print(wbuf)
        self.Write(wbuf, self.commOut)
        self._wait_empty(self.commOut)

    def AppendWriteChannelCommand(chan, count, data):
        """ Append a write command to the end of the write buffer
        """
        raise NotImplementedError, "Not Implemented"

    def PlayWriteBuffer(chan, count, data):
        """ Play the write buffer into the FPGALink device immediately
        """
        raise NotImplementedError, "Not Implemented"

    def CleanWriteBuffer(self):
        """ Clean the write buffer (if any)
        """


def test_simple():
    # The Host interface can start the sim engine
    print('1')
    # get the host interface
    fl = FpgaLinkHost(Verbose=True, Trace=True)   
    print('2')
    fl.setup(fl.GetFx2Bus())  # simulation setup
    print('3')
    fl.start()                # start simulation
    print('4')

    print('   reset')
    fl.Reset()
    print('   write channel')
    fl.WriteChannel(1, [1,2,3,4])
    #print('   read channel')
    #bb = fl.ReadChannel(1, 4)

    # stop the simulation
    fl.stop()
    
if __name__ == '__main__':
    test_simple()
