
from __future__ import absolute_import

import myhdl
from myhdl import intbv, enum, Signal, ResetSignal, always_seq

from rhea import Clock
from .sdram_intf import SDRAMInterface


@myhdl.block
def sdram_sdr_controller(clock, reset, ibus, extram, refresh=True):
    """ SDRAM controller
    This module is an SDRAM controller to interface and control
    SDRAM modules.  This module contains a state-machine that 
    controls the different SDRAM modes including refresh etc.

    This module provides the translation from a flat memory-mapped
    bus (e.g. Wishbone, Avalon, AXI, etc.) to the SDRAM interface.
    Also intended to support memory-mapped and streaming (FIFO
    mode).  In streaming / FIFO mode the external memory acts as
    one large FIFO.  The SDRAM controller type is determine by
    the internal interface (ibus) passed.

    This SDRAM controller is a port of the Xess SDRAM controller
    for the Xula boards.
    https://github.com/xesscorp/XuLA/blob/master/FPGA/XuLA_lib/SdramCntl.vhd
    """

    States = enum('INITWAIT', 'INITPCHG', 'INITSETMODE', 'INITRFSH', 
                  'RW', 'ACTIVATE', 'REFRESHROW', 'SELFREFRESH')

    # @todo: changed to named constants
    Commands = enum('nop', 'active', 'read', 'write', 
                    'pchg', 'mode', 'rfsh',
                    encoding='binary')

    cmdlut = (intbv('011100')[5:], 
              intbv('001100')[5:],
              intbv('010100')[5:],
              intbv('010000')[5:],
              intbv('001000')[5:],
              intbv('000000')[5:],
              intbv('000100')[5:])

    sdram = extram
    sdram.cmd = Signal(intbv(0)[5:])

    timer = Signal(intbv(0, min=0, max=sdram.cyc_init))
    ras_timer = Signal(intbv(0, min=0, max=sdram.cyc_ras))
    wr_timer = Signal(intbv(0, min=0, max=sdram.cyc_wr))
    
    state = Signal(States.INITWAIT)

    @always_seq(clock.posedge, reset=reset)
    def rtl_sdram_controller():
        
        # this is one big state-machine but ...
        if state == States.INITWAIT:
            if sdram.lock:
                timer.next = sdram.cyc_init
                state.next = States.initpchg
            else:
                sdram.sd_cke.next = False
            sdram.status.next = 1

        elif state == States.INITPCHG:
            sdram.cmd.next = Commands.PCHG
            # sdram.addr[CMDBITS] = Commands.ALL_BANKS
            timer.next = sdram.cycles

    return rtl_sdram_controller


# default portmap
clock = Clock(0, frequency=100e6)
sdram_sdr_controller.portmap = {
    'clock': clock, 
    'reset': ResetSignal(0, active=0, async=False),
    'ibus': None,
    'extmem': SDRAMInterface(clock)
}


