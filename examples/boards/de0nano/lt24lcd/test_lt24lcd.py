
from __future__ import print_function, division
from __future__ import division

import myhdl
from myhdl import instance, StopSimulation
from rhea.utils.test import run_testbench
from de0nano_lt24lcd import de0nano_lt24lcd


def test_de0nano_lt24lcd():
    portmap = de0nano_lt24lcd.portmap
    clock = portmap['clock']
    reset = portmap['reset']

    @myhdl.block
    def bench():
        tbdut = de0nano_lt24lcd(**portmap)
        tbclk = clock.gen()

        @instance
        def tbstim():
            yield reset.pulse(40)
            # relying on the design assertions 
            for ii in range(1000):
                yield clock.posedge
            raise StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(bench)


if __name__ == '__main__':
    test_de0nano_lt24lcd()
