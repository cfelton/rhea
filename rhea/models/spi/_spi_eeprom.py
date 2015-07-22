
from random import randint

from myhdl import *

def _b(s):
    s = s.replace('_', '')
    s = s.replace('x', '0')
    return int(s,2)

class SPIEEPROM(object):
    def __init__(self, addr_width=24, data_width=8, max_size=1024):
        
        if max_size > 0:
            size = max_size
        else:
            size = 2**addr_width
            
        self.size = size
        self.addr_width = addr_width
        self.data_width = data_width

        self.mem = [Signal(intbv(randint(0,255))[8:]) for _ in xrange(size)]
        # status register: WPEN, x,x,x,BP1,BP0,WEN,RDY
        self.status = Signal(intbv("0000_0000"))
                     
        
        # eeprom instructions
        self.instr = {'WREN': _b("0000_x110"),  # set write enable latch
                      'WRDI': _b("0000_x100"),  # reset write enable latch
                      'RDSR': _b("0000_x101"),  # read status register
                      'WRSR': _b("0000_x001"),  # write status register
                      'READ': _b("0000_x011"),  # read data from memory array
                      'WRITE': _b("0000_x010"), # write data to memory array
                      }         
        
    def get_init(self):
        return map(int,self.mem)
    
    def gen(self,clock,reset,spibus):
        """
        this is modeled after the AT25 series SPI eeprom.
        """

        # max number of bits to shift in
        bit_count = self.addr_width + self.data_width + 8        
        shiftin = Signal(intbv(0)[bit_count:])
        write_enable = Signal(False)
        write_protected = Signal(True)

        @instance
        def model():
            dowr,dord = False,False
            while True:
                yield spibus.ss.negedge
                count,odata,rnw,dcyc = 0,0,True,False
                while count < bit_count:
                    yield spibus.sck.posedge
                    if spibus.ss: break
                    
                    # most-sig-bit first in time
                    shiftin.next = concat(shiftin[23:0],spibus.mosi)
                    count += 1
                    
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    # Instruction
                    if count == 8:
                        instr = concat(shiftin[7:0],spibus.mosi)

                        # handle WREN, WRDI, RDSR, WRSR here
                        if instr == self.instr['WREN']:
                            write_enable.next = True
                        elif instr == self.instr['WRDI']:
                            write_enable.next = False
                        elif instr == self.instr['RDSR']:
                            odata = self.status
                            dcyc = True
                        elif instr == self.instr['WRSR']:
                            dcyc = True
                        elif instr == self.instr['READ']:
                            rnw.next = True
                        elif instr == self.instr['WRITE']:
                            rnw.next = False
                        else:
                            assert False, "Invalid Instruction %04X"%(instr)
                            
                        if (instr != self.instr['WRITE'] and
                            instr != self.instr['READ']):
                            break
                        
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    # Address
                    elif count == 24+8:
                        addr = concat(shiftin[23:0],spibus.mosi)

                    elif count == 24+8+8:
                        if instr == self.instr['WRSR']:
                            data = concat(shiftin[7:0],spibus.mosi)
                            self.status.next = data
                            break  # break out of the transaction loop
                        elif instr == self.instr['RDSR']:
                            break  # break out of the transaction loop
                        
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    # Data
                    elif count == 24+8+8:
                        data = concat(shiftin[7:0],spibus.mosi)
                        if not rnw and write_enable and not write_protected:
                            self.mem[addr].next = data
                        else:
                            odata = self.mem[addr]
                        dcyc = True

                    if dcyc:
                        # msb first in time
                        spibus.miso.next = (odata >> 8) & 0x01
                        odata = odata << 1

        return model
                    
