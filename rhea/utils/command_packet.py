
import struct

from myhdl import delay

class CommandPacket(object):
    def __init__(self, rnw=True, address=0, vals=None):
        """ """
        assert isinstance(vals, (type(None), list))
        self.packet = None
        self.packet = bytearray([0 for _ in range(16)])
        self.packet[0] = 0xDE
        self.packet[1] = 0xCA
        self.packet[2] = 1 if rnw else 2
        self.packet[3] = 0xFB
        self.packet[4:8] = struct.pack(">L", address)
        self.packet[8] = 4   # only support single read/write
        self.packet[9] = 0xAD

        # @todo: support variable packets, block read/writes
        if vals is not None:
            self.packet[16:20] = struct.pack(">L", vals[0])
        else:
            self.packet[16:20] = struct.pack(">L", 0xFEEDFACE)
        # @todo: added checksum / CRC

    def dump(self):
        pass

    def check_response(self, pkt, rvals=None, evals=None):
        assert pkt[0] == 0xDE
        assert pkt[1] == 0xCA
        assert pkt[2] == self.packet[2]
        assert pkt[3] == 0xFB
        assert pkt[4:8] == self.packet[4:8]
        if rvals is not None and evals is not None:
            for ii, ev in enumerate(evals):
                rval, = struct.unpack(">L", pkt[16+(ii*4):20+(ii*4)])
                assert rval == ev, "{:08X} != {:08X}".format(rval, ev)
                rvals.append(rval)

    def put(self, fifobus):
        yield fifobus.clock.posedge
        for byte in self.packet:
            fifobus.wr.next = True
            fifobus.wdata.next = byte
            yield fifobus.clock.posedge
        fifobus.wr.next = False

    def get(self, fifobus, rvals=None, evals=None, timeout=1000):
        response_packet = rpkt = bytearray([0 for _ in range(20
                                                             )])
        bytestoget, ii = 20, 0

        while fifobus.empty and timeout > 0:
            timeout -= 1
            yield fifobus.clock.posedge

        if timeout == 0:
            raise TimeoutError

        while bytestoget > 0:
            if not fifobus.empty and bytestoget > 1:
                fifobus.rd.next = True
            else:
                fifobus.rd.next = False

            if fifobus.rvld:
                bb = int(fifobus.rdata)
                rpkt[ii] = bb
                bytestoget -= 1
                ii += 1
            yield fifobus.clock.posedge
        fifobus.rd.next = False
        self.check_response(response_packet, rvals, evals)

