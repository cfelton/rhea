

from rhea.system import RegisterFile, Register


def test_simple():
    # create a registrer file
    regfile = RegisterFile()

    # create a status register and add it to the register file
    reg = Register('status', width=8, access='ro', default=0)
    regfile.add_register(reg)

    # create a control register with named bits and add
    reg = Register('control', width=8, access='rw', default=1)
    reg.add_named_bits('enable', bits=0, comment="enable the compoent")
    reg.add_named_bits('pause', bits=1, comment="pause current operation")
    reg.add_named_bits('mode', bits=(4,2), comment="select mode")
    regfile.add_register(reg)

    for name, reg in regfile.registers.items():
        print("  {0:8} {1:04X} {2:04X}".format(name, reg.addr, int(reg)))
    print("")


if __name__ == '__main__':
    test_simple()