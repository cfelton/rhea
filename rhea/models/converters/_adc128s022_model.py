

from myhdl import Signal, intbv, enum, instance, instances

from ...cores.spi import SPIBus


def convert(analog, rails=(0, 3.3)):
    sample_max = (2**12)-1
    sample_min = 0  
    sample = intbv(0)[12:]
    smp = (analog - rails[0]) * 2**12 
    smp = min(sample_max, smp)
    smp = max(sample_min, smp)
    sample[:] = smp 
    return sample  # digital
    
    
def adc128s022_model(spibus, analog_channels, vref_pos=3.3, vref_neg=0.):
    """
    This is a model of the ADC128S022 A/D converter.  It will emulated
    the behavior described in the datasheet.
    """
    assert isinstance(analog_channels, list) and len(analog_channels) == 8 
    
    # use the signals names in the datasheet, names from the device
    # perspective
    sclk, dout, din, csn = (spibus.sck, spibus.miso, spibus.mosi, spibus.csn)
    
    states = enum('start', 'track', 'hold')
    state = Signal(states.start)
    
    @instance
    def beh():
        sample = intbv(0xAA)[16:]
        bitcnt, bitsin = 0, intbv(0)[16:]
        while True:
            if state == states.start:
                yield sclk.negedge
                if not csn:
                    state.next = states.track
                    bitcnt = 16
                    dout.next = 0
                    
            elif state == states.track:
                yield sclk.posedge
                bitcnt -= 1 
                bitsin[bitcnt] = int(din)
                # @todo: determine a reasonable model of the track/capture
                levels = [float(val) for val in analog_channels]
                yield sclk.negedge
                if bitcnt == 12:
                    ch = bitsin[15:13]
                    state.next = states.hold
                    # the real converter converts the sample over the next
                    # 12 clock cycles, convert instantly (is fine)
                    sample = convert(levels[ch], (vref_neg, vref_pos))
                    print("converted channel {} from {} to {:04X}".format(
                          int(ch), float(analog_channels[ch]), int(sample)))
            elif state == states.hold:
                yield sclk.posedge
                yield sclk.negedge
                dout.next = sample[bitcnt]
                bitcnt -= 1
                
                if bitcnt == 0:
                    state.next = states.start
                    
    return instances()