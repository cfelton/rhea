
from __future__ import print_function

from myhdl import *

from btn_led_mm import m_btn_led_mm

from rhea.system import Clock
from rhea.system import Reset
from rhea.utils.test import tb_clean_vcd


def test_btn_led():

    clock = Clock(0, frequency=500e3)
    reset = Reset(0, active=0, async=False)
    leds = Signal(intbv(0)[8:])
    btns = Signal(intbv(0)[4:])

    def _test():

        # bus_type = ('A', 'B', 'W', 'X') # avalon, barebone, wishbon, AXI
        tbdut = m_btn_led_mm(clock, reset, leds, btns, bus_type='A')

        def dumpg(glist):
            for gg in glist:
                if isinstance(gg, (list,tuple)):
                    dumpg(gg)
                elif gg is not None:
                    print("{:16}:  {}".format(gg.func.func_name, 
                                              gg.func.func_code.co_filename))
        dumpg(tbdut)

        tbclk = clock.gen()

        @instance
        def tbstim():
            reset.next = reset.active
            yield delay(10)
            reset.next = not reset.active
            yield clock.posedge

            #assert leds == 0
            
            for ii in range(3):
                # simulate a button press
                btns.next = 1 << ii
                yield delay(12)
                btns.next = 0

                for cc in range(8):
                    yield clock.posedge
                    
                # @todo: a more interesting check
                #assert leds != 0
            yield delay(100)

            raise StopSimulation

        return tbdut, tbclk, tbstim

    tb_clean_vcd(_test.func_name)
    Simulation(traceSignals(_test)).run()
    #Simulation(_test()).run()
    # currently an error when converting to both at once,
    # only convert to one at a time.
    toVerilog(m_btn_led_mm, clock, reset, leds, btns)
    #toVHDL(m_btn_led_mm, clock, reset, leds, btns)


if __name__ == '__main__':
    test_btn_led()
