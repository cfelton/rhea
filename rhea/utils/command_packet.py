
import struct
from myhdl import now, delay

# packet definition constants
PACKET_LENGTH = 12
DATA_OFFSET = 8


class CommandPacket(object):
    def __init__(self, rnw=True, address=0, vals=None):
        """ """
        assert isinstance(vals, (type(None), list))
        self.rawbytes = bytearray([0 for _ in range(PACKET_LENGTH)])
        self.rawbytes[0] = 0xDE
        self.rawbytes[1] = 1 if rnw else 2
        self.rawbytes[2:6] = struct.pack(">L", address)
        self.rawbytes[6] = 4   # only support single read/write
        self.rawbytes[7] = 0xCA

        # @todo: support variable packets, block read/writes
        if vals is not None:
            self.rawbytes[8:12] = struct.pack(">L", vals[0])
        else:
            self.rawbytes[8:12] = struct.pack(">L", 0xFEEDFACE)

        # @todo: added checksum / CRC

    @staticmethod
    def pkt2str(pkt):
        assert isinstance(pkt, bytearray)
        pstr = " ".join(["{:02X}".format(bb) for bb in pkt])
        return pstr

    def __str__(self):
        return self.pkt2str(self.rawbytes)

    def dump(self, msg="", pkt=None):
        print("cmd: {}".format(self.pkt2str(self.rawbytes)))
        if pkt is not None:
            print("rsp: {}".format(self.pkt2str(pkt)))
        return msg

    def check_response(self, pkt, rvals=None, evals=None):
        assert pkt[0] == 0xDE, self.dump("invalid start byte", pkt)
        assert pkt[1] == self.rawbytes[1], self.dump("invalid command", pkt)
        assert pkt[2:6] == self.rawbytes[2:6], self.dump("invalid address", pkt)
        assert pkt[7] == 0xCA, self.dump("invalid byte 7", pkt)
        if rvals is not None and evals is not None:
            for ii, ev in enumerate(evals):
                rval, = struct.unpack(">L", pkt[8+(ii*4):12+(ii*4)])
                assert rval == ev, "{:08X} != {:08X}".format(rval, ev)
                rvals.append(rval)

    def put(self, fifobus):
        yield fifobus.clock.posedge
        for byte in self.rawbytes:
            fifobus.write.next = True
            fifobus.write_data.next = byte
            yield fifobus.clock.posedge
        fifobus.write.next = False

    def get(self, fifobus, rvals=None, evals=None, timeout=4000):
        timeout_value = timeout
        response_bytes = bytearray([0 for _ in range(PACKET_LENGTH)])
        rpkt = response_bytes
        bytestoget, ii = PACKET_LENGTH, 0

        while fifobus.empty and timeout > 0:
            timeout -= 1
            yield fifobus.clock.posedge

        if timeout == 0:
            raise TimeoutError

        timeout = timeout_value
        while bytestoget > 0 and timeout > 0:
            if not fifobus.empty and bytestoget > 1:
                fifobus.read.next = True
            else:
                fifobus.read.next = False

            if fifobus.read_valid:
                bb = int(fifobus.read_data)
                rpkt[ii] = bb
                bytestoget -= 1
                ii += 1
            timeout -= 1

            yield delay(1)
            if fifobus.empty:
                fifobus.read.next = False
            yield fifobus.clock.posedge

        # end read response packet loop, no more reads
        fifobus.read.next = False

        if timeout == 0:
            raise TimeoutError

        # check the received packet
        self.check_response(response_bytes, rvals, evals)
