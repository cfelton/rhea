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

from _fx2_model import Fx2Model

class UsbpHost(Fx2Model):
    """
    """

    def __init__(self):
        Fx2Model.__init__(self, FifoSize=512, Config=0)

    def WriteAddress(self, addr, data):
        wbuf = [0xDE, 0xCA, 0x01, 0x00, 0x00, 0x01, 0xFB, 0xAD, 0x00]
        rbuf = [0 for ii in range(9)]
        
        wbuf[3]  = (addr >> 8) & 0xFF
        wbuf[4]  = addr & 0xFF
        wbuf[5]  = 1
        wbuf[8]  = data

        self.Write(wbuf, self.EP2)
        while not self.IsEmpty(self.EP2):
            yield delay(2*self.IFCLK_TICK)
        while not self.IsData(self.EP6, 9):
            yield delay(2*self.IFCLK_TICK)
            
        for i in range(9):
            rbuf[i] = self.Read(self.EP6)        

        # The last byte is the previous value of the register, it will not match
        for i in range(8):
            if wbuf[i] != rbuf[i]:
                print "wbuf ", wbuf
                print 'rbuf ', rbuf
            assert wbuf[i] == rbuf[i], "Write Address Failed wbuf[%d](%02x) != rbuf[%d](%02x)" % (i, wbuf[i], i, rbuf[i])
            

    def ReadAddress(self, addr, data, w=1):

        plen = 8+w
        wbuf = [0]*plen
        rbuf = [0]*plen

        wbuf[0]  = 0xDE
        wbuf[1]  = 0xCA
        wbuf[2]  = 0x02
        wbuf[3]  = (addr >> 8) & 0xFF
        wbuf[4]  = addr & 0xFF
        wbuf[5]  = w
        wbuf[6]  = 0xFB
        wbuf[7]  = 0xAD

        self.Write(wbuf, self.EP2)
        while not self.IsEmpty(self.EP2):
            yield delay(2*self.IFCLK_TICK)
            
        while not self.IsData(self.EP6, plen):
            yield delay(2*self.IFCLK_TICK)

        for i in range(plen):
            rbuf[i] = self.Read(self.EP6)

        for i in range(8):
            if wbuf[i] != rbuf[i]:
                print '[%d] wbuf %s' % (i, wbuf)
                print '[%d] rbuf %s' % (i, rbuf)
                raise AssertionError, "Read Address Failed wbuf[%d](%02x) != rbuf[%d](%02x)" % (i, wbuf[i], i, rbuf[i])

        if w == 1:
            data[0] = rbuf[8]
        elif w == 2:
            data[0] = (rbuf[8] << 8) | rbuf[9]
        elif w == 3:
            data[0] = (rbuf[8] << 16) | (rbuf[9] << 8) | rbuf[10]
        if w == 4:
            data[0] = (rbuf[9] << 24) | (rbuf[9] << 16) | (rbuf[10] << 8) | rbuf[11]            
            print rbuf[8], rbuf[9], rbuf[10], rbuf[11]
    

    #---------------------------------------------------------------------------
    def HostReadRequest(self, DataInRdy48, BufferSize=4096):
        """ Emulated Host request

        In an actual system the host will request N bytes from the USB system.
        This is a separate generate that will do a ReadBlock from.  If a block is
        available it will copy it to the HostQueue.

        For simulation 
        """
        
        @always(DataInRdy48.posedge)
        def tm_host_request():
            pass

        return intances()
