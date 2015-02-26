
from myhdl import *
from ...system import Clock

# @todo move to separate file 
class SDRAM(object):
    # timing fields, all in ns
    freq = 100e6
    timing = { # all timing parameters in ns
        'init' : 200000.0,   # min init interval
        'ras'  : 45.0,       # min interval between active precharge commands
        'rcd'  : 20.0,       # min interval between active R/W commands
        'ref'  : 64000000.0, # max refresh interval
        'rfc'  : 65.0,       # refresh operaiton duration
        'rp'   : 20.0,       # min precharge command duration
        'xsr'  : 75.0,       # exit self-refresh time
    }

    addr_width = 12   # SDRAM address width
    data_width = 16   # SDRAM data width

    def __init__(self, clock, Nrows=4096, Ncols=512, Hwidth=23):
        self.freq = extract_freq(clock, self.freq)
        self.Nrows = Nrows   # number of rows in the SDRAM array
        self.Ncols = Ncols   # number of columns in the SDRAM array
        self.Hw = Hwidth     # host-side address width
        self.Sw = addr_width # SDRAM-side address width

        # internal signals
        self.lock = Signal(bool(0))
        self.rd = Signal(bool(0))
        self.wr = Signal(bool(0))
        # a_op_begyn, op_begun, rd_pending
        self.done = Signal(bool(0))
        self.addr = Signal(intbv(0)[Hwidth:0])
        self.wdata = Signal(intbv(0)[self.data_width:0])
        self.rdata = Signal(intbv(0)[self.data_width:0])
        self.status = Signal(intbv(0)[4:])

        # externl SDRAM signals
        self.sd_cke = Signal(bool(0))
        self.sd_ce = Signal(bool(0))
        self.sd_ras =  Signal(bool(0))
        self.sd_we = Signal(bool(0))
        self.sd_bs = Signal(intbv(0)[2:])
        self.sd_addr = Signal(intbv(0)[self.addr_width:])
        self.sd_wdata = Signal(intbv(0)[self.data_width:])
        self.sd_rdata = Signal(intbv(0)[self.data_width:])
        self.sd_dqmh = Signal(bool(0))  # enable upper-byte of SDRAM
        self.sd_dqml = Signal(bool(0))  # enable lower-byte of SDRAM

        cycles = {}
        for k,v in timing.iteritems():
            cycles[k] = v * (self.freq / 1e9)
 
        # need to add these to the namespace, currently the 
        # myhdl converter will not extract the constants from 
        # a data-structure (e.g. dict).
        for k,v in cycles.iteritems():
            self.__dict__['cyc_'+k] = v


class Winboad_W9812G6JH_75(SDRAM):
    
    freq = 10e6  # clock frequency in Hz
    timing = { # all timing parameters in ns
        'init' : 200000.0,   # min init interval
        'ras'  : 45.0,       # min interval between active precharge commands
        'rcd'  : 20.0,       # min interval between active R/W commands
        'ref'  : 64000000.0, # max refresh interval
        'rfc'  : 65.0,       # refresh operaiton duration
        'rp'   : 20.0,       # min precharge command duration
        'xsr'  : 75.0,       # exit self-refresh time
    }
    
    addr_width = 12   # SDRAM address width
    data_width = 16   # SDRAM data width

    

def m_sdram(clock, reset, mmbus, extram, refresh=True):
    """ SDRAM controller
    This module is an SDRAM controller to interface and control
    SDRAM modules.  This module contains a state-machine that 
    controls the different SDRAM modes including refresh etc.

    This module provides the translation from a flat memory-mapped
    bus (e.g. Wishbone, Avalon, AXI, etc.) to the SDRAM interface.

    This SDRAM controller is a port of the Xess SDRAM controller
    for the Xula boards.
    https://github.com/xesscorp/XuLA/blob/master/FPGA/XuLA_lib/SdramCntl.vhd
    """

    States = enum('INITWAIT', 'INITPCHG', 'INITSETMODE', 'INITRFSH', 
                  'RW', 'ACTIVATE', 'REFRESHROW', 'SELFREFRESH')

    Commands = enum('nop', 'active', 'read', 'write', 
                    'pchg', 'mode', 'rfsh') 
                    encoding='binary')
    cmdlut = (intbv('011100')[5:], 
              intbv('001100')[5:],
              intbv('010100')[5:],
              intbv('010000')[5:],
              intbv('001000')[5:],
              intbv('000000')[5:],
              intbv('000100')[5:])


    timer = Signal(intbv(0, min=0, max=sdram.Tinit))
    ras_timer = Signal(intbv(0, min=0, max=sdram.cycles['ras']))
    wr_timer = Signal(intbv(0, min=0, max=sdram.cycles['wr']))
    
    sdram = extram
    sdram.cmd = Signal(intbv(0)[5:])

    @always_seq(clock.posedge, reset=reset)
    def rtl_sdram_controller():
        
        # this is one big state-machine but ...
        if state == States.INITWAIT:
            if sdram.lock:
                timer.next = sdram.cyc_init
                state.next = States.initpchg
            else:
                sdram.cke.next = False
            status.next = 1

        elif state == States.INITPCHG:
            sdram.cmd.next = Commands.PCHG
            sdram.addr[CMDBITS] = Commands.ALL_BANKS
            timer.next = sdram.cycles

    return rtl_sdram_controller


# default portmap
clock = Clock(0, frequency=100e6)
m_sdram.portmap = {
    'clock': clock, 
    'reset': ResetSignal(0, active=0, async=False),
    'sdram': SDRAM(clock)
}


