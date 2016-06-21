
import myhdl


@myhdl.block
def fifo_tester(glbl, fifobus, finished, error, fifosize=16):
    """Embeddable FIFO tester.
    This is an embeddable FIFO tester.  The block is used to test
    the various FIFO implementations in hardware.  The tester will
    test single, bursts, and streams of data into the FIFO.  This
    is intended to be used on various platforms with a LED to
    indicate if the test passed or failed.

    (arguments == ports)
    Arguments:
        glbl (Global):
        fifobus (FIFOBus):
        finished (SignalType):
        error (SignalType):

    Parameters:
        fifosize: the size of the FIFO being tested

    """

    return myhdl.instances()
