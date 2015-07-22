
from myhdl import *
from ...utils import extract_freq

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
        'wr'   : 55,         # @todo ...
    }

    addr_width = 12   # SDRAM address width
    data_width = 16   # SDRAM data width

    def __init__(self, clock, Nrows=4096, Ncols=512, Hwidth=23):
        self.freq = extract_freq(clock, self.freq)
        self.Nrows = Nrows   # number of rows in the SDRAM array
        self.Ncols = Ncols   # number of columns in the SDRAM array
        self.Hw = Hwidth     # host-side address width
        self.Sw = self.addr_width # SDRAM-side address width

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
        for k,v in self.timing.iteritems():
            cycles[k] = v * (self.freq / 1e9)
 
        # need to add these to the namespace, currently the 
        # myhdl converter will not extract the constants from 
        # a data-structure (e.g. dict).
        for k,v in cycles.iteritems():
            self.__dict__['cyc_'+k] = v

        self.cycles = 5  # @todo: incorrect, needs to be fixed
