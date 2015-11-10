
from __future__ import absolute_import

from myhdl import Signal, intbv, enum 
from . import memmap_controller_basic


def memmap_command_bridge(glbl, fifobus, mmbus):
    """ Convert a command packet to a memory-mapped bus transaction
    
    This module will decode the incomming packet and start a bus 
    transaction, the memmap_controller_basic is used to generate
    the bus transactions, it convertes the Barebone interface to 
    the MemoryMapped interface being used. 
    
    The variable length command packet is:
        00: 
        01: 
        02: command byte
        03: 
        04: address high byte 
        05: address byte 
        06: address byte 
        07: address low byte 
        08: length of data (max lenght 256 bytes)
        09: 
        10 - 13:  
        14 - 15: 
        16 - 271 (organized big-endian)
    The total packet length is 16 + data_length
    """
    
    clock, reset = glbl.clock, glbl.reset 
    bb = Barebone(clock, reset)
    
    states = enum('idle', 'end')
    state = Signal(states.idle)
    
    mmc_inst = memmap_controller_basic(bb, mmbus)
    
    always_seq(clock.posedge, reset=reset)
    def beh_state_machine():
        pass
    
    
    
    return mmc_inst, beh_state_machine
    