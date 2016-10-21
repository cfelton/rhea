
import myhdl
from myhdl import (Signal, intbv, instance, delay, StopSimulation)

from rhea.cores.converters import adc128s022
from rhea.cores.spi import SPIBus
from rhea.system import FIFOBus
from rhea.system import Clock
from rhea.system import Reset
from rhea.system import Global
from rhea.models.converters import adc128s022_model
from rhea.utils.test import run_testbench


def test_adc128s022():
    
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=False)
    glbl = Global(clock, reset)
    fifobus = FIFOBus(width=16)
    spibus = SPIBus()
    channel = Signal(intbv(0, min=0, max=8))
    step = 3.3/7
    analog_channels = [Signal(3.3 - step*ii) for ii in range(0, 8)]
    print(analog_channels)
    assert len(analog_channels) == 8
    
    def check_empty(clock, fifo):
        for ii in range(4000):
            if not fifo.empty:
                break
            yield clock.posedge

    @myhdl.block
    def bench_adc128s022():
        tbdut = adc128s022(glbl, fifobus, spibus, channel)
        tbmdl = adc128s022_model(spibus, analog_channels,
                                 vref_pos=3.3, vref_neg=0.)
        tbclk = clock.gen()

        @instance
        def tbstim():
            sample = intbv(0)[16:]
            yield reset.pulse(33)
            yield clock.posedge
            
            # check the conversion value for each channel, should  get
            # smaller and smaller 
            for ch in range(0, 8):
                channel.next = (ch+1) % 8  # next channel
                yield check_empty(clock, fifobus)
                # should have a new sample
                if not fifobus.empty:
                    fifobus.read.next = True
                    sample[:] = fifobus.read_data
                    yield clock.posedge
                    fifobus.read.next = False
                    yield clock.posedge
                    print("sample {:1X}:{:4d}, fifobus {} \n".format(
                        int(sample[16:12]), int(sample[12:0]), str(fifobus)))
                    assert fifobus.empty 
                else:
                    print("No sample!")
                
            yield delay(100)
            raise StopSimulation
            
        return tbdut, tbmdl, tbclk, tbstim

    run_testbench(bench_adc128s022)
        
        
if __name__ == '__main__':
    test_adc128s022()
    
            
            

