
from rhea.build.boards.xilinx import Xula2


class MyCustomBoard(Xula2):
    # overriding the default ports, inherit the default 
    # clocks.  The default ports in this cause reprsent
    # the various widgets connected to the Xula2+stickit
    default_ports = {
        'leds': dict(pins=('R7', 'R15', 'R16', 'M15',)),
        'btns': dict(pins=('F1', 'F2', 'E1', 'E2',))
    }
