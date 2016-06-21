
import argparse

import myhdl
from myhdl import (Signal, intbv, always, always_comb, instances,
                   concat, instance, delay, StopSimulation)

from rhea.system import Global, Clock, Reset
from rhea.vendor import ClockManagement
from rhea.vendor import device_clock_mgmt
from rhea.utils.test import run_testbench, tb_args, tb_default_args
import rhea.build as build
from rhea.build.boards import get_board

flow = None


@myhdl.block
def de0nano_soc_device_prims(clock, reset, led):
    
    clkmgmt = ClockManagement(clock, reset,
                              output_frequencies=(100e6, 200e6),
                              vendor='altera')

    pll_inst = device_clock_mgmt(clkmgmt)
    maxcnt0 = int(clock.frequency)
    maxcnt1 = int(clkmgmt.clocks[0].frequency)
    maxcnt2 = int(clkmgmt.clocks[1].frequency)

    cnt0, cnt1, cnt2 = [Signal(intbv(0, min=0, max=mx)) 
                        for mx in (maxcnt0, maxcnt1, maxcnt2)]
    led0, led1, led2 = [Signal(bool(0)) for _ in range(3)]

    clock1, clock2 = clkmgmt.clocks

    @always(clock.posedge)
    def beh_toggle0():
        clkmgmt.enable.next = True
        if cnt0 >= maxcnt0-1:
            led0.next = not led0
            cnt0.next = 0
        else:
            cnt0.next = cnt0 + 1

    @always(clock1.posedge)
    def beh_toggle1():
        if cnt1 >= maxcnt1-1:
            led1.next = not led1
            cnt1.next = 0
        else:
            cnt1.next = cnt1 + 1            

    @always(clock2.posedge)
    def beh_toggle2():
        if cnt2 >= maxcnt2-1:
            led2.next = not led2
            cnt2.next = 0
        else:
            cnt2.next = cnt2 + 1

    @always_comb
    def beh_assign():
        led.next = concat(False, led2, led1, led0)

    return instances()
        

def test_devprim(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=True)
    led = Signal(intbv(0))

    @myhdl.block
    def bench_devprim():
        tbdut = de0nano_soc_device_prims(clock, reset, led)
        tbclk = clock.gen(hticks=10000)
        
        @instance
        def tbstim():
            print("start simulation")
            yield reset.pulse(36)
            yield clock.posedge
            for ii in range(40):
                yield delay(11111)
            print("end simulation")
            raise StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(bench_devprim, args=args)

    
def build_bitfile():
    global flow
    brd = get_board('de0nano_soc')
    flow = build.flow.Quartus(brd=brd, top=de0nano_soc_device_prims)
    flow.run(use='verilog')


def program():
    global flow
    if flow is not None:
        pass
    else:
        brd = get_board('de0nano_soc')
        flow = build.flow.Quartus(brd=brd, 
                                  top=de0nano_soc_device_prims)
        
    print("program board")
    flow.program()
    print("programming finished")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action='store_true', default=False)
    parser.add_argument("--program", action='store_true', default=False)
    parser.add_argument("--trace", action='store_true', default=False)
    args = parser.parse_args()

    # run a simple tests to check all is ok
    test_devprim(args=args)

    if args.build:
        build_bitfile()

    if args.program:
        program()
    

if __name__ == '__main__':
    main()
