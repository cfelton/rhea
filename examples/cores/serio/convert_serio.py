
import myhdl
from myhdl import Signal, ResetSignal, intbv, always_seq
from rhea.cores.misc import io_stub


@myhdl.block
def serio_ex(clock, reset, sdi, sdo, Np=8):
    
    pin = [Signal(intbv(0)[8:]) for _ in range(Np)]
    pout = [Signal(intbv(0)[8:]) for _ in range(Np)]

    io_inst = io_stub(clock, reset, sdi, sdo, pin, pout)

    @always_seq(clock.posedge, reset=reset)
    def beh():
        for ii in range(Np):
            pout[ii].next = pin[ii]

    return myhdl.instances()


def convert():
    clock = Signal(bool(0))
    reset = ResetSignal(0, 0, False)
    sdi = Signal(bool(0))
    sdo = Signal(bool(0))

    inst = serio_ex(clock, reset, sdi, sdo)
    inst.convert(hdl='Verilog', directory='output')

