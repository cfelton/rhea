
from __future__ import absolute_import

from myhdl import enum, Signal, intbv, always_seq

from ...system.memmap import MemoryMapped
from ...system.memmap import Barebone


def memmap_controller_basic(generic, memmap):
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

    States = enum('Idle', 'Wait', 'Write', 'WriteAck', 'Read',
                  'ReadDone', 'End')
    state = Signal(States.Idle)

    timeout_max = 33
    tocnt = Signal(intbv(0, min=0, max=timeout_max))

    # map the generic bus to the bus in use
    conv_inst = memmap.from_generic(generic)

    @always_seq(memmap.clock.posedge, reset=memmap.reset)
    def rtl_sm():

        # ~~~[Idle]~~~
        if state == States.Idle:
            if not generic.done:
                state.next = States.Wait
            elif generic.write:
                state.next = States.Write
            elif generic.read:
                state.next = States.Read

        # ~~~[Wait]~~~
        elif state == States.Wait:

            if generic.done:
                tocnt.next = 0
                if generic.write:
                    state.next = States.Done
                elif generic.read:
                    state.next = States.ReadValid

        # ~~~[Write]~~~
        elif state == States.Write:
            pass

        # ~~~[Read]~~~
        elif state == States.Read:
            pass

        # ~~~~[ReadDone]~~~
        elif state == States.ReadDone:
            pass

        # ~~~[Done]~~~
        elif state == States.Done:
            pass

        # ~~~[]~~~
        else:
            assert False, "Invalid state %s" % (state,)

        return conv_inst, rtl_sm

    return conv_inst
