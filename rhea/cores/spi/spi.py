#
# Copyright (c) 2006-2015 Christopher L. Felton
#
"""
SPI interface
-------------

This module is controlled / configured from the register bus.
data can either be transferred from the register bus or
it can be transferred from the streaming interface.

This module is register compatible with the Xilinx OPB SPI
controller.  The interrupt register has been removed and replaced
with a clock divide register.
"""
from __future__ import absolute_import, division

from myhdl import *

from ..fifo import fifo_fast
from rhea.system import Bit, Byte
from rhea.system import ControlStatus
from rhea.system import FIFOBus


class SPIControlStatus(ControlStatus):
    def __init__(self):
        """
        Attributes:
            enable: enable the SPI controller
            freeze: freeze the current state
            bypass_fifo: the write_data and read_data sink and source
              the FIFO instead of the FIFOBus
            clock_polarity:
            clock_phase:
            manual_slave_select:
            rx_empty:
            rx_full:
            tx_empty:
            tx_full:
            slave_select_fault
            tx_byte:
            rx_byte:
            slave_select:
            tx_fifo_count:
            rx_fifo_count:
            clock_divisor:
        """
        # control / configuration signals
        self.enable = Bit()
        self.freeze = Bit()
        self.bypass_fifo = Bit()
        self.loop = Bit()
        self.clock_polarity = Bit()
        self.clock_phase = Bit()
        self.manual_slave_select = Bit()

        # status signals
        self.rx_empty = Bit()
        self.rx_full = Bit()
        self.tx_empty = Bit()
        self.tx_full = Bit()
        self.slave_select_fault = Bit()

        self.tx_byte = Byte()
        self.rx_byte = Byte()
        self.slave_select = Byte()
        self.tx_fifo_count = Byte()
        self.rx_fifo_count = Byte()
        self.clock_divisor = Byte()

        super(SPIControlStatus, self).__init__()


def spi_controller(
    # ---[ Module Ports]---
    glbl,    # global interface, clock, reset, etc.
    regbus,  # memory-mapped register bus

    rxfb,    # streaming interface, receive fifo bus
    txfb,    # streaming interface, transmit fifo bus
    spibus,  # external SPI bus

    tstpts = None,
    
    # ---[ Module Parameters ]---
    base_address=0x0400,  # base address (memmap register bus)
    include_fifo=True,    # include aan 8 byte deep FIFO
    sck_frequency=100e3   # desired frequency of SCK
    ):
    """ SPI (Serial Peripheral Interface) module

    This is a generic SPI implementation, the register layout
    is similar to other SPI controller.


    """
    clock, reset = glbl.clock, glbl.reset
    # -- local signals --
    ena = Signal(False)
    clkcnt = Signal(modbv(0, min=0, max=2**12))
    bcnt = Signal(intbv(0, min=0, max=8))

    # separate tx and rx shift-registers (could be one in the same)
    treg = Signal(intbv(0)[8:])  # tx shift register
    rreg = Signal(intbv(0)[8:])  # rx shift register
    
    x_sck = Signal(False)
    x_ss = Signal(False)
    x_mosi = Signal(False)
    x_miso = Signal(False)

    # internal FIFO bus interfaces
    #   external FIFO side (FIFO to external SPI bus)
    xfb = FIFOBus(size=txfb.size, width=txfb.width)  
    #   internal FIFO side (FIFO to internal bus)
    ifb = FIFOBus(size=rxfb.size, width=rxfb.width)  
    
    States = enum('IDLE', 'WAIT_HCLK', 'DATA_IN', 'DATA_CHANGE',
                  'WRITE_FIFO', 'END')
    state = Signal(States.IDLE)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # memory- mapped registers
    # add the peripheral's regfile to the bus (informational only)
    regfile.base_address = base_address
    g_regbus = regbus.add(regfile, 'spi')

    # FIFO for the wishbone data transfer
    if include_fifo:
        g_tx_fifo = fifo_fast(clock, reset, txfb)
        g_rx_fifo = fifo_fast(clock, reset, rxfb)

    @always_comb
    def rtl_assign():
        regfile.sptc.next = txfb.count
        regfile.sprc.next = rxfb.count

        if clkcnt > 0:
            ena.next = False
        else:
            ena.next = True

    @always(regbus.clock.posedge)
    def rtl_clk_div():
        if regfile.spcr.spe and clkcnt != 0 and state != States.IDLE:
            clkcnt.next = (clkcnt - 1)
        else:
            if   regfile.spxx == 0:   clkcnt.next = 0     # 2
            elif regfile.spxx == 1:   clkcnt.next = 1     # 4
            elif regfile.spxx == 2:   clkcnt.next = 3     # 8
            elif regfile.spxx == 3:   clkcnt.next = 7     # 16
            elif regfile.spxx == 4:   clkcnt.next = 15    # 32
            elif regfile.spxx == 5:   clkcnt.next = 31    # 64
            elif regfile.spxx == 6:   clkcnt.next = 63    # 128
            elif regfile.spxx == 7:   clkcnt.next = 127   # 256
            elif regfile.spxx == 8:   clkcnt.next = 255   # 512
            elif regfile.spxx == 9:   clkcnt.next = 511   # 1024
            elif regfile.spxx == 10:  clkcnt.next = 1023  # 2048
            elif regfile.spxx == 11:  clkcnt.next = 2047  # 4096
            else: clkcnt.next = 4095

    @always_seq(regbus.clock.posedge, reset=regbus.reset)
    def rtl_state_and_more():
        """
        Designed to the following timing diagram

        SCK   CPOL=0 ______/---\___/---\___/---\___/---\___/---\___/---\___/---\___/---\___/---\ 
              CPOL=1 ------\___/---\___/---\___/---\___/---\___/---\___/---\___/---\___/---\___/ 
        SS           ---\_______________________________________________________________________ 
        CPHA=0 MOSI  ...|.0....|.1.....|.2.....|.3.....|.4.....|.5.....|.6.....|.7.....|.0.....| 
               MISO  ...|.0....|.1.....|.2.....|.3.....|.4.....|.5.....|.6.....|.7.....|.0.....| 
        CPHA=1 MOSI  ...|....0.....|.1.....|.2.....|.3.....|.4.....|.5.....|.6.....|.7.....|.0...
               MISO  ......|.0.....|.1.....|.2.....|.3.....|.4.....|.5.....|.6.....|.7.....|.0...
        """
        if not regfile.spcr.spe:
            state.next = States.IDLE
            bcnt.next = 0
            treg.next = 0
            
            xfb.rd.next = False
            xfb.wr.next = False

            x_sck.next = False
            x_ss.next = False
        else:
            if not regfile.freeze:
                # ~~~~ Idle state ~~~~
                if state == States.IDLE:
                    bcnt.next = 7
                    treg.next = xfb.rdata
                    x_sck.next = regfile.spcr.cpol
                    xfb.wr.next = False
                    
                    if not xfb.empty and not xfb.full:
                        xfb.rd.next = True
                        x_ss.next = False
                        if regfile.spcr.cpha: # Clock in on second phase 
                            state.next = States.WAIT_HCLK
                        else:  # Clock in on first phase
                            state.next = States.DATA_IN
                    else:
                        xfb.rd.next = False
                        x_ss.next  = True

                # ~~~~ Wait half clock period for cpha=1 ~~~~
                elif state == States.WAIT_HCLK:
                    xfb.rd.next = False
                    xfb.wr.next = False
                    if ena:
                        x_sck.next = not x_sck
                        state.next = States.DATA_IN

                # ~~~~ Clock data in (and out) ~~~~
                elif state == States.DATA_IN:
                    xfb.rd.next = False
                    xfb.wr.next = False
                    if ena:  # clk div
                        x_sck.next = not x_sck
                        rreg.next = concat(rreg[7:0], x_miso)
                        
                        if regfile.spcr.cpha and bcnt == 0:
                            xfb.wr.next = True
                            if xfb.empty or xfb.full:
                                state.next = States.END
                            else:
                                state.next = States.DATA_CHANGE
                                #bcnt.next  = 7
                                #x_fifo_rd.next = True
                                #treg.next = x_fifo_do
                        else:                            
                            state.next = States.DATA_CHANGE

                # ~~~~ Get ready for next byte out/in ~~~~
                elif state == States.DATA_CHANGE:
                    xfb.rd.next = False                    
                    xfb.wr.next = False                    
                    if ena:
                        x_sck.next = not x_sck
                        if bcnt == 0:  
                            if not regfile.spcr.cpha:
                                xfb.wr.next = True
                                
                            if xfb.empty or xfb.full:
                                state.next = States.END
                            else:  # more data to transfer
                                bcnt.next = 7
                                state.next = States.DATA_IN
                                xfb.rd.next = True
                                treg.next = xfb.rdata
                        else:
                            treg.next = concat(treg[7:0], intbv(0)[1:])
                            bcnt.next = bcnt - 1                        
                            state.next = States.DATA_IN

                # ~~~~ End state ~~~~
                elif state == States.END:
                    xfb.rd.next = False
                    xfb.wr.next = False                    
                    if ena:  # Wait half clock cycle go idle
                        state.next = States.IDLE

                # Shouldn't happen, error in logic
                else:
                    state.next = States.IDLE
                    assert False, "SPI Invalid State"

    @always_comb
    def rtl_fifo_sel():
        if regfile.spst.rdata:
            # data comes from the register file
            xfb.empty.next = txfb.empty
            xfb.full.next = rxfb.full
            xfb.rdata.next = txfb.rdata
            
            txfb.rd.next = xfb.rd
            txfb.wr.next = regfile.sptx.wr
            txfb.wdata.next = regfile.sptx            
            
            rxfb.wr.next = xfb.wr            
            rxfb.wdata.next = rreg
            rxfb.rd.next = regfile.sprx.rd    
            regfile.sprx.next = rxfb.rdata
            
            ifb.rd.next = False
            ifb.wr.next = False
            ifb.wdata.next = 0  # or'd bus must be 0

        else:
            # data comes from external FIFO bus interface            
            xfb.empty.next = ifb.empty
            xfb.full.next = ifb.full
            xfb.rdata.next = ifb.rdata
            
            txfb.rd.next = False
            rxfb.wr.next = False
            rxfb.wdata.next = 0  # or'd bus must be 0
            txfb.wr.next = False
            rxfb.rd.next = False

            ifb.rd.next = xfb.rd
            ifb.wr.next = xfb.wr
            ifb.wdata.next = treg

    @always_comb
    def rtl_x_mosi():
        # @todo lsbf control signal
        x_mosi.next = treg[7]

    @always(regbus.clock.posedge)
    def rtl_spi_sigs():
        spibus.sck.next = x_sck

        if regfile.spcr.loop:
            spibus.mosi.next = False
            x_miso.next = x_mosi
        else:
            spibus.mosi.next = x_mosi
            x_miso.next = spibus.mosi

        if regfile.spcr.msse:
            spibus.ss.next = ~regfile.spss
        else:
            if x_ss:
                spibus.ss.next = 0xFF
            else:
                spibus.ss.next = ~regfile.spss

    # myhdl generators in the __debug__ conditionals is not 
    # converted.
    if spi_controller.debug:
        @instance
        def mon_state():
            print("  :{:8d}: initial state {}".format(
                now(), str(state)))
                
            while True:
                yield state
                print("  :{:8d}: state trasition --> {}".format(
                    now(), str(state)))
                
        fbidle = intbv('0000')[4:]    
        @instance
        def mon_trace():
            while True:
                yield clock.posedge
                ccfb = concat(txfb.wr, txfb.rd, rxfb.wr, rxfb.rd)
                if ccfb != fbidle:
                    print("  :{:8d}: tx: w{} r{}, f{} e{}, rx: w{} r{} f{} e{}".format(
                        now(), 
                        int(txfb.wr), int(txfb.rd), int(txfb.full), int(txfb.empty),
                        int(rxfb.wr), int(rxfb.rd), int(rxfb.full), int(rxfb.empty),))
                    
        @always(clock.posedge)
        def mon_tx_fifo_write():
            if txfb.wr:
                print("   WRITE tx fifo {:02X}".format(int(txfb.wdata)))
            if txfb.rd:
                print("   READ tx fifo {:02X}".format(int(txfb.rdata)))
                
        @always(clock.posedge)
        def mon_rx_fifo_write():
            if rxfb.wr:
                print("   WRITE rx fifo {:02X}".format(int(rxfb.wdata)))
                
            if rxfb.rd:
                print("   READ rx fifo {:02X}".format(int(rxfb.rdata)))

    if tstpts is not None:
        if isinstance(tstpts.val, intbv) and len(tstpts) == 8:
            @always_comb    
            def rtl_tst_pts():
                tstpts.next[0] = spibus.ss[0]
                tstpts.next[1] = spibus.sck
                tstpts.next[2] = spibus.mosi
                tstpts.next[3] = spibus.miso
                
                tstpts.next[4] = txfb.wr
                tstpts.next[5] = txfb.rd
                tstpts.next[6] = rxfb.wr
                tstpts.next[7] = rxfb.rd
        else:
            print("WARNING: SPI tst_pts is not None but is not an intbv(0)[8:]")

    # return the myhdl generators
    gens = instances()
    
    return gens

spi_controller.debug = False
spi_controller.cso = SPIControlStatus
spi_controller.portmap = dict()
