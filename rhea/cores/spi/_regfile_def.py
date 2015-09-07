
from ...system import RegisterFile, Register

"""
      ----------------------------------------------------------------
      @todo: resolve the local register file organizaiton with 
         the memmap organiztion (e.g. this register file is a



         colleciton of 8bit registers, if the memmap is setup 
         as 32 databits and 32 address bits want to organize 
         these differently (combing into 32 bit registers))
      Registers are on 32bit boundaries and are big-edian.  Meaning
      the most significant byte is byte 0.  Example the first register
      byte addresses are:
        LSB 3 byte == address 0x63
            2 byte == address 0x62
            1 byte == address 0x61
        MSB 0 byte == address 0x60
      end todo
      ----------------------------------------------------------------


      Registers: (Base address +)
        0x58: ???? setup register
             Freeze ----------------------------------------------+ 
             Select streaming (1) or mm ------------------------+ | 
                                                    | | | | | | | |
                                                    7 6 5 4 3 2 1 0

        0x60: SPCR control register
             Loop ------------------------------------------------+
             SPE System Enable ---------------------------------+ |
                ----------------------------------------------+ | |
             CPOL Clock Polarity ---------------------------+ | | |
             CPHA Clock Phase ----------------------------+ | | | | 
??           Tx FIFO Reset -----------------------------+ | | | | |
??           Rx FIFO Reset ---------------------------+ | | | | | |
             Manual Slave Select Enable ------------+ | | | | | | |             
                                                    | | | | | | | |
                                                    7 6 5 4 3 2 1 0
                                           
        0x64: SPSR status register
                                                    7 6 5 4 3 2 1 0
        0x68: SPTX transmit register
                                                    7 6 5 4 3 2 1 0
        0x6C: SPRX receive register

        0x70: SPSS slave select register
        0x74: SPTC transmit fifo count
        0x78: SPRC receive fifo count
        0x7C: SPXX SCK clock divisor (divides wb clk_i)
            0  -- 2 divisor 24 MHz (usbp == 48MHz system clock)
"""

regfile = RegisterFile()
# -- SPI Setup Register 
spst = Register('spst', 0x58, 8, 'rw', 0x00)
spst.add_named_bits('freeze', slice(1,0), 
                    "freeze the core")
spst.add_named_bits('rdata', slice(2,1), 
                    "1 : register file (memmap) feeds TX/RX FIFO")
regfile.add_register(spst)

# -- SPI Control Register (Control Register 0) --
spcr = Register('spcr', 0x60, 8, 'rw', 0x98)
spcr.comment = "SPI control register"
spcr.add_named_bits('loop', slice(1,0), "internal loopback")
spcr.add_named_bits('spe', slice(2,1), "system enable")
spcr.add_named_bits('cpol', slice(4,3), "clock polarity")
spcr.add_named_bits('cpha', slice(5,4), "clock phase")
spcr.add_named_bits('msse', slice(8,7), "manual slave select enable")
regfile.add_register(spcr)

# -- SPI status register --
spsr = Register('spsr', 0x64, 8, 'ro', 0)
spsr.add_named_bits('rxe', slice(1,0), "RX FIFO empty")
spsr.add_named_bits('rxf', slice(2,1), "RX FIFO full")
spsr.add_named_bits('txe', slice(3,2), "TX FIFO empty")
spsr.add_named_bits('txf', slice(4,3), "TX FIFO full")
spsr.add_named_bits('modf', slice(5,4), "SS line driven external fault")
regfile.add_register(spsr)

# -- The rest of the registers --
sptx = Register('sptx', 0x68, 8, 'rw', 0)
sptx.comment = "SPI transmit"
regfile.add_register(sptx)

sprx = Register('sprx', 0x6C, 8, 'rw', 0)
sprx.comment = "SPI receive"
regfile.add_register(sprx)

spss = Register('spss', 0x70, 8, 'rw', 0)
spss.comment = "SPI slave select register, manually select external devices"
regfile.add_register(spss)

sptc = Register('sptc', 0x74, 8, 'rw', 0)
sptc.comment = "transmit FIFO count"
regfile.add_register(sptc)

sprc = Register('sprc', 0x78, 8, 'rw', 0)
sprc.comment = "receive FIFO count"
regfile.add_register(sprc)

spxx = Register('spxx', 0x78, 8, 'rw', 0)
spxx.comment = "clock divisor register, sets sck period"
regfile.add_register(spxx)
