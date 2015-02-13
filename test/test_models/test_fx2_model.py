
from random import randint
import shutil

from myhdl import *

from mn.models.usbext import Fx2Model
from mn.models.usbext.fx2._fx2_model import SlaveFifo

# The Fx2Model has two config modes.  The actual FX2 controller has
# numerous programmable modes.  The "configs" emulate configurations
# for different FX2 firmware (fpgalink, usrp, usbp, ...).  

def test_config1_host_write():

    fm = Fx2Model(Config=1, Verbose=True, Trace=False)
    fb = fm.GetFx2Bus()
    tb_dut = traceSignals(SlaveFifo,fm,fb)

    def _write(fm, num=1):
        pass
    
    def _read(fb, num=1):
        yield fb.IFCLK.posedge
        fb.SLRD.next = False
        fb.SLOE.next = False
        fb.ADDR.next = 0
        for ii in range(num):
            yield fb.IFCLK.posedge
        fb.SLRD.next = True
        fb.SLOE.next = True
        fb.ADDR.next = 0
        yield delay(3*fm.IFCLK_TICK)

    @instance
    def tb_stimulus():
        fb.ADDR.next = 0
        yield delay(3*fm.IFCLK_TICK)
        fb.RST.next = False
        yield delay(13*fm.IFCLK_TICK)
        fb.RST.next = True
        yield delay(13*fm.IFCLK_TICK)
        
        # FLAGC is gotdata
        # FLAGB is gotroom
        # In the config1 mode FLAGC is gotdata and FLAGB is gotroom.
        # At start FLAGB == True and FLAGC == False.  After a write
        # FLAGC == True.
        # Config1 onl
        
        assert fb.FLAGB == True
        assert fb.FLAGC == False
        
        fm.Write([0xCE], fm.EP2)
        yield delay(3*fm.IFCLK_TICK)
        assert fb.FLAGB == True  # still should have room
        assert fb.FLAGC == True  # should have data now
        assert fb.FDO == 0xCE
        assert not fm.IsEmpty(fm.EP2)

        # read out the data written, 1 byte
        yield _read(fb,1)
        assert fb.FLAGB == True  # still should have room
        assert fb.FLAGC == False # no data now
        assert fm.IsEmpty(fm.EP2)
        yield delay(13*fm.IFCLK_TICK)
        
        # Write a burst of data and read the burst of data
        data = range(33)
        data[0] = 0xFE
        fm.Write(data, fm.EP2)
        yield delay(3*fm.IFCLK_TICK)
        assert fb.FLAGB == True  # still should have room
        assert fb.FLAGC == True  # should have data now
        assert fb.FDO == 0xFE
        assert not fm.IsEmpty(fm.EP2)

        yield _read(fb,33)
        assert fb.FLAGB == True  # still should have room
        assert fb.FLAGC == False # now data now
        assert fm.IsEmpty(fm.EP2)

        # read one more
        yield _read(fb,1)        

        # fill the FIFO
        data = [randint(0,0xFF) for ii in range(512)]
        fm.Write(data, fm.EP2)
        yield delay(3*fm.IFCLK_TICK)
        assert fb.FLAGB == True  # still should have room
        assert fb.FLAGC == True  # should have data now
        assert fb.FDO == data[0]
        assert not fm.IsEmpty(fm.EP2)

        yield _read(fb, 512)
        assert fb.FLAGB == True  # still should have room
        assert fb.FLAGC == False # now data now
        assert fm.IsEmpty(fm.EP2)

        # The model should handle flow, control it will take
        # how much ever data? (this emulates how the host USB
        # software stack would work).
        data = [randint(0,0xFF) for ii in range(517)]
        fm.Write(data, fm.EP2)
        yield delay(3*fm.IFCLK_TICK)
        assert fb.FLAGB == True  # still should have room
        assert fb.FLAGC == True  # should have data now
        assert fb.FDO == data[0]
        assert not fm.IsEmpty(fm.EP2)

        yield _read(fb, 512)
        assert fb.FLAGB == True  # still should have room
        assert fb.FLAGC == True  # now data now

        yield _read(fb, 7)
        assert fb.FLAGB == True  # still should have room
        assert fb.FLAGC == False # now data now
        assert fm.IsEmpty(fm.EP2)

        

        raise StopSimulation
    
    Simulation((tb_dut, tb_stimulus)).run()
    shutil.move('SlaveFifo.vcd', 'v_test_config1_host_write.vcd')

def test_config1_host_read():

    fm = Fx2Model(Config=1, Verbose=True, Trace=False)
    fb = fm.GetFx2Bus()
    tb_dut = traceSignals(SlaveFifo,fm,fb)

    def _write(fb, data):
        yield fb.IFCLK.posedge
        for dd in data:
            fb.FDI.next = dd
            fb.SLWR.next = False
            yield fb.IFCLK.posedge
        fb.SLWR.next = True
        yield delay(3*fm.IFCLK_TICK)
    
    def _read(fm, num=1):
        pass

    @instance
    def tb_stimulus():
        fb.ADDR.next = 0
        yield delay(3*fm.IFCLK_TICK)
        fb.RST.next = False
        yield delay(13*fm.IFCLK_TICK)
        fb.RST.next = True
        yield delay(13*fm.IFCLK_TICK)
        fb.ADDR.next = 2
        
        # FLAGC is gotdata
        # FLAGB is gotroom
        # In the config1 mode FLAGC is gotdata and FLAGB is gotroom.
        # At start FLAGB == True and FLAGC == False.  After a write
        # FLAGC == True.
        # Config1 onl
        
        assert fb.FLAGB == True
        assert fb.FLAGC == False
        assert not fm.IsData(fm.EP6)
        
        yield _write(fb, [0xCE])
        assert fb.FLAGB == True
        assert fb.FLAGC == False
        assert fm.IsData(fm.EP6, Num=1)
        dd = fm.Read(fm.EP6, Num=1)
        assert dd[0] == 0xCE

        assert fb.FLAGB == True
        assert fb.FLAGC == False

        data = [randint(0,0xFF) for ii in range(512)]
        yield _write(fb, data)
        assert fb.FLAGB == False
        assert fb.FLAGC == False
        assert fm.IsData(fm.EP6, Num=1)    # more than 1
        assert fm.IsData(fm.EP6, Num=512)  # more than 1

        yield _write(fb, [0xCE])
        assert fb.FLAGB == False
        assert fb.FLAGC == False
        assert fm.IsData(fm.EP6, Num=1)    # more than 1
        assert fm.IsData(fm.EP6, Num=512)  # more than 1

        rdata = fm.Read(fm.EP6, Num=512)
        for wd,rd in zip(data, rdata):
            assert wd == rd
        yield delay(13*fm.IFCLK_TICK)
        assert fb.FLAGB == True
        assert fb.FLAGC == False
        assert not fm.IsData(fm.EP6)        

        raise StopSimulation
        

    Simulation((tb_dut, tb_stimulus)).run()
    shutil.move('SlaveFifo.vcd', 'v_test_config1_host_read.vcd')
    
if __name__ == '__main__':
    test_config1_host_write()
    test_config1_host_read()
        
    
