#
# Copyright (c) 2006-2013 Christopher L. Felton
#

from __future__ import division

import os
import logging
import threading
import time

import myhdl
from myhdl import Signal, ResetSignal, intbv, always, always_comb
from myhdl import instance, delay, StopSimulation, Simulation, now


class Bus(object):
    pass


@myhdl.block
def slave_fifo(fm, fx2_bus):
    """ Temp wrapper
    Interfaces are very powerful but not fully supported
    in MyHDL 0.7.  Easy to work around, anticipation that
    interfaces will be fully supported in newer releases.
    """

    cm = fm.slave_fifo(fx2_bus)

    # uppercase names to match names specified on the FX2 pins
    IFCLK = fx2_bus.IFCLK     # Output, 48MHz clock
    RST = fx2_bus.RST         # Input, system reset
    SLWR = fx2_bus.SLWR       # Slave write signal
    SLRD = fx2_bus.SLRD       # Slave read signal
    SLOE = fx2_bus.SLOE       # FIFO output enable
    ADDR = fx2_bus.ADDR       # FIFO Address Select
    FDI = fx2_bus.FDI         # External Data bus, data in
    FDO = fx2_bus.FDO         # External Data but, data out
    FLAGA = fx2_bus.FLAGA     # Programmable FIFO flags
    FLAGB = fx2_bus.FLAGB     # Programmable FIFO flags
    FLAGC = fx2_bus.FLAGC     # Programmable FIFO flags
    FLAGD = fx2_bus.FLAGD     # Programmable FIFO flags

    @always_comb
    def tb_monitor():
        if SLWR or SLRD or SLOE or FLAGA or FLAGB or FLAGC or FLAGD:
            fm.trace_print('   %d control signal changed' % (now()))
        if ADDR == 0:
            fm.trace_print('   %d address is zero' % (now()))
        else:
            fm.trace_print('   %d address not zero %d' % (now(), ADDR))
        if FDI != FDO:
            fm.trace_print('   %d data input != output' % (now()))
            
    return cm, tb_monitor


class Fx2Model(threading.Thread):
    EP2, EP4, EP6, EP8 = (2, 4, 6, 8)
    IFCLK_TICK = 22

    def __init__(self, fifo_size=512, config=0, verbose=False, trace=False):
        """
        This is a model of the FX2 USB processor.

        The FX2 is double buffered, 512 blocks, this model will have
        3 queues per pipe to simulate the operation.  Two of the queues will
        emulate the 512 byte double buffer and the third queue will emulate the
        host queue.

        When reading or writing (host perspective) all data will be transfered
        in 512 byte blocks.

        @todo Double buffer only implemented for endpoint 8 (Rd48).

        Note:  The internal variable names are from the host (testbench)
        perspective, i.e write* will be a write from the testbench.
        """

        self.fifo_size = fifo_size

        # Setup the FIFOs for this configuration
        self.configure(config=config)

        self.wr_toggle = Signal(False)
        self._stop = Signal(False)
        self.doreset = Signal(False)

        self.verbose = verbose
        self.trace = trace

        self.fx2_bus = None
        self.g = None

        if not os.path.isdir('output'):
            os.makedirs('output')
        logfn = os.path.join('output/', 'fx2_log.txt')
        logging.basicConfig(filename=logfn,
                            level=logging.DEBUG, filemode='w')

        self.ulog = logging.getLogger('Fx2Logger')
        threading.Thread.__init__(self)

    # ---------------------------------------------------------------------------
    # simulation framework thread functions
    def setup(self, fx2_bus, g=()):
        self.fx2_bus = fx2_bus
        self.g = g

    def stop(self):
        self._stop.next = True
        
    def run(self):
        """ Start the MyHDL Simulation.
        This function will start the myhdl simulator.  The myhdl simulator
        will run in a separate thread (this object).  The outside world will
        interact with the HDL simulator enviroment through the Read/Write
        functions.  These functions will send buffers (lists) to be read or
        written to the simulation enviornment.
        """
        gens = []
        # use the module/function wrapper for tracing
        tb_intf = slave_fifo(self, self.fx2_bus)

        @always(self._stop.posedge)
        def tb_mon():
            raise StopSimulation

        tb_intf.config_sim(trace=self.trace)
        gens = [tb_intf, tb_mon, self.g]
        sim = Simulation(gens)
        sim.run()
        sim.quit()

    # ---------------------------------------------------------------------------
    def get_bus(self):
        dbl = 1 if self.config == 1 else 0
        fx2 = Bus()
        fx2.IFCLK = Signal(bool(1))
        (fx2.SLWR, fx2.SLRD, fx2.SLOE) = [Signal(bool(dbl)) for _ in range(3)]
        fx2.RST = ResetSignal(bool(1), active=0, async=True)
        fx2.ADDR = Signal(intbv(0)[2:])
        fx2.FDI, fx2.FDO = [Signal(intbv(0)[8:]) for _ in (1, 2)]
        (fx2.FLAGA, fx2.FLAGB,
         fx2.FLAGC, fx2.FLAGD) = [Signal(bool(0)) for _ in range(4)]

        return fx2

    # ---------------------------------------------------------------------------
    def configure(self, config=0):
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
        self.config = config

        if self.config == 0:
            self.wr_fifo_ep2 = []  # Write FIFO (this) writes the fifo
            self.rd_fifo_ep6 = []  # Read FIFO
            self.wr_fifo_ep4 = []  # Write FIFO
            self.rd_fifo_ep8 = []
        elif self.config == 1:
            self.wr_fifo_ep2 = []
            self.rd_fifo_ep6 = []
            self.wr_fifo_ep4 = []
            self.rd_fifo_ep8 = []

    # ---------------------------------------------------------------------------
    def trace_print(self, str):
        if self.verbose:
            self.ulog.debug('%d ... ' % (now()) + str,)

    # ---------------------------------------------------------------------------
    @myhdl.block
    def slave_fifo(self, fx2_bus):
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
        fdi = fx.FDI
        fdo = fx.FDO

        @always(delay(self.IFCLK_TICK//2))
        def tb_clkgen():
            fx.IFCLK.next = not fx.IFCLK

        @instance
        def tb_reset():
            while True:
                print('%8d ... Wait Reset' % (now()))
                yield self.doreset.posedge
                print('%8d ... Do Reset' % (now()))
                fx.RST.next = False
                yield delay(13*self.IFCLK_TICK)
                fx.RST.next = True
                yield delay(13*self.IFCLK_TICK)
                self.doreset.next = False
                print('%8d ... End Reset' % (now()))

        # The different configurations use different "active"
        # levels for the control signals.  Config0 uses active-high
        # Config1 uses active-low.  The model below always assumes
        # active-high signals, invert the signals for the configurations
        # that use active low signals
        # see the "work-around" ...
        slrd, slwr, sloe = [Signal(bool(0)) for ii in range(3)]
        _slrd, _slwr, _sloe = fx.SLRD, fx.SLWR, fx.SLOE

        @always_comb
        def hdl_assign():
            if self.config == 1:
                slrd.next = not _slrd
                sloe.next = not _sloe
                slwr.next = not _slwr
            else:
                slrd.next = _slrd
                sloe.next = _sloe
                slwr.next = _slwr

        if self.config == 0:
            ep2_addr, ep4_addr, ep6_addr, ep8_addr = (0, 1, 2, 3)
        elif self.config == 1:
            ep2_addr, ep4_addr, ep6_addr, ep8_addr = (0, -1, 2, -1)
            
        @always(fx.IFCLK.posedge)
        def hdl_fifo_rw():
            if not fx.RST:
                if self.config == 0:
                    # active-high status signals
                    fx.FLAGA.next = True   # Empty, FIFOA
                    fx.FLAGB.next = False  # Full, FIFOA
                    fx.FLAGC.next = True   # Empty, FIFOB
                    fx.FLAGD.next = False  # Full, FIFOB
                elif self.config == 1:
                    fx.FLAGA.next = False  # not used
                    fx.FLAGD.next = False  # not used
                    fx.FLAGB.next = True   # (gotroom)
                    fx.FLAGC.next = False  # (gotdata)
            else:
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # Do Read / Writes to FIFOs
                # ?? How does the actual controller work ??
                # ?? can a read occur the same time the
                #    flags are being set?  Or are the flags
                #    In other words, the behavior of the
                #    read signal, if the read signal is always
                #    active does a read not occur till the
                #    FLAG* signals are set or right away.
                # ??   
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                assert ((slwr and not slrd)
                        or (not slwr and slrd)
                        or (not slwr and not slrd)), \
                        "Invalid Signal Combination SLWR %d SLRD %d" % \
                        (slwr, slrd,)

                # Slave write (data into the controller)
                if slwr and not sloe:
                    if fx.ADDR == ep6_addr:
                        if len(self.rd_fifo_ep6) < self.fifo_size:
                            self.rd_fifo_ep6.append(int(fdi.val))
                    elif fx.ADDR == ep8_addr:
                        if len(self.rd_fifo_ep8) < self.fifo_size:
                            self.rd_fifo_ep8.append(int(fdi.val))

                # Slave read (data out of the controller)
                elif sloe and slrd:
                    # can only read if the flags have been set
                    FIFOA_Ok = (self.config == 0 and not fx.FLAGA) or (self.config == 1 and fx.FLAGC)
                    FIFOB_Ok = (self.config == 0 and not fx.FLAGC)
                    if fx.ADDR == ep2_addr and FIFOA_Ok:
                        if len(self.wr_fifo_ep2) > 0:
                            self.trace_print("      fifoA %s" % (self.wr_fifo_ep2))
                            self.wr_fifo_ep2.pop(0)
                    elif fx.ADDR == ep4_addr and FIFOB_Ok:
                        if len(self.wr_fifo_ep4) > 0:
                            self.trace_print("      fifoB %s" % (self.wr_fifo_ep4))
                            self.wr_fifo_ep4.pop(0)

                if len(self.rd_fifo_ep8) == 128 or len(self.rd_fifo_ep8) == 256 or len(self.rd_fifo_ep8) == 512:
                    self.trace_print("rd_fifo_ep8 len %d " % (len(self.rd_fifo_ep8,)))
                    
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # FIFOs have been modified, adjust flags
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                if self.config == 0:
                    fx.FLAGA.next = False if len(self.wr_fifo_ep2) > 0 else True
                    fx.FLAGB.next = False if len(self.wr_fifo_ep4) > 0 else True
                    fx.FLAGC.next = True if len(self.rd_fifo_ep6) >= self.fifo_size else False
                    fx.FLAGD.next = True if len(self.rd_fifo_ep8) >= self.fifo_size else False

                elif self.config == 1:
                    # FLAGB : gotroom
                    # FLAGC : gotdata
                    fx.FLAGC.next = True if len(self.wr_fifo_ep2) > 0 else False
                    fx.FLAGB.next = True if len(self.rd_fifo_ep6) < self.fifo_size else False
                    fx.FLAGA.next = True
                    fx.FLAGD.next = True

        # or self.wrToggle.posedge or self.wrToggle.negedge)
        @always(fx.IFCLK.posedge, fx.IFCLK.negedge) 
        def hdl_do():
            FIFOA_Ok = (self.config == 0 and not fx.FLAGA) or (self.config == 1 and fx.FLAGC)
            FIFOB_Ok = (self.config == 0 and not fx.FLAGC)
            edge = 'p' if fx.IFCLK else 'n'
            if fx.ADDR == ep2_addr:
                if len(self.wr_fifo_ep2) > 0:
                    if slrd and FIFOA_Ok:
                        self.trace_print('%8d [%s] fdo26 --> %s (%s)' % (
                            now(), edge, hex(fdo), type(self.wr_fifo_ep2[0])))
                    fdo.next = self.wr_fifo_ep2[0]
                else:
                    fdo.next = 0
                    
            elif fx.ADDR == ep4_addr:
                if len(self.wr_fifo_ep4) > 0:
                    if slrd and FIFOB_Ok:
                        self.trace_print('%8d [%s] fdo48 --> %s (%s)' % (
                            now(), edge, hex(fdo), type(self.wr_fifo_ep4[0])))
                    fdo.next = self.wr_fifo_ep4[0]
                else:
                    fdo.next = 0
                
        return tb_clkgen, tb_reset, hdl_assign, hdl_fifo_rw, hdl_do

    # ---------------------------------------------------------------------------
    def reset(self):
        time.sleep(.1)
        self.trace_print('[S] RST %d' % (self.fx2_bus.RST,))
        self.doreset.next = True
        time.sleep(.1)
        while self.doreset:
            self.trace_print('[W2] RST %d' % (self.fx2_bus.RST,))
            time.sleep(.1)
        self.trace_print('[E] RST %d' % (self.fx2_bus.RST,))
            
    # ---------------------------------------------------------------------------
    def read(self, ep, num=1):
        """ Get values from an endpoint FIFO
        """
        rd = None
        if ep == self.EP6:
            if len(self.rd_fifo_ep6) > 0:
                rd = [self.rd_fifo_ep6.pop(0) for _ in range(num)]
            else:
                print('FX2: Error Read Fifo26')
        elif ep == self.EP8:
            if len(self.rd_fifo_ep8) > 0:
                rd = [self.rd_fifo_ep8.pop(0) for _ in range(num)]
            else:
                print('FX2: Error Read Fifo48')

        # @todo: toggle write signal (event)
        self.trace_print('FX2: Read EP %s --> %s f26 %d f48 %d' % (
            ep, str(rd), len(self.rd_fifo_ep6), len(self.rd_fifo_ep8)))
        self.trace_print('  FX2: Read f26 %s' % (self.rd_fifo_ep6,))
        self.trace_print('  FX2: Read f48 %s' % (self.rd_fifo_ep8,))

        return rd

    # ---------------------------------------------------------------------------
    def write(self, data, ep):
        assert ep in (self.EP2, self.EP4), "Incorrect Endpoint"
        self.trace_print('FX2: Write EP %s' % (ep,))
        fifo = self.wr_fifo_ep2 if ep == self.EP2 else self.wr_fifo_ep4
        if isinstance(data, list):
            for d in data:
                fifo.append(d)
                self.trace_print("fill fifo %s with %s " % (ep, str(d)))
        elif isinstance(data, int):
            self.fifo.append(data)
        else:
            raise TypeError
                
        self.wr_toggle.next = not self.wr_toggle
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # @todo: Need to make the following Is* functions more generic.  The
    #        Is* functions were specific to the USBP interface.  Need
    #        functions that work with the different configurations.
    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    # ---------------------------------------------------------------------------
    def isempty(self, ep):
        self.trace_print('FX2: Wait Empty EP %s' % (ep))
        if ep == self.EP2:
            if len(self.wr_fifo_ep2) > 0:
                return False
        elif ep == self.EP4:
            self.trace_print('FX2: Length WrFifo48 %d' % (len(self.wr_fifo_ep4)))
            if len(self.wr_fifo_ep4) > 0:
                return False
                    
        return True

    # ---------------------------------------------------------------------------
    def isdata(self, ep, num=1):
        data = True
        if ep == self.EP6:
            self.trace_print('FX2: is Data EP %s %d' % (ep, len(self.rd_fifo_ep6),))
            if len(self.rd_fifo_ep6) < num:
                data = False
        elif ep == self.EP8:
            self.trace_print('FX2: is Data EP %s %d' % (ep, len(self.rd_fifo_ep8)))
            if len(self.rd_fifo_ep8) < num:
                data = False

        return data

    # ---------------------------------------------------------------------------
    def wait_empty(self, ep):
        """ Wait for empty (only if a simulation generator)
        """
        # @todo add empty trigger signal (event) to wait
        while not self.isempty(ep):
            yield delay(2*self.IFCLK_TICK)

    # ---------------------------------------------------------------------------
    def wait_data(self, ep, num=1):
        """ Wait for data (only if a simulation generator)
        """
        # @todo add threshold trigger signal (event) to wait
        while not self.isdata(ep, num):
            yield delay(2*self.IFCLK_TICK)
