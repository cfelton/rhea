
import myhdl
from myhdl import Signal, SignalType, intbv, always_comb, ConcatSignal


@myhdl.block
def keep_port_names(**ports):
    """ touch the top-level ports so they are persevered """
    gens, width, catsig = [], 0, None

    # walk through all the ports
    for name, port in ports.items():
        if isinstance(port, (int, str, list, tuple,)):
            pass
        elif isinstance(port, SignalType):
            width += len(port)
            if catsig is None:
                catsig = port
            else:
                catsig = ConcatSignal(catsig, port)
        else:
            g = keep_port_names(**vars(port))
            gens.append(g)

    if width > 0:
        monsig = Signal(intbv(0)[width:])

        @always_comb
        def mon():
            monsig.next = catsig

        gens.append(mon)

    return gens
