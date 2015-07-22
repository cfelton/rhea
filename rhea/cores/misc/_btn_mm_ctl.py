
from myhdl import *

from _btn_debounce import m_btn_debounce

def m_btn_mm_ctl(glbl, regbus, btns, led_addr=0x8240):
    """
    """

    clock, reset = glbl.clock, glbl.reset
    dbtns = Signal(intbv(0)[len(btns):])

    # simple interface to control (invoke) the controller
    ctl = regbus.get_controller_intf()

    # debounce the buttons
    gbtn = m_btn_debounce(glbl, btns, dbtns)

    # use the basic controller defined in the memmap modules
    # this basic controller is very simple, a write strobe 
    # will start a write cycle and a read strobe a read cycle.
    gctl = regbus.m_controller_basic(ctl)


    # @todo: finish, can't use the write's like they are
    #    but I need a bus agnostic method to read/write
    #    different buses.
    @always_seq(clock.posedge, reset=reset)
    def rtl():
        # default values
        ctl.write.next = False
        ctl.read.next = False
        ctl.addr.next = led_addr

        if ctl.done:
            if btns != 0:
                ctl.write.next = True

            if dbtns[0]:
                ctl.wdata.next = 1
            elif dbtns[1]:
                ctl.wdata.next = 2
            elif dbtns[2]:
                ctl.wdata.next = 3
            elif dbtns[3]:
                ctl.wdata.next = 4


    return gbtn, gctl, rtl