
import os
from random import randint
import shutil

import myhdl
from myhdl import delay, instance, StopSimulation

from rhea.models.usbext import Fx2Model
from rhea.models.usbext.fx2 import slave_fifo
from rhea.utils.test import run_testbench

# The Fx2Model has two config modes.  The actual FX2 controller has
# numerous programmable modes.  The "configs" emulate configurations
# for different FX2 firmware (fpgalink, usrp, usbp, ...).  


def test_config1_host_write():
    """
    """

    fm = Fx2Model(config=1, verbose=True, trace=False)
    fb = fm.get_bus()

    def writetrans(fm, num=1):
        pass
    
    def readtrans(fb, num=1):
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

    @myhdl.block
    def bench_host_write():

        tbdut = slave_fifo(fm, fb)

        @instance
        def tbstim():
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

            assert fb.FLAGB
            assert not fb.FLAGC

            fm.write([0xCE], fm.EP2)
            yield delay(3*fm.IFCLK_TICK)
            assert fb.FLAGB  # still should have room
            assert fb.FLAGC  # should have data now
            assert fb.FDO == 0xCE
            assert not fm.isempty(fm.EP2)

            # read out the data written, 1 byte
            yield readtrans(fb, 1)
            assert fb.FLAGB      # still should have room
            assert not fb.FLAGC  # no data now
            assert fm.isempty(fm.EP2)
            yield delay(13*fm.IFCLK_TICK)

            # Write a burst of data and read the burst of data
            data = list(range(33))
            data[0] = 0xFE
            fm.write(data, fm.EP2)
            yield delay(3*fm.IFCLK_TICK)
            assert fb.FLAGB  # still should have room
            assert fb.FLAGC  # should have data now
            assert fb.FDO == 0xFE
            assert not fm.isempty(fm.EP2)

            yield readtrans(fb, 33)
            assert fb.FLAGB      # still should have room
            assert not fb.FLAGC  # now data now
            assert fm.isempty(fm.EP2)

            # read one more
            yield readtrans(fb, 1)

            # fill the FIFO
            data = [randint(0, 0xFF) for _ in range(512)]
            fm.write(data, fm.EP2)
            yield delay(3*fm.IFCLK_TICK)
            assert fb.FLAGB  # still should have room
            assert fb.FLAGC  # should have data now
            assert fb.FDO == data[0]
            assert not fm.isempty(fm.EP2)

            yield readtrans(fb, 512)
            assert fb.FLAGB      # still should have room
            assert not fb.FLAGC  # now data now
            assert fm.isempty(fm.EP2)

            # The model should handle flow, control it will take
            # how much ever data? (this emulates how the host USB
            # software stack would work).
            data = [randint(0, 0xFF) for _ in range(517)]
            fm.write(data, fm.EP2)
            yield delay(3*fm.IFCLK_TICK)
            assert fb.FLAGB  # still should have room
            assert fb.FLAGC  # should have data now
            assert fb.FDO == data[0]
            assert not fm.isempty(fm.EP2)

            yield readtrans(fb, 512)
            assert fb.FLAGB  # still should have room
            assert fb.FLAGC  # now data now

            yield readtrans(fb, 7)
            assert fb.FLAGB      # still should have room
            assert not fb.FLAGC  # now data now
            assert fm.isempty(fm.EP2)

            raise StopSimulation

        return tbdut, tbstim

    run_testbench(bench_host_write)


def test_config1_host_read():
    """
    """

    fm = Fx2Model(config=1, verbose=True, trace=False)
    fb = fm.get_bus()

    def writetrans(fb, data):
        yield fb.IFCLK.posedge
        for dd in data:
            fb.FDI.next = dd
            fb.SLWR.next = False
            yield fb.IFCLK.posedge
        fb.SLWR.next = True
        yield delay(3*fm.IFCLK_TICK)
    
    def readtrans(fm, num=1):
        pass


    @myhdl.block
    def bench_host_read():

        tbdut = slave_fifo(fm, fb)

        @instance
        def tbstim():
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

            assert fb.FLAGB
            assert not fb.FLAGC
            assert not fm.isdata(fm.EP6)

            yield writetrans(fb, [0xCE])
            assert fb.FLAGB
            assert not fb.FLAGC
            assert fm.isdata(fm.EP6, num=1)
            dd = fm.read(fm.EP6, num=1)
            assert dd[0] == 0xCE

            assert fb.FLAGB
            assert not fb.FLAGC

            data = [randint(0, 0xFF) for _ in range(512)]
            yield writetrans(fb, data)
            assert not fb.FLAGB
            assert not fb.FLAGC
            assert fm.isdata(fm.EP6, num=1)    # more than 1
            assert fm.isdata(fm.EP6, num=512)  # more than 1

            yield writetrans(fb, [0xCE])
            assert not fb.FLAGB
            assert not fb.FLAGC
            assert fm.isdata(fm.EP6, num=1)    # more than 1
            assert fm.isdata(fm.EP6, num=512)  # more than 1

            rdata = fm.read(fm.EP6, num=512)
            for wd, rd in zip(data, rdata):
                assert wd == rd
            yield delay(13*fm.IFCLK_TICK)
            assert fb.FLAGB
            assert not fb.FLAGC
            assert not fm.isdata(fm.EP6)

            raise StopSimulation

        return tbdut, tbstim

    run_testbench(bench_host_read)


if __name__ == '__main__':
    test_config1_host_write()
    test_config1_host_read()
