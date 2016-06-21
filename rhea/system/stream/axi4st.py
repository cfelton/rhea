
import myhdl
from myhdl import Signal, intbv, always_comb, always_seq
from . import Streamers


class AXI4StreamChannel(Streamers):
    def __init__(self, glbl, data_width=32):
        """ Interface for AXI4 streaming protocol """
        super(AXI4StreamChannel, self).__init__(glbl, data_width)
        vmax = 2**data_width
        self.valid = Signal(bool(0))
        self.data = Signal(intbv(vmax-1)[data_width:])
        self.accept = Signal(bool(1))

    @myhdl.block
    def register(self, upstream):
        """ register the upstream interface
        Register the upstream interface to this interface (this (self) is the
        downstream interface).
        """
        sti = upstream
        clock, reset = self.clock, self.reset
        accept = Signal(bool(1))

        @always_comb
        def beh_acc():
            sti.accept.next = (self.accept and self.valid) or accept

        @always_seq(clock.posedge, reset=reset)
        def beh_reg():
            xi = sti.accept and sti.valid
            if xi:
                self.data.next = sti.data
            self.valid.next = xi or (self.valid and not self.accept)
            accept.next = (sti.accept and not sti.valid)

        return beh_acc, beh_reg


class AXI4StreamLite(Streamers):
    def __init__(self, glbl, data_width=32, address_width=4, response_width=2):
        super(AXI4StreamLite, self).__init__(glbl, data_width)
        # currently top-level port interfaces can't contain multiple
        # levels (nested).  This will be enhanced in the future.
        self.clock = glbl.clock
        self.aw = AXI4StreamChannel(glbl, address_width)  # write address channel
        self.w = AXI4StreamChannel(glbl, data_width)      # write data channel
        self.ar = AXI4StreamChannel(glbl, address_width)  # read address channel
        self.r = AXI4StreamChannel(glbl, data_width)      # read data channel
        self.b = AXI4StreamChannel(glbl, response_width)  # response channel

    @myhdl.block
    def assign_upstream_port(self, pobj):
        """
        The need for the function should be removed in the future the
        myhdl converter will support nested interfaces.
        """
        assert isinstance(pobj, AXI4StreamLitePort)

        @always_comb
        def beh_assign():
            self.aw.valid.next = pobj.awvalid
            self.aw.data.next = pobj.awdata
            self.aw.accept.next = pobj.awaccept

            self.w.valid.next = pobj.wvalid
            self.w.data.next = pobj.wdata
            self.w.accept.next = pobj.waccept

            self.ar.valid.next = pobj.arvalid
            self.ar.data.next = pobj.ardata
            self.ar.accept.next = pobj.araccept

            pobj.rvalid.next = self.r.valid
            pobj.rdata.next = self.r.data
            pobj.raccept.next = self.r.accept

            pobj.bvalid.next = self.b.valid
            pobj.bdata.next = self.b.data
            pobj.baccept.next = self.b.accept

        return beh_assign

    def assign_downstream_port(self, pobj):
        assert isinstance(pobj, AXI4StreamLitePort)

    @myhdl.block
    def register(self, upstream):
        sti, gens = upstream, []
        for ch in ('aw', 'w', 'ar'):
            chintf = getattr(self, ch)
            gens.append(chintf.register(getattr(sti, ch)))

        for ch in ('r', 'b'):
            chintf = getattr(sti, ch)
            gens.append(chintf.register(getattr(self, ch)))
        return gens


class AXI4StreamLitePort:
    def __init__(self, data_width=32,  address_width=4, response_width=2):
        self.data_width = data_width
        self.address_width = address_width
        self.response_width = response_width
        # currently top-level port interfaces can't contain multiple
        # levels (nested).  This will be enhanced in the future.

        self.awvalid = Signal(bool(0))
        self.awdata = Signal(intbv(15)[address_width:])
        self.awaccept = Signal(bool(1))

        self.wvalid = Signal(bool(0))
        self.wdata = Signal(intbv(0xE6)[data_width:])
        self.waccept = Signal(bool(1))

        self.arvalid = Signal(bool(0))
        self.ardata = Signal(intbv(15)[address_width:])
        self.araccept = Signal(bool(1))

        self.rvalid = Signal(bool(0))
        self.rdata = Signal(intbv(0xE8)[data_width:])
        self.raccept = Signal(bool(1))

        self.bvalid = Signal(bool(0))
        self.bdata = Signal(intbv(3)[response_width:])
        self.baccept = Signal(bool(1))

