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
from rhea.system import FIFOBus

from .cso import SPIControlStatus


def spi_controller(
    # ---[ Module Ports]---
    glbl,          # global interface, clock, reset, etc.
    spibus,        # external SPI bus
    # optional ports
    fifobus=None,  # streaming interface, FIFO bus
    mmbus=None,    # memory-mapped bus, contro status access
    cso=None,      # control-status object
    
    # ---[ Module Parameters ]---
    include_fifo=True,    # include aan 8 byte deep FIFO
):
    """ SPI (Serial Peripheral Interface) module
    This module is an SPI controller (master) and can be used to interface
    with various external SPI devices.

    Arguments:
        glbl (Global): clock and reset interface
        spibus (SPIBus): external (off-chip) SPI bus
        fifobus (FIFOBus): interface to the FIFOs, write side is to
          the TX the read side from the RX.
        mmbus (MemoryMapped): a memory-mapped bus used to access
          the control-status signals.
        cso (ControlStatus): the control-status object used to control
          this peripheral

        include_fifo (bool): include the FIFO ... this is not fully
          implemented

    Note:
        At last check the register-file automation was not complete, only
        the `cso` external control or `cso` configuration can be utilized.
    """
    clock, reset = glbl.clock, glbl.reset
    if cso is None:
        cso = spi_controller.cso()

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
    itx = FIFOBus(size=fifobus.size, width=fifobus.width)
    #   internal FIFO side (FIFO to internal bus)
    irx = FIFOBus(size=fifobus.size, width=fifobus.width)
    
    states = enum('idle', 'wait_hclk', 'data_in', 'data_change',
                  'write_fifo', 'end')
    state = Signal(states.idle)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # memory- mapped registers
    # add the peripheral's regfile to the bus (informational only)
    # @todo: the automatic building of the register files is incomplete
    if mmbus is not None:
        # the register-file (rf) will drive all the cso signals
        rf = cso.get_register_file()
        mmbus.add(rf, 'spi')

    # FIFO for the wishbone data transfer
    if include_fifo:
        fifo_tx_inst = fifo_fast(clock, reset, itx)
        fifo_rx_inst = fifo_fast(clock, reset, irx)

    @always_comb
    def rtl_assign():
        cso.tx_fifo_count.next = itx.count
        cso.rx_fifo_count.next = irx.count

        if clkcnt > 0:
            ena.next = False
        else:
            ena.next = True

    clock_counts = tuple([(2**ii)-1 for ii in range(13)])

    @always(clock.posedge)
    def rtl_clk_div():
        if cso.enable and clkcnt != 0 and state != states.idle:
            clkcnt.next = (clkcnt - 1)
        else:
            clkcnt.next = clock_counts[cso.clock_divisor]

    @always_seq(clock.posedge, reset=reset)
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
        if not cso.enable:
            state.next = states.idle
            bcnt.next = 0
            treg.next = 0
            
            itx.rd.next = False
            irx.wr.next = False

            x_sck.next = False
            x_ss.next = False
        else:
            if not cso.freeze:
                # ~~~~ Idle state ~~~~
                if state == states.idle:
                    bcnt.next = 7
                    treg.next = itx.rdata
                    x_sck.next = cso.clock_polarity
                    irx.wr.next = False
                    
                    if not itx.empty and not irx.full:
                        itx.rd.next = True
                        x_ss.next = False
                        if cso.clock_phase:  # Clock in on second phase
                            state.next = states.wait_hclk
                        else:  # Clock in on first phase
                            state.next = states.data_in
                    else:
                        itx.rd.next = False
                        x_ss.next = True

                # ~~~~ Wait half clock period for cpha=1 ~~~~
                elif state == states.wait_hclk:
                    itx.rd.next = False
                    irx.wr.next = False
                    if ena:
                        x_sck.next = not x_sck
                        state.next = states.data_in

                # ~~~~ Clock data in (and out) ~~~~
                elif state == states.data_in:
                    itx.rd.next = False
                    irx.wr.next = False
                    if ena:  # clk div
                        x_sck.next = not x_sck
                        rreg.next = concat(rreg[7:0], x_miso)
                        
                        if cso.clock_phase and bcnt == 0:
                            irx.wr.next = True
                            if itx.empty or irx.full:
                                state.next = states.end
                            else:
                                state.next = states.data_change
                        else:
                            state.next = states.data_change

                # ~~~~ Get ready for next byte out/in ~~~~
                elif state == states.data_change:
                    itx.rd.next = False
                    irx.wr.next = False
                    if ena:
                        x_sck.next = not x_sck
                        if bcnt == 0:  
                            if not cso.clock_phase:
                                irx.wr.next = True
                                
                            if itx.empty or irx.full:
                                state.next = states.end
                            else:  # more data to transfer
                                bcnt.next = 7
                                state.next = states.data_in
                                itx.rd.next = True
                                treg.next = itx.rdata
                        else:
                            treg.next = concat(treg[7:0], intbv(0)[1:])
                            bcnt.next = bcnt - 1                        
                            state.next = states.data_in

                # ~~~~ End state ~~~~
                elif state == states.end:
                    itx.rd.next = False
                    irx.wr.next = False
                    if ena:  # Wait half clock cycle go idle
                        state.next = states.idle

                # Shouldn't happen, error in logic
                else:
                    state.next = states.idle
                    assert False, "SPI Invalid State"

    @always_comb
    def rtl_fifo_sel():
        """
        The `itx` and `irx` FIFO interfaces are driven by different
        logic depending on the configuration.  This modules accesses
        the `itx` read side and drives the `irx` write side.  The
        `itx` write side is driven by the `cso` or the `fifobus` port.
        The `irx` read side is accessed by the `cso` or the `fifobus`
        port.
        """
        if cso.bypass_fifo:
            # data comes from the register file
            cso.tx_empty.next = itx.empty
            cso.tx_full.next = itx.full
            itx.wdata.next = cso.tx_byte

            cso.rx_empty.next = irx.empty
            cso.rx_full.next = irx.empty
            cso.rx_byte.next = irx.rdata

            # @todo: if cso.tx_byte write signal (written by bus) drive the
            # @todo: FIFO write signals, same if the cso.rx_byte is accessed
            itx.wr.next = cso.tx_write
            irx.rd.next = cso.rx_read

        else:
            # data comes from external FIFO bus interface
            fifobus.full.next = itx.full
            itx.wdata.next = fifobus.wdata
            itx.wr.next = fifobus.wr

            fifobus.empty.next = irx.empty
            fifobus.rdata.next = irx.rdata
            fifobus.rvld.next = irx.rvld
            irx.rd.next = fifobus.rd

        # same for all modes
        irx.wdata.next = rreg

    @always_comb
    def rtl_x_mosi():
        # @todo lsbf control signal
        x_mosi.next = treg[7]

    @always(clock.posedge)
    def rtl_spi_sigs():
        spibus.sck.next = x_sck

        if cso.loopback:
            spibus.mosi.next = False
            x_miso.next = x_mosi
        else:
            spibus.mosi.next = x_mosi
            x_miso.next = spibus.mosi

        if cso.manual_slave_select:
            spibus.ss.next = ~cso.slave_select
        else:
            if x_ss:
                spibus.ss.next = 0xFF
            else:
                spibus.ss.next = ~cso.slave_select

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
                ccfb = concat(itx.wr, itx.rd, irx.wr, irx.rd)
                if ccfb != fbidle:
                    fstr = "  :{:8d}: tx: w{} r{}, f{} e{}, rx: w{} r{} f{} e{}"
                    print(fstr.format(now(),
                        int(itx.wr), int(itx.rd), int(itx.full), int(itx.empty),
                        int(irx.wr), int(irx.rd), int(irx.full), int(irx.empty),)
                    )
                    
        @always(clock.posedge)
        def mon_tx_fifo_write():
            if itx.wr:
                print("   WRITE tx fifo {:02X}".format(int(itx.wdata)))
            if itx.rd:
                print("   READ tx fifo {:02X}".format(int(itx.rdata)))
                
        @always(clock.posedge)
        def mon_rx_fifo_write():
            if irx.wr:
                print("   WRITE rx fifo {:02X}".format(int(irx.wdata)))
                
            if irx.rd:
                print("   READ rx fifo {:02X}".format(int(irx.rdata)))

    # return the myhdl generators
    gens = instances()
    return gens

spi_controller.debug = False
spi_controller.cso = SPIControlStatus
# @todo: complete the portmap
spi_controller.portmap = dict()
