

from myhdl import Signal

from rhea.system import RegisterFile, Register
from rhea.system import Clock, Reset, Global
from rhea.system import Barebone
from rhea.cores.misc import led_stroby, led_dance, led_count
from rhea.cores.misc import button_controller, button_debounce


def create_regfile():
    # create a register file
    regfile = RegisterFile()

    # create a status register and add it to the register file
    reg = Register('status', width=8, access='ro', default=0)
    regfile.add_register(reg)

    # create a control register with named bits and add
    reg = Register('control', width=8, access='rw', default=1)
    reg.add_named_bits('enable', bits=0, comment="enable the compoent")
    reg.add_named_bits('pause', bits=1, comment="pause current operation")
    reg.add_named_bits('mode', bits=(4, 2), comment="select mode")
    regfile.add_register(reg)

    return regfile


def test_simple():
    regfile = create_regfile()
    for name, reg in regfile.registers.items():
        print("  {0:8} {1:04X} {2:04X}".format(name, reg.addr, int(reg)))
    print("")


def led_blinker(glbl, csrbus, leds):
    regfile = create_regfile()
    gregbus = csrbus.add(glbl, regfile, 'led')

    # instantiate the module to interface to the regfile
    led_modules = (led_stroby, led_dance, led_count)
    mleds = [Signal(leds.val) for _ in led_modules]
    mods = []
    for ii, ledmod in enumerate(led_modules):
        mods += ledmod(glbl, mleds[ii])

    return gregbus, mods


def led_blinker_top(clock, reset, leds, buttons):

    glbl = Global(clock, reset)
    csrbus = Barebone()
    dbtns = Signal(buttons.val)

    gled = led_blinker(glbl, csrbus, leds)
    gdbn = button_debounce(glbl, buttons, dbtns)
    gbtn = button_controller(glbl, csrbus, dbtns)

    # above all the components have been added, now build the
    # register file (figures out addresses, etc) and then get
    # the memory-mapped bus interconnect
    csrbus.regfile_build()
    gx = csrbus.interconnect()

    return gled, gdbn, gbtn, gx

def test_led_blinker():
    pass


if __name__ == '__main__':
    test_simple()
