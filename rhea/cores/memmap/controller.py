
from __future__ import absolute_import

from myhdl import enum, Signal, intbv, always_seq

from rhea.system.memmap import MemoryMapped
from rhea.system.memmap import Barebone


def controller_basic(generic, memmap):
    """

    Ports:
    :param generic: barebone interface
    :param memmap: any memory-map interface
    :return:

    Parameters:

    This module contains a basic

    """

    assert isinstance(generic, Barebone)
    assert isinstance(memmap, MemoryMapped)

    states = enum('idle', 'wait', 'write', 'writeack', 'read',
                  'readdone', 'done', 'end')
    state = Signal(states.idle)

    timeout_max = 33
    tocnt = Signal(intbv(0, min=0, max=timeout_max))

    # map the generic bus to the bus in use
    conv_inst = memmap.map_from_generic(generic)

    @always_seq(memmap.clock.posedge, reset=memmap.reset)
    def beh_sm():

        # ~~~[Idle]~~~
        if state == states.idle:
            if not generic.done:
                state.next = states.wait
            elif generic.write:
                state.next = states.write
            elif generic.read:
                state.next = states.read

        # ~~~[Wait]~~~
        elif state == states.wait:
            if generic.done:
                tocnt.next = 0
                if generic.write:
                    state.next = states.done
                elif generic.read:
                    state.next = states.readdone

        # ~~~[Write]~~~
        elif state == states.write:
            state.next = states.done
            tocnt.next = 0

        # ~~~[Read]~~~
        elif state == states.read:
            state.next = states.readdone

        # ~~~~[ReadDone]~~~
        elif state == states.readdone:
            if generic.done:
                state.next = states.done

        # ~~~[Done]~~~
        elif state == states.done:
            # wait for transaction signals to be release
            if not (generic.write or generic.read):
                state.next = states.idle

        # ~~~[]~~~
        else:
            assert False, "Invalid state %s" % (state,)

    return conv_inst, beh_sm
