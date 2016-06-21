
import myhdl
from myhdl import intbv

from rhea import Constants
from rhea.system import Bit, Byte
from rhea.system import ControlStatusBase
from ..misc import assign


class ControlStatus(ControlStatusBase):
    def __init__(self):
        """ The control-status object for the SPI controller

        Attributes:
            enable: enable the SPI controller
            freeze: freeze the current state
            bypass_fifo: the write_data and read_data sink and source
              the FIFO instead of the FIFOBus
            clock_polarity:
            clock_phase:
            manual_slave_select:
            clock_divisor:

            rx_empty:
            rx_full:
            tx_empty:
            tx_full:
            tx_byte:
            rx_byte:
            tx_fifo_count:
            rx_fifo_count:

            slave_select:
            slave_select_fault:

        The following cso attributes use the pre-defined hardware types,
        these are used to give "hints" to the automated register-file
        construction.  Mark the status (read-only) signals as driven,
        then the tools know these are read-only signals.
        """
        self.enable = Bit(1)
        self.freeze = Bit(0)
        self.bypass_fifo = Bit(config=True)
        self.loopback = Bit(config=True)
        self.clock_polarity = Bit(config=True)
        self.clock_phase = Bit(config=True)
        self.manual_slave_select = Bit(0)
        self.clock_divisor = Byte(config=True)
        self.slave_select = Byte(config=True)
        self.slave_select_fault = Bit(driven=True)

        self.tx_empty = Bit()
        self.tx_full = Bit()
        self.tx_byte = Byte()
        self.tx_write = Bit()    # WriteStrobe(self.tx_byte)
        self.tx_fifo_count = Byte()

        self.rx_empty = Bit()
        self.rx_full = Bit()
        self.rx_byte = Byte()
        self.rx_read = Bit()     # ReadStrobe(self.rx_byte)
        self.rx_byte_valid = Bit()
        self.rx_fifo_count = Byte()

        super(ControlStatus, self).__init__()

    @myhdl.block
    def default_assign(self):
        cfgbits = self.get_config_bits()
        cfg = Constants(**cfgbits)

        insts = []

        # In the static configuration case only one value makes sense
        # for certain configuration signals, those are set here
        insts += [assign(self.enable, True)]
        insts += [assign(self.freeze, False)]

        for ii, k in enumerate(cfgbits):
            configsig = getattr(self, k)
            configval = getattr(cfg, k)
            assert isinstance(configval, (bool, int, intbv))
            if isinstance(configsig.val, bool):
                configval = bool(configval)
            insts += [assign(configsig, configval)]

        return myhdl.instances()

    @myhdl.block
    def instances(self):
        if self.isstatic:
            inst = self.default_assign()
        else:
            inst = []

        return inst
