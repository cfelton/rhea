
from __future__ import absolute_import

from myhdl import (Signal, intbv, enum, always_seq, always_comb,
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
        10 - 13:  ?? error code(s) ??
        14 - 15:
        Only fixed 20 byte packet currently supported, future
        to support block write/reads upto 256-16
        16 - 19: first write / read (expects dummy bytes in read pkt)
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
    
    states = enum(
        'idle',
        'wait_for_packet',   # receive a command packet
        'check_packet',      # basic command check
        'write',             # bus write
        'write_end',         # end of the write cycle
        'read',              # read bus cycles for response
        'read_end',          # end of the read cycle
        'response',          # send response packet
        'error',             # error occurred
        'end'                # end state
    )

    state = Signal(states.idle)
    ready = Signal(bool(0))
    error = Signal(bool(0))
    bytecnt = intbv(0, min=0, max=256)

    # known knows
    pidx = (0, 1, 3, 9)
    pval = (0xDE, 0xCA, 0xFB, 0xAD)
    assert len(pidx) == len(pval)
    nknown = len(pidx)

    bytemon = Signal(intbv(0)[8:])

    # only supporting 20byte packets (single read/write) for now
    packet = [Signal(intbv(0)[8:]) for _ in range(20)]
    command = packet[2]
    address = ConcatSignal(*packet[4:8])
    data = ConcatSignal(*packet[16:20])
    datalen = packet[8]

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
            bytecnt[:] = 0

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

                packet[bytecnt].next = fbrx.rdata
                bytecnt[:] = bytecnt + 1

            # @todo: replace 20 with len(CommandPacket().header)
            if bytecnt == 20:
                ready.next = False
                state.next = states.check_packet

        elif state == states.check_packet:
            # @todo: some packet checking
            bb.per_addr = address[32:28]
            bb.mem_addr = address[28:0]
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
                packet[16].next = bb.read_data[32:24]
                packet[17].next = bb.read_data[24:16]
                packet[18].next = bb.read_data[16:8]
                packet[19].next = bb.read_data[8:0]
                state.next = states.response

        elif state == states.response:
            fbtx.wr.next = False
            if bytecnt < 20:
                fbtx.wr.next = True
                fbtx.wdata.next = packet[bytecnt]
            else:
                state.next = states.end

            bytecnt[:] = bytecnt + 1

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
