
from __future__ import absolute_import

from myhdl import (Signal, intbv, enum, always_seq, always_comb, concat,
                   ConcatSignal)

from rhea.system import MemoryMapped, Barebone, FIFOBus
from . import memmap_controller_basic


def memmap_command_bridge(glbl, fifobusi, fifobuso, mmbus):
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
        08: length of data (max length 256 bytes)
        09: 
        10 - 13:  
        14 - 15: 
        16 - 271 (organized big-endian)
    The total packet length is 16 + data_length

    Ports:
      glbl: global signals and control
      fifobusi: input fifobus, host packets to device (interface)
      fifobuso: output fifobus, device responses to host (interface)
      mmbus: memory-mapped bus (interface)

    this module is convertible
    """
    assert isinstance(fifobusi, FIFOBus)
    assert isinstance(fifobuso, FIFOBus)
    assert isinstance(mmbus, MemoryMapped)
    fbrx, fbtx = fifobusi, fifobuso
    clock, reset = glbl.clock, glbl.reset 
    bb = Barebone(glbl, data_width=mmbus.data_width,
                  address_width=mmbus.address_width)
    
    states = enum('idle', 'wait_for_packet', 'set', 'write', 'response',
                  'read', 'error', 'end')

    state = Signal(states.idle)
    ready = Signal(bool(0))
    error = Signal(bool(0))
    bytecnt = intbv(0, min=0, max=256)

    # known knows
    pidx = (0, 1, 3, 9)
    pval = (0xDE, 0xCA, 0xFB, 0xAD)
    assert len(pidx) == len(pval)
    nknown = len(pidx)

    #command = Signal(intbv(0)[8:])
    #address = Signal(intbv(0)[32:])
    #data = Signal(intbv(0)[32:])
    #pktlen = Signal(intbv(0)[8:])
    #fourbytes = [Signal(intbv(0)[8::]) for _ in range(4)]
    bytemon = Signal(intbv(0)[8:])

    # only supporting 20byte packets (single read/write) for now
    packet = [Signal(intbv(0)[8:]) for _ in range(20)]
    command = packet[2]
    address = ConcatSignal(*packet[4:8])
    data = ConcatSignal(*packet[16:20])
    datalen = packet[[8]
    ]
    # convert generic memory-mapped bus to the memory-mapped interface
    # passed to the controller
    mmc_inst = memmap_controller_basic(bb, mmbus)

    @always_comb
    def beh_fifo_read():
        if ready and not fbrx.empty:
            fbrx.rd.next = True
        else:
            fbrx.rd.next = False

    @always_seq(clock.posedge, reset=reset)
    def beh_state_machine():

        if state == states.idle:
            state.next = states.wait_for_packet
            ready.next = True

        elif state == states.wait_for_packet:
            if fbrx.rvld:
                # check the known bytes, if the values is unexpected
                # goto the error state and flush all received bytes.
                for ii in range(nknown):
                    idx = pidx[ii]
                    val = pval[ii]
                    if bytecnt == idx:
                        if fbrx.rdata != val:
                            error.next = True
                            state.next = states.error

                if bytecnt == 2:
                    command.next = fbrx.rdata
                elif bytecnt == 4:
                    fourbytes[0].next = fbrx.rdata
                elif bytecnt == 5:
                    fourbytes[1].next = fbrx.rdata
                elif bytecnt == 6:
                    fourbytes[2].next = fbrx.rdata
                elif bytecnt == 7:
                    fourbytes[3].next = fbrx.rdata
                elif bytecnt == 8:
                    # @todo: packet definition supports variable length
                    # @todo: (block read/write) currently only implemented
                    # @todo: a single read/write
                    assert fbrx.rdata == 4
                    pktlen.next = fbrx.rdata
                    address.next = concat(fourbytes[0], fourbytes[1],
                                          fourbytes[2], fourbytes[3])
                    if fbrx.rdata != 4:
                        error.next = True
                        state.next = states.error
                elif bytecnt == 16:
                    fourbytes[0].next = fbrx.rdata
                elif bytecnt == 17:
                    fourbytes[1].next = fbrx.rdata
                elif bytecnt == 18:
                    fourbytes[2].next = fbrx.rdata
                elif bytecnt == 19:
                    fourbytes[3].next = fbrx.rdata
                    data.next = concat(fourbytes[0], fourbytes[1],
                                       fourbytes[2], fbrx.rdata)
                # keep track of the number of bytes consumed
                bytecnt[:] = bytecnt + 1

            # @todo: replace 20 with len(CommandPacket().header)
            if bytecnt == 20:
                ready.next = False
                state.next = states.set

        elif state == states.set:
            bb.per_addr = address[32:28]
            bb.mem_addr = address[28:0]
            if command == 1:
                bytecnt[:] = 0
                state.next = states.response
            elif command == 2:
                bb.write_data.next = data
                state.next = states.write
            else:
                error.next = True
                state.next = states.error

        elif state == state.response:
            fbtx.next = False
            # start sending the response and doing reads along the way
            if bytecnt == 0:
                fbtx.wr.next = True
                fbtx.wdata.next = 0xDE
            elif bytecnt == 1:
                fbtx.wr.next = True
                fbtx.wdata.next = 0xCA
            elif bytecnt == 2:
                fbtx.wr.next = True
                fbtx.wdata.next = command

        elif state == states.error:
            if not fbrx.rvld:
                state.next = states.end
                ready.next = False

        elif state == states.end:
            error.next = False
            ready.next = False
            state.next = states.idle

        else:
            assert False, "Invalid state %s" % (state,)

        bytemon.next = bytecnt

    return beh_fifo_read, mmc_inst, beh_state_machine
