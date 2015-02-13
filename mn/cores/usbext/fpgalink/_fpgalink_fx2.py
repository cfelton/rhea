
from myhdl import *

FX2_OUT_FIFO = int('00', base=2)
FX2_IN_FIFO = int('01', base=2)

class Bus(object): pass
    
def get_interfaces():
    """ Single function to get the buses
    """
    clock = Signal(bool(1))
    reset = ResetSignal(bool(1), active=0, async=False)

    # Get an object that can be used for the "interfaces"
    fx2bus = Bus()  # External to the FPGA
    flbus = Bus()   # Internal

    # I am using a slightly different names
    fx2bus.fifosel = Signal(bool(0))      # FIFOADR[0] (FIFOADR[1] = 1)
    fx2bus.data_i = Signal(intbv(0)[8:])  # FD[7:0]
    fx2bus.data_o = Signal(intbv(0)[8:])  # FD[7:0]
    fx2bus.data_t = Signal(bool(0))       # data direction
    fx2bus.read = Signal(bool(0))         # SLOE, SLRD
    fx2bus.gotdata = Signal(bool(0))      # FLAGC
    fx2bus.write = Signal(bool(0))        # SLWR
    fx2bus.gotroom = Signal(bool(0))      # FLAGB
    fx2bus.pktend = Signal(bool(0))       # PKTEND

    flbus.chan_addr = Signal(intbv(0)[7:])# chanAddr
    flbus.data_o = Signal(intbv(0)[8:])   # h2f_data_out
    flbus.valid_o = Signal(bool(0))       # h2f_valid_out
    flbus.ready_i = Signal(bool(0))       # h2f_ready_in
    flbus.data_i = Signal(intbv(0)[8:])   # f2h_data_in
    flbus.valid_i = Signal(bool(0))       # f2h_valid_in
    flbus.ready_o = Signal(bool(0))       # f2h_ready_out

    return (clock, reset, fx2bus, flbus)

def m_fpgalink_fx2(
    clock,           # synchronous FPGA clock
    reset,           # synchronous FPGA reset

    fx2bus,          # external FX2 bus interface
    flbus,           # internal fpgalink bus interface    
    ):
    """ FPGALINK FX2 External USB Controller Interface
    """

    States = enum('IDLE', 'GET_COUNT0', 'GET_COUNT1', 'GET_COUNT2',
                  'GET_COUNT3', 'BEGIN_WRITE', 'WRITE', 'END_WRITE_ALIGNED',
                  'END_WRITE_NONALIGNED', 'READ', 'READ_WAIT')

    fopREAD, fopWRITE, fopNOP = [2,1,3]

    # Internal Signals
    state = Signal(States.IDLE)
    fifop = Signal(intbv(fopNOP)[2:])
    count =  Signal(intbv(0)[32:])
    is_aligned = Signal(bool(0))
    is_write = Signal(bool(0))
        
    @always_seq(clock.posedge, reset=reset)
    def hdl_sm():
        if state == States.GET_COUNT0:
            if fx2bus.gotdata:
                count.next = fx2bus.data_i << 24
                state.next = States.GET_COUNT1
            else:
                count.next = 0
                
        elif state == States.GET_COUNT1:
            if fx2bus.gotdata:
                count.next = count | (fx2bus.data_i << 16)
                state.next = States.GET_COUNT2

        elif state == States.GET_COUNT2:
            if fx2bus.gotdata:
                count.next = count | (fx2bus.data_i << 8)
                state.next = States.GET_COUNT3

        elif state == States.GET_COUNT3:
            if fx2bus.gotdata:
                count.next = count | fx2bus.data_i
                if is_write:
                    state.next = States.BEGIN_WRITE
                else:
                    if flbus.ready_i:
                        fifop.next = fopREAD      
                        state.next = States.READ
                    else:
                        fifop.next = fopNOP
                        state.next = States.READ_WAIT

        elif state == States.BEGIN_WRITE:
            fx2bus.fifosel.next = FX2_IN_FIFO
            fifop.next = fopNOP
            if count[9:] == 0:
                is_aligned.next = True
            else:
                is_aligned.next = False
            state.next = States.WRITE
                
        elif state == States.WRITE:
            if fx2bus.gotroom:
                flbus.ready_o.next = True
            if fx2bus.gotroom and flbus.valid_i:
                fifop.next = fopWRITE
                fx2bus.data_o.next = flbus.data_i
                fx2bus.data_t.next = True
                count.next = count - 1
                if count == 1:
                    if is_aligned:
                        state.next = States.END_WRITE_ALIGNED
                    else:
                        state.next = States.END_WRITE_NONALIGNED
            else:
                fifop.next = fopNOP            

        elif state == States.END_WRITE_ALIGNED:
            fx2bus.fifosel.next = FX2_IN_FIFO
            fifop.next = fopNOP
            state.next = States.IDLE

        elif state == States.END_WRITE_NONALIGNED:
            fx2bus.fifosel.next = FX2_IN_FIFO
            fifop.next = fopNOP
            fx2bus.pktend.next = False
            state.next = States.IDLE

        elif state == States.READ:
            fx2bus.fifosel.next = FX2_OUT_FIFO
            if fx2bus.gotdata and flbus.ready_i:
                assert not fx2bus.read
                flbus.valid_o.next = True
                flbus.data_o.next = fx2bus.data_i
                if count <= 1:
                    state.next = States.IDLE
                    count.next = 0
                else:
                    count.next = count - 1

                    
        elif state == States.READ_WAIT:
            if fx2bus.gotdata and flbus.ready_i:
                state.next = States.READ
                fifop.next = fopREAD
        
        else: # Idle state and others
            # The original state-machine left the 'read' control
            # signal always active until a write.
            fifop.next = fopREAD
            count.next = 0
            flbus.valid_o.next = False
            if fx2bus.gotdata:
                flbus.chan_addr.next = fx2bus.data_i[7:]
                is_write.next = fx2bus.data_i[7]
                state.next = States.GET_COUNT0

    @always_comb
    def hdl_assigns():
        fx2bus.read.next = fifop[0]
        fx2bus.write.next = fifop[1]
        
    return hdl_sm, hdl_assigns
    
if __name__ == '__main__':
    clock,reset,fx2bus,flbus = get_interfaces()
    g = fpgalink_fx2(clock, reset, fx2bus, flbus)
