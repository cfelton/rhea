#
# Copyright (c) 2015 Christopher Felton, Nick Shaffner
#
# Master .UCF Reference:
#   https://digilentinc.com/Data/Products/ANVYL/ANVYL-Master_UCF.zip
#
# Reference Manual:
#   https://reference.digilentinc.com/_media/anvyl:anvyl_rm.pdf
#

from rhea.build import FPGA
from rhea.build.extintf import Port
from rhea.build.toolflow import ISE

class Anvyl(FPGA):
    vendor = 'xilinx'
    family = 'spartan6'
    device = 'XC6SLX45'
    package = 'CSG484'
    speed = '-3'
    _name = 'anvyl'

    default_clocks = {
        'clock': dict(frequency=100e6, pins=('D11',), iostandard='LVCMOS33')
    }
    
    default_ports = {
        # leds
        'led': dict(pins=('W3', 'Y4', 'Y1', 'Y3', 'AB4', 'W1', 'AB3', 'AA4',),
                    iostandard='LVCMOS18'),

        # gyr leds (x2)
        'ldt1g': dict(pins=('T7',), iostandard='LVCMOS18'),
        'ldt1y': dict(pins=('W4',), iostandard='LVCMOS18'),
        'ldt1r': dict(pins=('U8',), iostandard='LVCMOS18'),
        'ldt2g': dict(pins=('R7',), iostandard='LVCMOS18'),
        'ldt2y': dict(pins=('U6',), iostandard='LVCMOS18'),
        'ldt2r': dict(pins=('T8',), iostandard='LVCMOS18'),

        # 7 segment display (x6 digits)
        'seg': dict(pins=('AA21', 'AA22', 'Y22', 'N15', 'AB19', 'P20', 'Y21', 'P15',),
                    iostandard='LVCMOS33'),
        'an': dict(pins=('P16', 'M17', 'N16', 'P19', 'AA20', 'AB21',),
                   iostandard='LVCMOS33'),

        # slide switches
        'sw': dict(pins=('V5', 'U4', 'V3', 'P4', 'R4', 'P6', 'P5', 'P8',),
                   iostandard='LVCMOS18'),

        # push-buttons
        'btn': dict(pins=('E6', 'D5', 'A3', 'AB9',), iostandard='LVCMOS18'),

        # keypad
        'kypd_col': dict(pins=('H8', 'J7', 'K8', 'K7',), iostandard='LVCMOS18'),
        'kypd_row': dict(pins=('E4', 'F3', 'G8', 'G7',), iostandard='LVCMOS18'),    # external pull-up

        # breadboard:
        'bb': dict(pins=('AB20', 'P17', 'P18', 'Y19', 'Y20', 'R15', 'R16', 'R17', 'R19', 'V19',),
                   iostandard='LVCMOS33'),

        # dip banks a & b
        'dip_a': dict(pins=('G6', 'G4', 'F5', 'E5',), iostandard='LVCMOS18'),
        'dip_b': dict(pins=('F8', 'F7', 'C4', 'D3',), iostandard='LVCMOS18'),

        # rs232 (FT223 http://www.ftdichip.com/Support/Documents/DataSheets/ICs/DS_FT2232H.pdf )
        'rs232_uart_tx': dict(pins=('T19',), iostandard='LVCMOS33'),
        'rs232_uart_rx': dict(pins=('T20',), iostandard='LVCMOS33'),

        # usb1
        'usb1_clk': dict(pins=('A12',), iostandard='LVCMOS33'),
        'usb1_sdi': dict(pins=('B16',), iostandard='LVCMOS33'),
        'usb1_sdo': dict(pins=('A16',), iostandard='LVCMOS33'),
        'usb1_ss': dict(pins=('C17',), iostandard='LVCMOS33'),

        # usb2
        'usb2_clk': dict(pins=('K17',), iostandard='LVCMOS33'),
        'usb2_data': dict(pins=('L17',), iostandard='LVCMOS33'),

        # iic
        'iic_sda': dict(pins=('C5',), pullup=True, iostandard='LVCMOS33'),  # TODO: Should be tri-state
        'iic_scl': dict(pins=('A4',), pullup=True, iostandard='LVCMOS33'),

        # audio ( SSM2603 http://www.analog.com/media/en/technical-documentation/data-sheets/SSM2603.pdf )
        'ac_playbackdata': dict(pins=('A5',), iostandard='LVCMOS33'),
        'ac_playbacklrc': dict(pins=('D6',), iostandard='LVCMOS33'),
        'ac_recdata': dict(pins=('C6',), iostandard='LVCMOS33'),
        'ac_reclrc': dict(pins=('B6',), iostandard='LVCMOS33'),
        'ac_bclk': dict(pins=('B120',), iostandard='LVCMOS33'),
        'ac_clko': dict(pins=('C11',), iostandard='LVCMOS33'),
        'ac_mute': dict(pins=('A15',), iotandard='LVCMOS33'),
        'ac_mclk': dict(pins=('A6',), iostandard='LVCMOS33'),

        # oled ( UG-2832HSWEG04 https://cdn-shop.adafruit.com/datasheets/UG-2832HSWEG04.pdf )
        'oled_sdin': dict(pins=('C8',), iostandard='LVCMOS33'),
        'oled_sclk': dict(pins=('D7',), iostandard='LVCMOS33'),
        'oled_dc': dict(pins=('A8',), iostandard='LVCMOS33'),
        'oled_res': dict(pins=('B8',), iostandard='LVCMOS33'),
        'oled_vbat': dict(pins=('C7',), iostandard='LVCMOS33'),
        'oled_vdd': dict(pins=('A7',), iostandard='LVCMOS33'),

        # touchscreen tft

        # vga
        'red_o': dict(pins=('T3', 'B2', 'H3', 'H4',), iostandard='LVCMOS18'),
        'green_o': dict(pins=('T4', 'M6', 'H6', 'N6',), iostandard='LVCMOS18'),
        'blue_o': dict(pins=('M8', 'M7', 'N7', 'P7',), iostandard='LVCMOS18'),

        'vsync_o': dict(pins=('V18',), iostandard='LVCMOS33'),
        'hsync_o': dict(pins=('V17',), iostandard='LVCMOS33'),

        # hdmi
        'hdmi_tx_p': dict(pins=('D10', 'C9', 'D9',), iostandard='TDMS_33'),
        'hdmi_tx_p_clk': dict(pins=('B10',), iostandard='TDMS_33'),
        'hdmi_tx_n': dict(pins=('C10', 'A9', 'D8',), iostandard='TDMS_33'),
        'hdmi_tx_n_clk': dict(pins=('A10',), iostandard='TDMS_33'),

        # ethernet

        # sram ( R1LV0816ASB - https://www.renesas.com/en-us/doc/products/memory/rej03c0387_r1lv0816asb_ds.pdf )
        'memory_address': dict(pins=('F22', 'F21', 'E22', 'D22', 'D21', 'D19', 'D20' 'E20'
                                     'G17', 'H18', 'H13', 'H12', 'K16', 'L15', 'G15', 'J16',
                                     'H17', 'H16', 'G16'), iostandard='LVCMOS33'),

        'memory_data': dict(pins=('H21', 'A20', 'A21', 'A19', 'B20', 'C18', 'C19', 'F15',
                                  'F18', 'F17', 'F14', 'F13', 'H14', 'H19', 'H20', 'G20',),
                            iostandard='LVCMOS33'),  # TODO: This should be tri-state.

        'sram_cs1': dict(pins=('G22',), iostandard="LVCMOS33"),
        'sram_cs2': dict(pins=('G13',), iostandard="LVCMOS33"),
        'sram_oe': dict(pins=('F19',), iostandard="LVCMOS33"),
        'sram_we': dict(pins=('F16',), iostandard="LVCMOS33"),
        'sram_upper_b': dict(pins=('F20',), iostandard='LVCMOS33', drive=2, pulldown=True),
        'sram_lower_b': dict(pins=('G19',), iostandard='LVCMOS33', drive=2, pulldown=True),

        # ddr2

        # pmod connectors
        'ja': dict(pins=('AA18', 'AA16', 'Y15', 'V15', 'AB18', 'AB16', 'AB15', 'W15',), iostandard='LVCMOS33'),
        'jb': dict(pins=('Y16', 'AB14', 'Y14', 'U14', 'AA14', 'W14', 'T14', 'W11',), iostandard='LVCMOS33'),
        'jc': dict(pins=('Y10', 'AB12', 'AB11', 'AB10', 'AA12', 'Y11', 'AA10', 'Y13',), iostandard='LVCMOS33'),
         # note: pmods jd-jg are shared with the expansion connector:
        'jd': dict(pins=('AB13', 'Y12', 'T11', 'W10', 'W12', 'R11', 'V11', 'T10',), iostandard='LVCMOS33'),
        'je': dict(pins=('U10', 'V9', 'Y8', 'AA8', 'U9', 'W9', 'Y9', 'AB8',), iostandard='LVCMOS33'),
        'jf': dict(pins=('V7', 'W6', 'Y7', 'AA6', 'W8', 'Y6', 'AB7', 'AB6',), iostandard='LVCMOS33'),
        'jg': dict(pins=('V20', 'T18', 'D17', 'B18', 'T17', 'A17', 'C16', 'A18',), iostandard='LVCMOS33'),

        # 40 pin expansion connector J1 - essentially an aggregate of pmods jd, je, jf and jg
        # NOTE: pins 1 = GND, 2 = 5V, 3 = 3.3V, 4-35 = as below, 36-40 = NC
        'expansion': dict(pins=('AB13', 'Y12', 'T11', 'W10', 'W12', 'R11', 'V11', 'T10',    # same as pmod 'jd'
                                'U10', 'V9', 'Y8', 'AA8', 'U9', 'W9', 'Y9', 'AB8',          # same as pmod 'je'
                                'V7', 'W6', 'Y7', 'AA6', 'W8', 'Y6', 'AB7', 'AB6',          # same as pmod 'jf'
                                'V20', 'T18', 'D17', 'B18', 'T17', 'A17', 'C16', 'A18',),   # same as pmod 'jg'
                          iostandard='LVCMOS33')
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)