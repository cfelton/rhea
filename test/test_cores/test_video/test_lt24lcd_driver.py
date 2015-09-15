
from __future__ import absolute_import

# @todo: fix, only import what is needed
from myhdl import *

from rhea.system import Global, Clock, Reset
from rhea.cores.video.lcd import LT24Interface
from rhea.cores.video.lcd._lt24 import lt24lcd_driver 
from rhea.utils.test import tb_clean_vcd


def tb_lt24lcd_driver(args):
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    lcd = LT24Interface()
    
    cmd = Signal(intbv(0)[8:])
    datalen = Signal(intbv(0, min=0, max=lcd.number_of_pixels))
    data = Signal(intbv(0)[16:])
    datasent = Signal(bool(0))
    cmd_in_progress = Signal(bool(0))
    
    def _bench():
        tbdut = lt24lcd_driver(glbl, lcd, cmd, datalen, data,
                               datasent, cmd_in_progress, 
                               maxlen=lcd.number_of_pixels)
                               
        tbclk = clock.gen()
        
        @instance
        def tbstim():
            yield reset.pulse(111)
            yield clock.posedge
            
            # send a column write command
            cmd.next = 0x2A
            bytes = [0, 0, 0, 239]
            data.next = bytes[0]
            datalen.next = 4 
            
            for ii in range(4):
                yield datasent.posedge
                data.next = bytes[ii+1] if ii < 3 else 0
                
            raise StopSimulation
            
        return tbdut, tbclk, tbstim
            
    vcd = tb_clean_vcd(tb_lt24lcd_driver.__name__)
    traceSignals.name = vcd
    print("start simulation")
    Simulation(traceSignals(_bench)).run()
    print("simulation done")
    
    
if __name__ == '__main__':
    tb_lt24lcd_driver(None)
            
        