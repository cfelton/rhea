#
# Copyright (c) 2006-2015 Christopher L. Felton
# See the licence file in the top directory
#

from __future__ import absolute_import, division

from math import ceil

import myhdl
from myhdl import Signal, intbv, enum, always_seq, concat

from rhea.system import FIFOBus
from ..spi import SPIBus
from ..fifo import fifo_fast
from ..misc import assign


@myhdl.block
def adc128s022(glbl, fifobus, spibus, channel):
    """An interface to the ADC 128s022

    Arguments:
        glbl: global interface, clock, reset, enable, etc.
        fifobus: FIFO interface
        channel: channel to read
    """
    assert isinstance(fifobus, FIFOBus)
    assert isinstance(spibus, SPIBus)

    # local references
    clock, reset = glbl.clock, glbl.reset 
    # use the signals names in the datasheet, datashee names are 
    # from the device perspective, swapped here
    sclk, dout, din, csn = spibus()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # get a FIFO to put the samples in, each sample is 12 bits 
    # the upper 4 bits contain the channel that was sampled
    assert len(fifobus.write_data) == 16 
    assert len(fifobus.read_data) == 16 
    sample = Signal(intbv(0)[12:])
    
    fifo_inst = fifo_fast(glbl, fifobus, size=16)
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # generate the sclk frequency, the clock needs to 
    # be between 1MHz and 3.2MHz.  To read all samples 
    # at the max rate 16*200e3 = 3.2MHz (200 kS/s)
    # the clock directly controls the conversion process
    max_frequency = 3.2e6  
    ndiv = int(ceil(clock.frequency / max_frequency))
    sample_rate = (clock.frequency / ndiv) / 16
    hightick = ndiv // 2
    lowtick = ndiv - hightick
    print("derived sample rate: {} ({}, {}) given a {} MHz clock".format(
          sample_rate, hightick, lowtick, clock.frequency/1e6))
        
    # depending on the system (global) clock frequency the sclk 
    # might not have 50% duty cycle (should be ok)
    # the datasheet indicates it requires at least a 40% cycle
    # for the high,
    # @todo: add a check for duty cycle
    clkcnt = Signal(intbv(hightick, min=0, max=ndiv))
    sclkpos, sclkneg = [Signal(bool(0)) for _ in range(2)]    
    
    @always_seq(clock.posedge, reset=reset)
    def beh_sclk_gen():
        # default case 
        sclkneg.next = False
        sclkpos.next = False
        
        # when the count expires toggle the clock 
        if clkcnt == 1:
            if sclk:
                sclk.next = False
                sclkneg.next = True
                clkcnt.next = lowtick
            else:
                sclk.next = True
                sclkpos.next = True
                clkcnt.next = hightick
        else:
            clkcnt.next = clkcnt-1
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # state-machine to drive sample conversion
    states = enum('start', 'capture') 
    state = Signal(states.start)
    bitcnt = Signal(intbv(0, min=0, max=17))
    
    # these could be combined into a single register (future optimization)
    sregout = Signal(intbv(0)[16:])  # shift-out register 
    sregin = Signal(intbv(0)[16:])   # shift-in register 
    
    # the ADC will generate continuous samples, each sample retrieval
    # is 16 bits.  The following state-machine assumes there are a
    # couple clock cycles between sclk pos/neg strobes.  Should add
    # a check
    # @todo: check ndiv > 4 ( ?)
    @always_seq(clock.posedge, reset=reset)
    def beh_state_machine():
        fifobus.write.next = False
        
        if state == states.start:
            # @todo: wait some amount of time
            if sclkneg:
                bitcnt.next = 0
                state.next = states.capture
                csn.next = False
                sregout.next[14:11] = channel
            
        elif state == states.capture:
            if sclkpos:
                bitcnt.next = bitcnt + 1 
                sregin.next = concat(sregin[15:0], din)
            elif sclkneg:
                sregout.next = concat(sregout[15:0], '0')
            
            if bitcnt == 16:
                state.next = states.start
                sample.next = sregin[12:]   # this can be removed
                if not fifobus.full:
                    fifobus.write_data.next = sregin
                    fifobus.write.next = True
                else:
                    print("FIFO full dropping sample")
                    
    # assign the serial out bit to the msb of the shift-register
    assign(dout, sregout(15))
    
    return myhdl.instances()