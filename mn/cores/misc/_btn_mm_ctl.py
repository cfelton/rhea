
from myhdl import *

def m_btn_mm_ctl(glbl, regbus, btns, led_addr=0x8240):
    """
    """

    clock,reset = glbl.clock, glbl.reset
    dbnts = Signal(intbv(0)[len(btns):])
    gbtn = m_btn_debounce(glbl, bnts, dbnts)

    # use the basic controller defined in the memmap modules
    gctl = regbus.m_controller_basic(glbl, write, read, done,
                                     addr, wdata, rdata)

    # @todo: finish, can't use the write's like they are
    #    but I need a bus agnostic method to read/write
    #    different buses.
    @always_seq(clock.posedge, reset=reset)
    def rtl():
        write.next = False
        read.next = False
        addr.next = led_addr

        if done:
            if btns != 0:
                write.next = True

            if dbtns[0]:
                wdata.next = 1
            elif dbtns[1]:
                wdata.next = 2
            elif dbtns[2]:
                wdata.next = 3
            elif dbtns[3]:
                wdata.next = 4

    return gbtn, gctl, rtl