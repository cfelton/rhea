
import myhdl
from myhdl import Signal, intbv, always_seq, always_comb, concat


@myhdl.block
def io_stub(clock, reset, sdi, sdo, port_inputs, port_outputs, valid):
    """ Port emulators, serial to parallel input / output

    This module is a port emulator, a single input and single output
    will be serialized into larger parallel data words (bus).

    This module is a simple module used for synthesis testing for 
    particular FPGA devices.  This module allows a bunch of inputs 
    to be tied to a couple IO (pins).  Typically this is not used
    in a functionally working implementation but a circuit valid
    and timing valid implementation to determine a rough number
    of resources required for a design.

    Arguments:
        clock: system clock
        reset: system reset
        sdi: serial-data in, this should be assigned to a pin on
            the device
        sdo: serial-data out, this should be assigned to a pin on
            the device
        port_inputs: number of inputs desired, list of same type Signals,
            output of this module
        port_outputs: number of outputs desired, list of same type Signals,
            input to this module
        valid: load new inputs, outputs valid

    Limitations
    -----------
    Each member in the `pin` and `pout` lists need to be
    the same type.


    This module is myhdl convertible
    """
    
    # verify pin and pout are lists
    pin, pout = port_inputs, port_outputs
    assert isinstance(pin, list)
    assert isinstance(pout, list)

    nin = len(pin)      # number of inputs (outputs of this module)
    nout = len(pout)    # number of outputs (inputs to this module)
    nbx = len(pin[0])   # bit lengths of the inputs
    nby = len(pout[0])  # bit lengths of the outputs

    signed = True if pin[0].min < 0 else False

    # make the input and output registers same length
    xl, yl = nin*nbx, nout*nby
    nbits = max(xl, yl)
    irei = Signal(bool(0))   # serial input registered
    oreo = Signal(bool(0))   # serial output registered

    # the large shift registers
    ireg = [Signal(intbv(0)[nbx:]) for _ in range(nin)]
    oreg = [Signal(intbv(0)[nby:]) for _ in range(nout)]
    # ireg = Signal(intbv(0)[nbits:])
    # oreg = Signal(intbv(0)[nbits:])

    # the number of shifts ...
    scnt = Signal(intbv(0, min=0, max=nbits+1))
    imax = scnt.max-1

    # @always_seq(clock.posedge, reset=reset)
    # def beh_shift_regs():
    #
    #     # extra register on the inputs and outputs
    #     irei.next = sdi
    #     oreo.next = oreg[nbits-1]
    #     sdo.next = oreo
    #
    #     ireg.next = concat(ireg[nbits-2:0], irei)
    #
    #     if scnt >= imax:
    #         valid.next = True

    lastoreg = oreg[nout-1]

    @always_seq(clock.posedge, reset=reset)
    def beh_shifts():
        # extra registers on the serial inputs and outputs
        irei.next = sdi
        oreo.next = lastoreg[nby-1]
        sdo.next = oreo

        # build the large shift register out of the logical
        # list of signals (array)
        for ii in range(nin):
            tmp1 = ireg[ii]
            if ii == 0:
                ireg[ii].next = concat(tmp1[nbx-1:0], irei)
            else:
                tmp0 = ireg[ii-1]
                ireg[ii].next = concat(tmp1[nbx-1:0], tmp0[nbx-1])

        if scnt == imax:
            valid.next = True
            scnt.next = 0
            for oo in range(nout):
                oreg[oo].next = pout[oo]
        else:
            valid.next = False
            scnt.next = scnt + 1
            for oo in range(nout):
                tmp2 = oreg[oo]
                if oo == 0:
                    oreg[oo].next = concat(tmp2[nby-1:0],  tmp2[nby-1])
                else:
                    tmp3 = oreg[oo-1]
                    oreg[oo].next = concat(tmp2[nby-1:0], tmp3[nby-1])

    @always_comb
    def beh_assign():
        for ii in range(nin):
            pin[ii].next = ireg[ii]

    return beh_shifts, beh_assign

