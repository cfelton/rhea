
from __future__ import print_function, division

from fractions import gcd
import myhdl
from myhdl import Signal, intbv, modbv, enum, always_seq, always


@myhdl.block
def uartbaud(glbl, baudce, baudce16, baudrate=115200):
    """ Generate the UART baudrate strobe

    Three separate strobes are create: baudce, baudceh
    
    Arguments:
        glbl: rhea.Global interface, clk from glbl
        baudce: The baudce stobe
        baudce16: The baudce16 strobe
        Both of these are calculated in the function.

    Parameters:
        baudrate: The desired baudrate

    myhdl convertible
    """
    clock, reset = glbl.clock, glbl.reset

    # determine the actual baud rate given the system clock and then
    # calculate the limit.  The following creates a counter that counts
    # in increments of baudfreq, this creates a strobe on average equal
    # to the desired frequency.
    # @todo: this didn't work as well as I thought it would ???
    div = gcd(clock.frequency, 16*baudrate)
    baudfreq = int((16*baudrate) / div)
    baudlimit = int((clock.frequency / div)) 
    
    cbaud = clock.frequency / (16*(baudlimit / baudfreq))
    print("")
    print("uartlite ")
    print("  baudrate: {:f} actual {:f} ".format(baudrate, cbaud))
    print("  baud frequency: {:.3f}, baud limit: {:.3f}".format(
          baudfreq, baudlimit))
    print("  remainder {:f}".format(baudlimit / baudfreq))
    print("")

    cntmax = baudlimit - baudfreq
    cnt = Signal(intbv(0, min=0, max=2*cntmax))
    cnt16 = Signal(modbv(0, min=0, max=16))

    @always_seq(clock.posedge, reset=reset)
    def beh_baud16():
        if cnt >= cntmax:
            cnt.next = cnt - cntmax  #baudlimit
            baudce16.next = True
        else:
            cnt.next = cnt + baudfreq
            baudce16.next = False

    @always_seq(clock.posedge, reset=reset)
    def beh_baud():
        # this strobe will be delayed one clocke from
        # the baudce16 strobe (non-issue)
        if baudce16:
            cnt16.next = cnt16 + 1
            if cnt16 == 0:
                baudce.next = True
            else:
                baudce.next = False
        else:
            baudce.next = False

    return myhdl.instances()


@myhdl.block
def uarttx(glbl, fbustx, tx, baudce):
    """UART transmitter  function
    
    Arguments(Ports):
        glbl : rhea.Global interface, clock and reset
        fbustx : FIFOBus interface to the TX fifo
        tx : The actual transmition line

    Parameters:
        baudce : The transmittion baud rate

    myhdl convertible
    """
    clock, reset = glbl.clock, glbl.reset

    states = enum('wait', 'start', 'byte', 'stop', 'end')
    state = Signal(states.wait)
    txbyte = Signal(intbv(0)[8:])
    bitcnt = Signal(intbv(0, min=0, max=9))

    @always_seq(clock.posedge, reset=reset)
    def beh_tx():
        # default values
        fbustx.read.next = False

        # state handlers
        if state == states.wait:
            if not fbustx.empty and baudce:
                txbyte.next = fbustx.read_data
                fbustx.read.next = True
                state.next = states.start

        elif state == states.start:
            if baudce:
                bitcnt.next = 0
                tx.next = False
                state.next = states.byte

        elif state == states.byte:
            if baudce:
                bitcnt.next = bitcnt + 1
                tx.next = txbyte[bitcnt]
            elif bitcnt == 8:
                state.next = states.stop
                bitcnt.next = 0

        elif state == states.stop:
            if baudce:
                tx.next = True
                state.next = states.end

        elif state == states.end:
            if baudce:
                state.next = states.wait

        else:
            assert False, "Invalid state %s" % (state)

    return myhdl.instances()


@myhdl.block
def uartrx(glbl, fbusrx, rx, baudce16):
    """UART receiver function
       
    Arguments(Ports):
        glbl : rhea.Global interface, clock and reset
        fbusrx : FIFOBus interface to the RX fifo
        rx : The actual receiver line
        baudce16 : The receive baud rate, strobes 16x the
            configured baud rate.

    myhdl convertible
    """
    clock, reset = glbl.clock, glbl.reset

    states = enum('wait', 'byte', 'stop', 'end')
    state = Signal(states.wait)
    rxbyte = Signal(intbv(0)[8:])
    bitcnt = Signal(intbv(0, min=0, max=9))

    # signals use do find the mid bit
    rxd = Signal(bool(0))
    mcnt = Signal(modbv(0, min=0, max=16))
    midbit = Signal(bool(0))
    rxinprog = Signal(bool(0))

    # get the middle of the bits, always sync to the beginning
    # (negedge) of the start bit
    @always(clock.posedge)
    def beh_mid():
        rxd.next = rx
        if (rxd and not rx) and state == states.wait:
            mcnt.next = 0
            rxinprog.next = True
        elif rxinprog and state == states.end:
            rxinprog.next = False
        elif baudce16:
            mcnt.next = mcnt + 1

        # 7 or 8 doesn't really matter
        if rxinprog and mcnt == 7 and baudce16:
            midbit.next = True
        else:
            midbit.next = False

    @always_seq(clock.posedge, reset=reset)
    def beh_rx():
        # defaults
        fbusrx.write.next = False

        # state handlers
        if state == states.wait:
            if midbit and not rx:
                state.next = states.byte

        elif state == states.byte:
            if midbit:
                rxbyte.next[bitcnt] = rx
                bitcnt.next = bitcnt + 1
            elif bitcnt == 8:
                state.next = states.stop
                bitcnt.next = 0

        elif state == states.stop:
            if midbit:
                #assert rx
                state.next = states.end
                fbusrx.write.next = True
                fbusrx.write_data.next = rxbyte

        elif state == states.end:
            state.next = states.wait
            bitcnt.next = 0

    return myhdl.instances()
