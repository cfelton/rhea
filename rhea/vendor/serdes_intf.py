
import myhdl
from myhdl import Signal, intbv, always_comb
from . import Vendor


class SERDESInterface(Vendor):
    def __init__(self, clock_serial, clock_parallel=None, number_of_bits=8):
        """

        Ports
          clock_serial: serial clock
          clock_parallel: parallel clock

        Parameters
          number_of_bits: number of bits to convert to to parallel/serial

        """
        self.number_of_bits = number_of_bits
        nbits = number_of_bits
        # @todo: define the "first-in-time" bits, lsb or msb
        self.clock_serial = clock_serial
        self.clock_parallel = clock_parallel

        # serial bits input/output
        self.serial = Signal(bool(0))

        # parallel data
        self.data = Signal(intbv(0)[nbits:])

    @myhdl.block
    def input_buffer(self, seri_p, seri_n):
        @always_comb
        def beh():
            self.serial.next = seri_p and not seri_n
        return beh,

    @myhdl.block
    def output_buffer(self, sero_p, sero_n):
        @always_comb
        def beh():
            sero_p.next = self.serial
            sero_n.next = not self.serial
        return beh,

    def get_signals(self):
        return self.clock_serial, self.clock_parallel, self.data
