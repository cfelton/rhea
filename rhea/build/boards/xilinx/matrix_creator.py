
from rhea.build import FPGA
from rhea.build.toolflow import ISE


class MatrixCreator(FPGA):
    """
    Matrix Creator board:
    https://creator.matrix.one/#/index

    Pinout definitions:
    https://github.com/matrix-io/matrix-creator-fpga/blob/master/creator_core/creator.ucf
    """
    vendor = 'xilinx'
    family = 'spartan6'
    device = 'XC6SLX4'
    package = 'TQG144'
    speed = '-2'
    _name = 'matrix_creator'

    default_clocks = {
        'clock': dict(frequency=50e6, pins=(84,))
    }

    default_resets = {
        'reset': dict(active=0, async=True, pins=(123,), pullup=True)
    }

    default_ports = {
        # led pins
        'led': dict(pins=(39,), drive=24),   # debug led
        'everloop': dict(pins=(56,)),

        # pins to the raspberry pi
        'rpi_tx': dict(pins=(70,), pullup=True),
        'rpi_rx': dict(pins=(69,), pullup=True),
        'rpi_io': dict(
            pins=(138,    # RPI GPIO 05
                  139,    # RPI GPIO 06
                  120,    # RPI GPIO 13
                  119,    # RPI GPIO 16
                  1,      # RPI GPIO 25
                  )),

        # expansion pins
        'exp_io': dict(pins=(78, 79, 80, 81,
                             82, 83, 85, 88,
                             92, 93, 94, 95,
                             98, 99, 101, 102
                             ))

    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)

