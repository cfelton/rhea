
from myhdl import Signal, intbv, always, always_comb, instances

from rhea.system import Global
from rhea.vendor import PLLInterface
from rhea.vendor import device_pll
import rhea.build as build
from rhea.build.boards import get_board


def de0nano_soc_device_prims(clock, reset, led):
    
    pllintf = PLLInterface(clock, reset,
                           output_frequencies=(100e6, 200e6))

    pll_inst = device
    maxcnt0 = int(clock.frequency)
    maxcnt1 = int(pllintf.clocks[0].frequency)
    maxcnt2 = int(pllintf.clocks[1].frequency)

    @always(clock.posedge)
    def beh_toggle0():
        if cnt0 >= maxcnt0-1:
            led0.next = not led0
            cnt0.next = 0
        else:
            cnt0.next = cnt0 + 1

    @always(pllintf.clocks[0].posedge)
    def beh_toggle1():
        if cnt1 >= maxcnt1-1:
            led1.next = not led1
            cnt1.next = 0
        else:
            cnt1.next = cnt1 + 1            

    @always(pllintf.clocks[1].posedge)
    def beh_toggle2():
        if cnt2 >= maxcnt2-1:
            led2.next = not led2
            cnt2.next = 0
        else:
            cnt2.next = cn2 + 1

    @always_comb
    def beh_assign():
        led.next = concat(False, led2, led1, led0)

    return instances()
        

def build_bitfile():
    brd = get_board('de0nano_soc')
    flow = build.flow.Quartus(brd=brd, top=de0nano_soc_device_prims)
    flow.run(use='verilog')


if __name__ == '__main__':
    build_bitfile()