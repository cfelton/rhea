
from myhdl import *

from mn.cores import m_serio

def m_serio_ex(clock, reset, sdi, sdo, Np=8):
    
    pin = [Signal(intbv(0)[8:]) for _ in range(Np)]
    pout = [Signal(intbv(0)[8:]) for _ in range(Np)]

    gserio = m_serio(clock, reset, sdi, sdo, pin, pout)

    @always_seq(clock.posedge, reset=reset)
    def rtl():
        for ii in range(Np):
            pout[ii].next = pin[ii]

    return gserio, rtl

clock = Signal(bool(0))
reset = ResetSignal(0, 0, False)
sdi = Signal(bool(0))
sdo = Signal(bool(0))
 

toVerilog(m_serio_ex, clock, reset, sdi, sdo)
toVHDL(m_serio_ex, clock, reset, sdi, sdo)

