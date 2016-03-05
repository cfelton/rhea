
from myhdl import Signal, intbv, SignalType

# this is the fifo interfaces


class fifobus(object):
    """
    This object defines the signals needed to interface with the
    FIFO cores.  If used in the "mn" pakcage use the FIFOBus defined
    in "system"
    """
    def __init__(self, width=8, size=128):
        self.clear = Signal(bool(0))           # fifo clear
        self.wclk = None                       # write side clock
        self.wr = Signal(bool(0))              # write strobe to fifo
        self.wdata = Signal(intbv(0)[width:])  # fifo data in
        
        self.rclk = None                       # read side clock
        self.rd = Signal(bool(0))              # fifo read strobe
        self.rdata = Signal(intbv(0)[width:])  # fifo data out
        self.empty = Signal(bool(0))           # fifo empty
        self.full = Signal(bool(0))            # fifo full
        self.count = Signal(intbv(0, min=0, max=size))


def _fifo_intf_dump():
    """
    dump a ton of information about the expected bus interface
    """
    pass


def check_fifo_intf(fbus):
    """
    In the MN project, typically the FIFOBus is used to created 
    a FIFO.   It is plausible for a separate interface to be 
    defined and passed.  This function will check the inteface
    for the correct signals (attributes) and try to provide useful
    feedback what is missing / inconsistent in the interface.
    """
    try:
        assert isinstance(fbus.write, SignalType)
        assert isinstance(fbus.write_data, SignalType)

        assert isinstance(fbus.read, SignalType)
        assert isinstance(fbus.read_data, SignalType)

        assert len(fbus.write_data) == len(fbus.read_data)
        # @todo: the above is a small start ... to be continued ...
    except AssertionError as err:
        _fifo_intf_dump()
        raise err
    except Exception as err:
        raise err
