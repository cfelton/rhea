#
# Copyright (c) 2006-2013 Christopher L. Felton
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

import sys, os
import copy
import logging
import threading
import time

from myhdl import *


class Bus(object):pass

GG = None
def _tricky():
    return GG

def SlaveFifo(fm, fx2_bus):
    """ Temp wrapper
    Interfaces are very powerful but not fully supported
    in MyHDL 0.7.  Easy to work around, anticipation that
    interfaces will be fully supported in newer releases.
    """

    cm = fm.SlaveFifo(fx2_bus)

    IFCLK = fx2_bus.IFCLK
    RST = fx2_bus.RST
    SLWR = fx2_bus.SLWR
    SLRD = fx2_bus.SLRD
    SLOE = fx2_bus.SLOE
    ADDR = fx2_bus.ADDR
    FDI = fx2_bus.FDI
    FDO = fx2_bus.FDO
    FLAGA = fx2_bus.FLAGA
    FLAGB = fx2_bus.FLAGB
    FLAGC = fx2_bus.FLAGC
    FLAGD = fx2_bus.FLAGD
    
    @always_comb
    def tb_monitor():
        if SLWR or SLRD or SLOE or FLAGA or FLAGB or FLAGC or FLAGD:
            fm.TracePrint('   %d control signal changed' % (now()))
        if ADDR == 0:
            fm.TracePrint('   %d address is zero' % (now()))
        else:
            fm.TracePrint('   %d address not zero %d' % (now(), ADDR))
        if FDI != FDO:
            fm.TracePrint('   %d data input != output' % (now()))
            
    return cm, tb_monitor


class Fx2Model(threading.Thread):
    """
    This is a model of the FX2 USB processor.

    The FX2 is double buffered, 512 blocks, this model will have
    3 queues per pipe to simulate the operation.  Two of the queues will emulate
    the 512 byte double buffer and the third queue will emulate the host queue.

    When reading or writing (host perspective) all data will be transfered in 512
    byte blocks.

    @todo Double buffer only implemented for endpoint 8 (Rd48).

    Note:  The internal variable names are from the host (testbench) perspective, i.e
           write* will be a write from the testbench.
    """
    EP2,EP4,EP6,EP8 = (2,4,6,8)
    IFCLK_TICK = 22
    
    def __init__(self, FifoSize=512, Config=0, Verbose=False, Trace=False):

        self.FifoSize = FifoSize

        # Setup the FIFOs for this configuration
        self.Configure(Config=Config)

        self.wrToggle = Signal(False)
        self.Stop = Signal(False)
        self.DoReset = Signal(False)

        self.Verbose  = Verbose
        self.Trace = Trace
        logging.basicConfig(filename='fx2_log.txt',
                            level=logging.DEBUG, filemode='w')
        self.ulog = logging.getLogger('Fx2Logger')
        threading.Thread.__init__(self)


    #---------------------------------------------------------------------------
    # simulation framework thread functions
    def setup(self, fx2_bus, g=()):
        self.fx2_bus = fx2_bus
        self.g = g

    def stop(self):
        self.Stop.next = True
        
    def run(self):
        """ Start the MyHDL Simulation.
        This function will start the myhdl simulator.  The myhdl simulator
        will run in a separate thread (this object).  The outside world will
        interact with the HDL simulator enviroment through the Read/Write
        functions.  These functions will send buffers (lists) to be read or
        written to the simulation enviornment.
        
        """
        global GG
        if self.Trace:
            tb_intf = traceSignals(SlaveFifo, self, self.fx2_bus)
        else:
            tb_intf = SlaveFifo(self, self.fx2_bus)

        @always(self.Stop.posedge)
        def tb_mon():
            raise StopSimulation
        
        GG = [tb_intf, tb_mon, self.g]
        #g = traceSignals(_tricky)
        Simulation(GG).run()


    #---------------------------------------------------------------------------
    def GetFx2Bus(self):
        #IFCLK,     # Output, 48MHz clock
        #RST,       # Input, system reset
        #SLWR,      # Slave write signal
        #SLRD,      # Slave read signal
        #SLOE,      # FIFO output enable
        #ADDR,      # FIFO Address Select
        #FDI,       # External Data bus, data in
        #FDO,       # External Data but, data out
        #FLAGA,     # Programmable FIFO flags
        #FLAGB,     # Programmable FIFO flags
        #FLAGC,     # Programmable FIFO flags
        #FLAGD      # Programmable FIFO flags

        dbl = 1 if self.Config == 1 else 0
        fx2 = Bus()
        fx2.IFCLK = Signal(bool(1))
        (fx2.SLWR,fx2.SLRD,fx2.SLOE) = [Signal(bool(dbl)) for ii in range(3)]
        fx2.RST = ResetSignal(bool(1), active=0, async=True)
        fx2.ADDR = Signal(intbv(0)[2:])
        fx2.FDI,fx2.FDO = [Signal(intbv(0)[8:]) for ii in (1,2)]
        (fx2.FLAGA,fx2.FLAGB,
         fx2.FLAGC,fx2.FLAGD) = [Signal(bool(0)) for ii in range(4)]
        return fx2
        
        
    #---------------------------------------------------------------------------
    def Configure(self, Config=0):
        """
        The FX2 USB controller has many programmable options for the
        slave fifo interface (GPIB interface not supported).  The USBP FPGA
        slave fifo interface supports two FX2 fifos and the FPGALINK (FL)
        supports a single FIFO.  The FX2 device allows many different FIFO
        and control signal configurations.  This function allows the same
        configurations in the model.

        USBP configuration (Config=0) :
           FIFOA - EP2 (write) EP6 (read)
           FIFOB - EP4 (write) EP8 (read)           

        FPGALINK configuration (Config=1) :
           FIFOA - EP2 (write) EP8 (read)
              FLAGB : gotroom
              FLAGC : gotdata

        @todo: need to implement double buffering
        """
        self.Config = Config
        # @todo: use a dict to hold the FIFOs
        #self.Fifos = {self.EP2:[],self.EP4:[],self.EP6:[],self.EP8}
        #if self.Config == 1: 
        #    self.Fifos[self.EP4] = None
        #    self.Fifos[self.EP6] = None
        
        if self.Config == 0:
            self.WrFifoEP2 = []  # Write FIFO (this) writes the fifo
            self.RdFifoEP6 = []  # Read FIFO        
            self.WrFifoEP4 = []  # Write FIFO
            self.RdFifoEP8 = []
        elif self.Config == 1:
            self.WrFifoEP2 = []
            self.RdFifoEP6 = [] 
            self.WrFifoEP4 = [] #None
            self.RdFifoEP8 = [] #None


    
    #---------------------------------------------------------------------------
    def TracePrint(self, str):
        if self.Verbose:
            #sys.write(str+'\n')
            #sys.stdout.flush()            
            self.ulog.debug('%d ... '%(now()) + str)   


    #---------------------------------------------------------------------------
    def SlaveFifo(self,
                  fx2_bus
                  ):
        """
        This function will drive the FX2 Slave FIFO interface.  This is intended
        to be part of a MyHDL simulation.

        USBP usage:
           FLAGA : EP2_EMPTY, EndPoint 2 Empty, ADDR = 00
           FLAGB : EP6_FULL, EndPoint 6 Full, ADDR = 10
           FLAGC : EP4_EMPTY, EndPoint 4 Empty, ADDR = 01
           FLAGD : EP8_FULL, EndPoint 8 Full, ADDR = 11
        """
        fx = fx2_bus
        self.fx2_bus = fx2_bus
        #fdi = Signal(intbv(0)[8:])
        #fdo = Signal(intbv(0)[8:])
        fdi = fx.FDI
        fdo = fx.FDO

        @always(delay(self.IFCLK_TICK/2))
        def tb_clkgen():
            #self.TracePrint('IFCLK %d' % (fx.IFCLK))
            fx.IFCLK.next = not fx.IFCLK

        @instance
        def tb_reset():
            while True:
                print('%8d ... Wait Reset' % (now()))
                yield self.DoReset.posedge
                print('%8d ... Do Reset' % (now()))
                fx.RST.next = False
                yield delay(13*self.IFCLK_TICK)
                fx.RST.next = True
                yield delay(13*self.IFCLK_TICK)
                self.DoReset.next = False
                print('%8d ... End Reset' % (now()))


        # The different configurations use different "active"
        # levels for the control signals.  Config0 uses active-high
        # Config1 uses active-low.  The model below always assumes
        # active-high signals, invert the signals for the configurations
        # that use active low signals
        # see the "work-around" ...
        slrd,slwr,sloe = [Signal(bool(0)) for ii in range(3)]
        _slrd,_slwr,_sloe = fx.SLRD,fx.SLWR,fx.SLOE
        @always_comb
        def hdl_assign():
            if self.Config == 1:
                slrd.next = not _slrd
                sloe.next = not _sloe
                slwr.next = not _slwr
            else:
                slrd.next = _slrd
                sloe.next = _sloe
                slwr.next = _slwr

        if self.Config == 0:
            EP2Addr,EP4Addr,EP6Addr,EP8Addr = (0,1,2,3)
        elif self.Config == 1:
            EP2Addr,EP4Addr,EP6Addr,EP8Addr = (0,-1,2,-1)
            
        @always(fx.IFCLK.posedge)
        def hdl_fifo_rw():
            if not fx.RST:
                #self.TracePrint('Slave Fifo Reset')
                if self.Config == 0:
                    # active-high status signals
                    fx.FLAGA.next = True   # Empty, FIFOA
                    fx.FLAGB.next = False  # Full, FIFOA
                    fx.FLAGC.next = True   # Empty, FIFOB
                    fx.FLAGD.next = False  # Full, FIFOB
                elif self.Config == 1:
                    fx.FLAGA.next = False  # not used
                    fx.FLAGD.next = False  # not used
                    fx.FLAGB.next = True   # (gotroom)
                    fx.FLAGC.next = False  # (gotdata)

            else:
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # Do Read / Writes to FIFOs
                # ?? How does the actual controller work ??
                # ?? can a read occur the same time the
                #    flags are being set?  Or are the flags
                #    In other words, the behavior of the
                #    read signal, if the read signal is always
                #    active does a read not occur till the
                #    FLAG* signals are set or right away.
                # ??   
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                assert ((slwr and not slrd)
                        or (not slwr and slrd)
                        or (not slwr and not slrd)), \
                       "Invalid Signal Combination SLWR %d SLRD %d" % (slwr, slrd)

                # Slave write (data into the controller)
                if slwr and not sloe:
                    if fx.ADDR == EP6Addr:
                        if len(self.RdFifoEP6) < self.FifoSize:
                            self.RdFifoEP6.append(int(fdi.val))
                    elif fx.ADDR == EP8Addr:
                        if len(self.RdFifoEP8) < self.FifoSize:
                            self.RdFifoEP8.append(int(fdi.val))                        

                # Slave read (data out of the controller)
                elif sloe and slrd:
                    # can only read if the flags have been set
                    FIFOA_Ok = (self.Config == 0 and not fx.FLAGA) or (self.Config == 1 and fx.FLAGC)
                    FIFOB_Ok = (self.Config == 0 and not fx.FLAGC)
                    #self.TracePrint("slave read %d, fifoA %s fifob %s" % (fx.ADDR, FIFOA_Ok, FIFOB_Ok))
                    if fx.ADDR == EP2Addr and FIFOA_Ok:
                        if len(self.WrFifoEP2) > 0:
                            self.TracePrint("      fifoA %s" % (self.WrFifoEP2))
                            self.WrFifoEP2.pop(0)
                    elif fx.ADDR == EP4Addr and FIFOB_Ok:
                        if len(self.WrFifoEP4) > 0:
                            self.TracePrint("      fifoB %s" % (self.WrFifoEP4))
                            self.WrFifoEP4.pop(0)

                if len(self.RdFifoEP8) == 128 or len(self.RdFifoEP8) == 256 or len(self.RdFifoEP8) == 512:
                    self.TracePrint("RdFifoEP8 len %d " % (len(self.RdFifoEP8)))
                    
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # FIFOs have been modified, adjust flags
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if self.Config == 0:
                    fx.FLAGA.next = False if len(self.WrFifoEP2) > 0 else True
                    fx.FLAGB.next = False if len(self.WrFifoEP4) > 0 else True
                    fx.FLAGC.next = True if len(self.RdFifoEP6) >= self.FifoSize else False
                    fx.FLAGD.next = True if len(self.RdFifoEP8) >= self.FifoSize else False

                elif self.Config == 1:
                    # FLAGB : gotroom
                    # FLAGC : gotdata
                    fx.FLAGC.next = True if len(self.WrFifoEP2) > 0 else False
                    fx.FLAGB.next = True if len(self.RdFifoEP6) < self.FifoSize else False
                    fx.FLAGA.next = True
                    fx.FLAGD.next = True

        #or self.wrToggle.posedge or self.wrToggle.negedge)
        @always(fx.IFCLK.posedge, fx.IFCLK.negedge) 
        def hdl_do():
            FIFOA_Ok = (self.Config == 0 and not fx.FLAGA) or (self.Config == 1 and fx.FLAGC)
            FIFOB_Ok = (self.Config == 0 and not fx.FLAGC)
            edge = 'p' if fx.IFCLK else 'n'
            if fx.ADDR == EP2Addr:
                if len(self.WrFifoEP2) > 0:
                    if slrd and FIFOA_Ok:
                        self.TracePrint('%8d [%s] fdo26 --> %s (%s)' % (now(), edge, hex(fdo), type(self.WrFifoEP2[0])))
                    fdo.next = self.WrFifoEP2[0]
                else:
                    fdo.next = 0
                    
            elif fx.ADDR == EP4Addr:
                if len(self.WrFifoEP4) > 0:
                    if slrd and FIFOB_Ok:
                        self.TracePrint('%8d [%s] fdo48 --> %s (%s)' % (now(), edge, hex(fdo), type(self.WrFifoEP4[0])))
                    fdo.next = self.WrFifoEP4[0]
                else:
                    fdo.next = 0
                
        return tb_clkgen, tb_reset, hdl_assign, hdl_fifo_rw, hdl_do
                

    #---------------------------------------------------------------------------
    def Reset(self):
        time.sleep(.1)
        self.TracePrint('[S] RST %d' % (self.fx2_bus.RST))
        self.DoReset.next = True
        time.sleep(.1)
        while self.DoReset:
            self.TracePrint('[W2] RST %d' % (self.fx2_bus.RST))
            time.sleep(.1)
        self.TracePrint('[E] RST %d' % (self.fx2_bus.RST))
            
    #---------------------------------------------------------------------------    
    def Read(self, ep, Num=1):
        """ Get values from an endpoint FIFO
        """
        rd = None
        if ep == self.EP6:
            if len(self.RdFifoEP6) > 0:
                rd = [self.RdFifoEP6.pop(0) for ii in range(Num)]
                #rd = self.RdFifoEP6.popleft()
            else:
                print('FX2: Error Read Fifo26')
        elif ep == self.EP8:
            if len(self.RdFifoEP8) > 0:
                rd = [self.RdFifoEP8.pop(0) for ii in range(Num)]
                #rd = self.RdFifoEP8.popleft()
            else:
                print('FX2: Error Read Fifo48')

        # @todo: toggle write signal (event)
        self.TracePrint('FX2: Read EP %s --> %s f26 %d f48 %d' % (ep, str(rd), len(self.RdFifoEP6), len(self.RdFifoEP8)))
        self.TracePrint('  FX2: Read f26 %s' % (self.RdFifoEP6))
        self.TracePrint('  FX2: Read f48 %s' % (self.RdFifoEP8))
        return rd


    #---------------------------------------------------------------------------
    def Write(self, data, ep):
        assert ep in (self.EP2, self.EP4), "Incorrect Endpoint"
        self.TracePrint('FX2: Write EP %s' % (ep))
        fifo = self.WrFifoEP2 if ep == self.EP2 else self.WrFifoEP4
        if type(data) is list:
            [fifo.append(d) for d in data]
            self.TracePrint("fill fifo %s with %s " % (ep, str(d)))
        elif isinstance(data, (int, long)):
            self.fifo.append(data)
        else:
            raise TypeError
                
        self.wrToggle.next = not self.wrToggle

    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # @todo: Need to make the following Is* functions more generic.  The
    #        Is* functions were specific to the USBP interface.  Need
    #        functions that work with the different configurations.
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    #---------------------------------------------------------------------------
    def IsEmpty(self, ep):
        self.TracePrint('FX2: Wait Empty EP %s' % (ep))
        if ep == self.EP2:
            if len(self.WrFifoEP2) > 0:
                return False
        elif ep == self.EP4:
            self.TracePrint('FX2: Length WrFifo48 %d' % (len(self.WrFifoEP4)))
            if len(self.WrFifoEP4) > 0:
                return False
                    
        return True


    #---------------------------------------------------------------------------
    def IsData(self, ep, Num=1):
        if ep == self.EP6:
            self.TracePrint('FX2: is Data EP %s %d' % (ep, len(self.RdFifoEP6)))
            if len(self.RdFifoEP6) < Num:
                return False
        elif ep == self.EP8:
            self.TracePrint('FX2: is Data EP %s %d' % (ep, len(self.RdFifoEP8)))
            if len(self.RdFifoEP8) < Num:
                return False

        return True


    #---------------------------------------------------------------------------
    def WaitEmpty(self, ep):
        """ Wait for empty (only if a simulation generator)
        """
        # @todo add empty trigger signal (event) to wait
        while not self.IsEmpty(ep):
            yield delay(2*self.IFCLK_TICK)


    #---------------------------------------------------------------------------
    def WaitData(self, ep, Num=1):
        """ Wait for data (only if a simulation generator)
        """
        # @todo add threshold trigger signal (event) to wait
        while not self.IsData(ep, Num):
            yield delay(2*self.IFCLK_TICK)
                    

        

        
