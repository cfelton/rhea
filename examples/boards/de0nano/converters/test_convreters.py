
from __future__ import print_function
from __future__ import division

from myhdl import *

from rhea.system import Clock, Reset
from rhea.utils.test import tb_clean_vcd
from de0nano_converters import de0nano_converters


def test_de0nano_converters():
    portmap = de0nano_converters.portmap
    clock = portmap['clock']
    reset = portmap['reset']

    def _bench():
        tbdut = de0nano_converters(**portmap)
        tbclk = clock.gen()

        @instance
        def tbstim():
            yield reset.pulse(40)
            # relying on the design assertions 
            for ii in range(1000):
                yield clock.posedge
            raise StopSimulation

        return tbdut, tbclk, tbstim

    vcd = tb_clean_vcd(_bench.__name__)
    traceSignals.name = vcd
    traceSignals.timescale = '1ns'
    Simulation(traceSignals(_bench)).run()


if __name__ == '__main__':
    test_de0nano_converters()
        