

from myhdl import *

def m_serio(clock, reset, sdi, sdo, pin, pout):
    """ serial-in, serial-out
    This module is a simple module used for synthesis testing for 
    particular FPGA devices.  This module allows a bunch of inputs 
    to be tied to a couple IO (pins).  Typically this is not used
    in a functionally working implementation but a circuit valid
    and timing valid implementation to determine a rought number 
    of resources required for a design.

    Ports
    -----
      clock : 
      reset : 
      sdi : serial-data in, this should be assigned to a pin on
            the device
      sdo : serial-data out, this should be assigned to a pin on
            the device
      pdin : number of inputs desired
      pdout : number of outputs desired

    Parameters
      None

    Limitations each member in the pin and pout lists need to be
    the same type.
    ----------
    """
    
    # verify pin and pout are lists
    assert isinstance(pin, list)
    assert isinstance(pout, list)

    Nin = len(pin)      # number of inputs (outputs of this module)
    Nout = len(pout)    # number of outputs (inputs to this module)
    nbx = len(pin[0])   # bit lengths of the inputs
    nby = len(pout[0])  # bit lengths of the outputs

    Signed = True if pin[0].min < 0 else False

    # make the input and output registers same length
    xl,yl = Nin*nbx, Nout*nby
    Nbits = max(xl, yl)
    irei = Signal(bool(0))
    oreo = Signal(bool(0))
    ireg = [Signal(intbv(0)[nbx:]) for _ in range(Nin)]
    oreg = [Signal(intbv(0)[nby:]) for _ in range(Nin)] 

    scnt = Signal(intbv(0, min=0, max=Nbits+1))
    imax = scnt.max-1


    @always_seq(clock.posedge, reset=reset)
    def rtl_shifts():
        irei.next = sdi
        oreo.next = oreg[Nout-1][nby-1]
        sdo.next = oreo

        # build the large shift register out of the logical
        # list of signals (array)
        for ii in range(Nin):
            if ii == 0:
                ireg[ii].next = concat(ireg[ii][nbx-1:0], irei)
            else:
                ireg[ii].next = concat(ireg[ii][nbx-1:0], ireg[ii-1][nbx-1])

        if scnt == imax:
            scnt.next = 0
            for oo in range(Nout):
                oreg[oo].next = pout[oo]
        else:
            scnt.next = scnt + 1
            for oo in range(Nout):
                if oo == 0:
                    oreg[oo].next = oreg[oo] << 1
                else:
                    oreg[oo].next = concat(oreg[oo][nby-1:0], oreg[oo-1][nby-1])

    @always_comb
    def rtl_assign():
        for ii in range(Nin):
            pin[ii].next = ireg[ii]

    return rtl_shifts, rtl_assign

