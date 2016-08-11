
import myhdl
from myhdl import Signal, intbv, always_seq

from . import button_debounce
from rhea.cores.memmap import controller_basic


@myhdl.block
def button_controller(glbl, regbus, btns, led_addr=0x240):
    """ Generate bus cycles from a button input
    This is a nonsensical module that creates memory-mapped
    bus cycles from a button press.  It is used in simple
    examples and demonstrations.
    """

    clock, reset = glbl.clock, glbl.reset
    dbtns = Signal(intbv(0)[len(btns):])
    led_addr = intbv(led_addr)[16:]

    # simple interface to control (invoke) the controller
    ctl = regbus.get_generic()

    # debounce the buttons
    btn_inst = button_debounce(glbl, btns, dbtns)

    # use the basic controller defined in the memmap modules
    # this basic controller is very simple, a write strobe 
    # will start a write cycle and a read strobe a read cycle.
    ctl_inst = controller_basic(ctl, regbus)

    # @todo: finish, can't use the write's like they are
    #    but I need a bus agnostic method to read/write
    #    different buses.
    @always_seq(clock.posedge, reset=reset)
    def beh():
        # default values
        ctl.write.next = False
        ctl.read.next = False
        ctl.per_addr.next = led_addr[16:8]
        ctl.mem_addr.next = led_addr[8:0]

        if ctl.done:
            if btns != 0:
                ctl.write.next = True

            if dbtns[0]:
                ctl.write_data.next = 1
            elif dbtns[1]:
                ctl.write_data.next = 2
            elif dbtns[2]:
                ctl.write_data.next = 3
            elif dbtns[3]:
                ctl.write_data.next = 4

    return myhdl.instances()
