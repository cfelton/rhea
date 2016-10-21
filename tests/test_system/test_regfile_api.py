
import myhdl
from myhdl import Signal

from rhea import Global
from rhea.system import RegisterFile, Register
from rhea.system import Barebone
from rhea.cores.misc import led_blinker
from rhea.cores.misc import button_controller, button_debounce


def create_regfile():
    # create a register file
    regfile = RegisterFile()

    # create a status register and add it to the register file
    reg = Register('status', width=8, access='ro', default=0)
    regfile.add_register(reg)

    # create a control register with named bits and add
    reg = Register('control', width=8, access='rw', default=1)
    reg.add_namedbits('enable', bits=0, comment="enable the component")
    reg.add_namedbits('pause', bits=1, comment="pause current operation")
    reg.add_namedbits('mode', bits=(4, 2), comment="select mode")
    regfile.add_register(reg)

    return regfile


def test_simple():
    regfile = create_regfile()
    for name, reg in regfile.registers.items():
        print("  {0:8} {1:04X} {2:04X}".format(name, reg.addr, int(reg)))
    print("")


@myhdl.block
def led_blinker_top(clock, reset, leds, buttons):

    glbl = Global(clock, reset)
    csrbus = Barebone()
    dbtns = Signal(buttons.val)

    led_inst = led_blinker(glbl, csrbus, leds)
    dbn_inst = button_debounce(glbl, buttons, dbtns)
    btn_inst = button_controller(glbl, csrbus, dbtns)

    # above all the components have been added, now build the
    # register file (figures out addresses, etc) and then get
    # the memory-mapped bus interconnect
    csrbus.regfile_build()
    bus_inst = csrbus.interconnect()

    return myhdl.instances()


def test_led_blinker():
    pass


if __name__ == '__main__':
    test_simple()
