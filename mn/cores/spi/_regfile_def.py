
from collections import OrderedDict
from myhdl import *
from ...system import RegisterFile,Register,RegisterBits

"""
      Registers are on 32bit boundaries and are big-edian.  Meaning
      the most significant byte is byte 0.  Example the first register
      byte addresses are:
        LSB 3 byte == address 0x63
            2 byte == address 0x62
            1 byte == address 0x61
        MSB 0 byte == address 0x60

      Registers: (Base address +)
        0x60: SPCR control register
             Loop ------------------------------------------------+
             SPE System Enable ---------------------------------+ |
             CPOL Clock Polarity ---------------------------+   | |
             CPHA Clock Phase ----------------------------+ |   | | 
??             Tx FIFO Reset -----------------------------+ | |   | |
??             Rx FIFO Reset ---------------------------+ | | |   | |
             Manual Slave Select Enable ------------+ | | | |   | |             
             Freeze ------------------------------+ | | | | |   | |
             Select streaming (1) or wb --------+ | | | | | |   | |
                                                | | | | | | |   | |
                                                9 8 7 6 5 4 3 2 1 0
        0x64: SPSR status register
                                                  8 7 6 5 4 3 2 1 0
        0x68: SPTX transmit register
                                                  8 7 6 5 4 3 2 1 0
        0x6C: SPRX receive register
        0x70: SPSS slave select register
        0x74: SPTC transmit fifo count
        0x78: SPRC receive fifo count
        0x7C: SPXX SCK clock divisor (divides wb clk_i)
            0  -- 2 divisor 24 MHz (usbp == 48MHz system clock)
"""

regdef = OrderedDict()

# -- SPI Control Register (Control Register 0) --
spcr = Register('spcr',0x60,8,'rw',0x98)
spcr.comment = "SPI control register"
spcr.add_named_bits('loop', slice(1,0), "internal loopback")
spcr.add_named_bits('spe', slice(2,1), "system enable")
spcr.add_named_bits('cpol', slice(4,3), "clock polarity")
spcr.add_named_bits('cpha', slice(5,4), "clock phase")
spcr.add_named_bits('msse', slice(6,5), "manual slace select enable")
spcr.add_named_bits('freeze', slice(7,6), "freeze the core")
spcr.add_named_bits('rdata', slice(8,7), "1 : register file (memmap) feeds TX/RX FIFO")
regdef[spcr.name] = spcr

# -- SPI status register --
spsr = Register('spsr',0x64,8,'ro',0)
spsr.add_named_bits('rxe', slice(1,0), "RX FIFO empty")
spsr.add_named_bits('rxf', slice(2,1), "RX FIFO full")
spsr.add_named_bits('txe', slice(3,2), "TX FIFO empty")
spsr.add_named_bits('txf', slice(4,3), "TX FIFO full")
spsr.add_named_bits('modf', slice(5,4), "SS line driven external fault")

# -- The rest of the registers --
sptx = Register('sptx',0x68,8,'rw',0)
sptx.comment = "SPI transmit"
regdef[sptx.name] = sptx

sprx = Register('sprx',0x6C,8,'rw',0)
sprx.comment = "SPI receive"
regdef[sprx.name] = sprx

spss = Register('spss',0x70,8,'rw',0)
spss.comment = "SPI slave select register, manually select external devices"
regdef[spss.name] = spss

sptc = Register('sptc',0x74,8,'rw',0)
sptc.comment = "transmit FIFO count"
regdef[sptc.name] = sptc

sprc = Register('sprc',0x78,8,'rw',0)
sprc.comment = "receive FIFO count"
regdef[sprc.name] = sprc

spxx = Register('spxx',0x78,8,'rw',0)
spxx.comment = "clock divisor register, sets sck period"
regdef[spxx.name] = spxx

# @todo need a home for the following control signals they should go in the control register
#RegDef["SPC1"
#       but see the @todo comment top of this file.
#  "tx_rst" : {"b" : 8,  "width" : 1, "comment" : "TX FIFO reset"} ,
#  "rx_rst" : {"b" : 9,  "width" : 1, "comment" : "RX FIFO reset"} ,
#  "lsbf"   : {"b" : 10, "width" : 1, "comment" : "lsb first in time (first out).  msb first in time is default"},

regfile = RegisterFile(regdef)
