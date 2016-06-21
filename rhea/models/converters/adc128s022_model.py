
import myhdl
from myhdl import (Signal, intbv, enum, instance, always, delay,
                   concat, now, instances)


def convert(analog, rails=(0, 3.3)):
    sample_max = (2**12)-1
    sample_min = 0  
    sample = intbv(0)[12:]
    smp = (analog - rails[0])/rails[1] * ((2**12)-1)
    smp = min(sample_max, smp)
    smp = max(sample_min, smp)
    sample[:] = smp 
    return sample  # digital
    

@myhdl.block
def adc128s022_model(spibus, analog_channels, vref_pos=3.3, vref_neg=0.):
    """
    This is a model of the ADC128S022 A/D converter.  It will emulated
    the behavior described in the datasheet.
    """
    assert isinstance(analog_channels, list) and len(analog_channels) == 8 
    
    # use the signals names in the datasheet, names from the device
    # perspective
    sclk, dout, din, csn = spibus()
    
    states = enum('start', 'track', 'hold')
    state = Signal(states.start)

    monbits = Signal(intbv(0)[16:])
    monsmpl = Signal(intbv(0)[16:])
    monbcnt = Signal(intbv(0)[16:])

    @instance
    def beh():
        sample = intbv(0xAA)[16:]
        bitcnt, bitsin = 0, intbv(0)[16:]
        nextch = 0
        dout.next = 0

        while True:
            if state == states.start:
                yield delay(10)
                if not csn:
                    state.next = states.track
                    bitcnt = 15
                    dout.next = 0
                monbcnt.next = bitcnt
                    
            elif state == states.track:
                yield sclk.posedge
                bitsin[bitcnt] = int(din)
                bitcnt -= 1
                monbcnt.next = bitcnt
                # @todo: determine a reasonable model of the track/capture
                levels = [float(val) for val in analog_channels]
                yield sclk.negedge
                if bitcnt == 12:
                    ch = nextch
                    state.next = states.hold
                    # the real converter converts the sample over the next
                    # 12 clock cycles, convert instantly (is fine)
                    sample = convert(levels[ch], (vref_neg, vref_pos))
                    monsmpl.next = sample
                    print("converted channel {} from {} to {:04X}".format(
                          int(ch), float(levels[ch]), int(sample)))

            elif state == states.hold:
                yield sclk.posedge
                bitsin[bitcnt] = int(din)
                bitcnt -= 1
                if bitcnt == 10:
                    nextch = bitsin[14:11]
                    # print("  captured next channel {} ({:04X})".format(nextch, int(bitsin)))
                monbcnt.next = bitcnt
                yield sclk.negedge
                dout.next = sample[bitcnt]
                # print("{:8d}: sample[{:2d}] = {:4d}, {}->{}".format(
                #       now(), bitcnt, int(sample), int(dout.val), int(dout.next)))
                if bitcnt == 0:
                    state.next = states.start
                    yield sclk.posedge  # let the last bit clock in

            # need signals to update before next pass through
            yield delay(1)

    @always(sclk.posedge)
    def mon():
        monbits.next = concat(monbits[15:0], din)
                    
    return instances()
