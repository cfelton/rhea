#
# Copyright (c) 2015 Christopher L. Felton
#
# As Per To Do, Completed GPIO pins
# Mike Kennedy (Va3TeC)
#
#

from __future__ import absolute_import

from string import Template

from rhea.build import FPGA
from rhea.build.toolflow import Quartus


class DE0NanoSOC(FPGA):
    vendor = 'altera'
    family = 'Cyclone V'
    device = '5CSEMA4U23C6'
    speed = '6'
    _name = 'de0nano_soc'

    default_clocks = {
        'clock': dict(frequency=50e6, pins=('V11',))
    }

    default_resets = {
        'reset': dict(active=0, async=True, pins=('AH16',))
    }
    
    default_ports = {
        'led': dict(pins=('W15', 'AA24', 'V16', 'V15',
                          'AF26', 'AE26', 'Y16', 'AA23',)),
        'key': dict(pins=('AH17')),
        'sw': dict(pins=('L10', 'L9', 'H6', 'H5')),
        
        # bi-directional GPIO, 
        # @todo: finish the GPIO pins  (Completed)

        'gpio': dict(pins=(	'V12', # GPIO_0[0]
				'AF7', # GPIO_0[1] 
				'W12', # GPIO_0[2]
				'AF8', # GPIO_0[3]
				'Y8',  # GPIO_0[4]
				'AB4', # GPIO_0[5]
                           	'W8',  # GPIO_0[6]
				'Y4',  # GPIO_0[7]
				'Y5',  # GPIO_0[8]
				'U11', # GPIO_0[9]
				'T8',  # GPIO_0[10]
				'T12', # GPIO_0[11]
				'AH5', # GPIO_0[12]
				'AH6', # GPIO_0[13]
				'AH4', # GPIO_0[14]
				'AG5', # GPIO_0[15]
				'AH3', # GPIO_0[16]
				'AH2', # GPIO_0[17]
				'AF4', # GPIO_0[18]
				'AG6', # GPIO_0[19]
				'AF5', # GPIO_0[20]
				'AE4', # GPIO_0[21]
				'T13', # GPIO_0[22]
				'T11', # GPIO_0[23]
				'AE7', # GPIO_0[24]
				'AF6', # GPIO_0[25]
				'AF9', # GPIO_0[26]
				'AE8', # GPIO_0[27]
				'AD10', # GPIO_0[28]
				'AE9', # GPIO_0[29]
				'AD11', # GPIO_0[30]
				'AF10', # GPIO_0[31]
				'AD12', # GPIO_0[32]
				'AE11', # GPIO_0[33]
				'AF11', # GPIO_0[34]
				'AE12', # GPIO_0[35]

    			'Y15', # GPIO_1[0]
				'AG28', # GPIO_1[1] 
				'AA15', # GPIO_1[2]
				'AH27', # GPIO_1[3]
				'AG26',  # GPIO_1[4]
				'AH24', # GPIO_1[5]
                           	'AF23',  # GPIO_1[6]
				'AE22',  # GPIO_1[7]
				'AF21',  # GPIO_1[8]
				'AG20', # GPIO_1[9]
				'AG19',  # GPIO_1[10]
				'AF20', # GPIO_1[11]
				'AC23', # GPIO_1[12]
				'AG18', # GPIO_1[13]
				'AH26', # GPIO_1[14]
				'AA19', # GPIO_1[15]
				'AG24', # GPIO_1[16]
				'AF25', # GPIO_1[17]
				'AH23', # GPIO_1[18]
				'AG23', # GPIO_1[19]
				'AE19', # GPIO_1[20]
				'AF18', # GPIO_1[21]
				'AD19', # GPIO_1[22]
				'AE20', # GPIO_1[23]
				'AE24', # GPIO_1[24]
				'AD20', # GPIO_1[25]
				'AF22', # GPIO_1[26]
				'AH22', # GPIO_1[27]
				'AH19', # GPIO_1[28]
				'AH21', # GPIO_1[29]
				'AG21', # GPIO_1[30]
				'AH18', # GPIO_1[31]
				'AD23', # GPIO_1[32]
				'AE23', # GPIO_1[33]
				'AA18', # GPIO_1[34]
				'AC22', # GPIO_1[35]
				)),

    
        'arduino_io': dict(pins=(	'AG13', # Arduino_IO0  RXD
					'AF13', # Arduino_IO1  TXD
					'AG10', # Arduino_IO2
					'AG9', # Arduino_IO3
					'U14', # Arduino_IO4
					'U13', # Arduino_IO5
					'AG8', # Arduino_IO6
					'AH8', # Arduino_IO7
					'AF17', # Arduino_IO8
					'AE15', # Arduino_IO9
					'AF15', # Arduino_IO10  SS
					'AG16', # Arduino_IO11  MOSI
					'AH11', # Arduino_IO12  MISO
					'AH12', # Arduino_IO13  SCK
					'AH9', # Arduino_IO14  SDA
					'AG11', # Arduino_IO15  SCL
					'AH7', # Arduino_Reset_n 
				)),
	
        'adc': dict(pins=('L10', # ADC_CONVST    Conversion Start
			  'L9',  #ADC_SCK        SErial DAta Clock
			  'H6',  #ADC_SDI        Serial Data Input (FPGA to ADC)
			  'H5'   #ADC_SDO	 Serial Data Output (ADC to FPGA)
			)),
	}

    program_device_cli = (
        Template("quartus_pgm -c \"DE-SoC [1-1]\" -m jtag -o \"p;$bitfile.sof@2\" "),
             )
    # example quartus_pgm -c USB-Blaster -m jtag -o bpv:design.pof
    program_nonvolatile_cli = (Template(""),)

    def get_flow(self):
        return Quartus(brd=self)
