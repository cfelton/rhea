
from __future__ import absolute_import

import myhdl
from myhdl import (Signal, intbv, enum, always_seq, always_comb,
                   ConcatSignal)

from rhea.system import MemoryMapped, Barebone, FIFOBus
from . import controller_basic


@myhdl.block
def command_bridge(glbl, fifobus, mmbus):
    """ Convert a command packet to a memory-mapped bus transaction
    
    This module will decode the incomming packet and start a bus 
    transaction, the memmap_controller_basic is used to generate
    the bus transactions, it convertes the Barebone interface to 
    the MemoryMapped interface being used. 
    
    The variable length command packet is:
        00: 0xDE
        01: command byte (response msb indicates error)
        02: address high byte 
        03: address byte 
        04: address byte 
        05: address low byte 
        06: length of data (max length 256 bytes)
        07: 0xCA   # sequence number, fixed for now
        08: data high byte 
        09: data byte
        10: data byte
        11: data low byte
        Fixed 12 byte packet currently supported, future
        to support block write/reads up to 256-8-4
        12 - 253: write / read (big-endian)
        @todo: last 2 bytes crc
    The total packet length is 16 + data_length

    Ports:
      glbl: global signals and control
      fifobus: FIFOBus interface, read and write path
      mmbus: memory-mapped bus (interface)

    this module is convertible
    """
    assert isinstance(fifobus, FIFOBus)
    assert isinstance(mmbus, MemoryMapped)

    clock, reset = glbl.clock, glbl.reset 
    bb = Barebone(glbl, data_width=mmbus.data_width,
                  address_width=mmbus.address_width)
    
    states = enum(
        'idle',
        'wait_for_packet',   # receive a command packet
        'check_packet',      # basic command check
        'write',             # bus write
        'write_end',         # end of the write cycle
        'read',              # read bus cycles for response
        'read_end',          # end of the read cycle
        'response',          # send response packet
        'response_full',     # check of RX FIFO full
        'error',             # error occurred
        'end'                # end state
    )

    state = Signal(states.idle)
    ready = Signal(bool(0))
    error = Signal(bool(0))
    bytecnt = intbv(0, min=0, max=256)

    # known knows
    pidx = (0, 7,)
    pval = (0xDE, 0xCA,)
    assert len(pidx) == len(pval)
    nknown = len(pidx)

    bytemon = Signal(intbv(0)[8:])

    # only supporting 12byte packets (single read/write) for now
    packet_length = 12
    data_offset = 8
    packet = [Signal(intbv(0)[8:]) for _ in range(packet_length)]
    command = packet[1]
    address = ConcatSignal(*packet[2:6])
    data = ConcatSignal(*packet[8:12])
    datalen = packet[6]

    # convert generic memory-mapped bus to the memory-mapped interface
    # passed to the controller
    mmc_inst = controller_basic(bb, mmbus)

    @always_comb
    def beh_fifo_read():
        if ready and not fifobus.empty:
            fifobus.read.next = True
        else:
            fifobus.read.next = False

    @always_seq(clock.posedge, reset=reset)
    def beh_state_machine():

        if state == states.idle:
            state.next = states.wait_for_packet
            ready.next = True
            bytecnt[:] = 0

        elif state == states.wait_for_packet:
            if fifobus.read_valid:
                # check the known bytes, if the values is unexpected
                # goto the error state and flush all received bytes.
                for ii in range(nknown):
                    idx = pidx[ii]
                    val = pval[ii]
                    if bytecnt == idx:
                        if fifobus.read_data != val:
                            error.next = True
                            state.next = states.error

                packet[bytecnt].next = fifobus.read_data
                bytecnt[:] = bytecnt + 1

            # @todo: replace 20 with len(CommandPacket().header)
            if bytecnt == packet_length:
                ready.next = False
                state.next = states.check_packet

        elif state == states.check_packet:
            # @todo: some packet checking
            # @todo: need to support different address widths, use
            # @todo: `bb` attributes to determine which bits to assign
            bb.per_addr.next = address[32:28]
            bb.mem_addr.next = address[28:0]
            assert bb.done
            bytecnt[:] = 0

            if command == 1:
                state.next = states.read
            elif command == 2:
                bb.write_data.next = data
                state.next = states.write
            else:
                error.next = True
                state.next = states.error

        elif state == states.write:
            # @todo: add timeout
            if bb.done:
                bb.write.next = True
                state.next = states.write_end

        elif state == states.write_end:
            bb.write.next = False
            if bb.done:
                state.next = states.read

        elif state == states.read:
            # @todo: add timeout
            if bb.done:
                bb.read.next = True
                state.next = states.read_end

        elif state == states.read_end:
            bb.read.next = False
            if bb.done:
                # @todo: support different data_width bus
                packet[data_offset+0].next = bb.read_data[32:24]
                packet[data_offset+1].next = bb.read_data[24:16]
                packet[data_offset+2].next = bb.read_data[16:8]
                packet[data_offset+3].next = bb.read_data[8:0]
                state.next = states.response

        elif state == states.response:
            fifobus.write.next = False
            if bytecnt < packet_length:
                if not fifobus.full:
                    fifobus.write.next = True
                    fifobus.write_data.next = packet[bytecnt]
                    bytecnt[:] = bytecnt + 1
                state.next = states.response_full
            else:
                state.next = states.end
                
        elif state == states.response_full:
            fifobus.write.next = False
            state.next = states.response

        elif state == states.error:
            if not fifobus.read_valid:
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
