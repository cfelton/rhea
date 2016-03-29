
from myhdl import Signal, always_comb
from rhea.system import Constants
from rhea.system import Bit, Byte
from rhea.system import ControlStatusBase, assign_config


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
            slave_select_fault

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

    def default_assign(self):
        cfgbits = self.get_config_bits()
        cfg = Constants(**cfgbits)
        keep = Signal(bool(0))

        @always_comb
        def beh_assign():
            """
            In the static configuration case only one value makes sense
            for certain configuration signals, those are set here
            """
            self.enable.next = True if keep else True
            self.freeze.next = False

        gas = [None for _ in cfgbits]
        for ii, k in enumerate(cfgbits):
            gas[ii] = assign_config(getattr(self, k), getattr(cfg, k))

        return beh_assign, gas

    def get_generators(self):
        gens = []
        if self.isstatic:
            gens.append(self.default_assign())

        return gens
