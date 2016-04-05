#
# Copyright (c) 2015 Christopher L. Felton
#
# 
# Added Support for the Terasic De1-SoC Board
# By Mike Kennedy (Va3TeC)
#

from __future__ import absolute_import

from string import Template

from rhea.build import FPGA
from rhea.build.toolflow import Quartus


class DE1SoC(FPGA):
    vendor = 'altera'
    family = 'Cyclone V'
    device = '5CSEMA5F31C6'
    speed = '6'
    _name = 'de1_SoC'


# As Per page 23 of the user Guide for DE1-SoC
    default_clocks = {
        'clock': dict(frequency=50e6, pins=('AF14',)) 
        #'clock2': dict(frequency=50e6, pins=('AA16',))
        #'clock3': dict(frequency=50e6, pins=('Y26',))
        #'clock4': dict(frequency=50e6, pins=('K14',))
    }

    default_resets = {
        'reset': dict(active=0, async=True, pins=('',)) #Fixc
    }
    
    default_ports = {
        'led': dict(pins=('V16', 'W16', 'V17', 'V18', 'W17', 'W19', 'Y19', 'W20', 'W21', 'Y21')),
        'sw_key': dict(pins=('AA14', 'AA15', 'W15', 'Y16')),
        'sw_slide': dict(pins=('AB12', 'AC12', 'AF9', 'AF10','AD11','AD12','AE11','AC9','AD10','AE12')),
	
	'7-seg_0': dict(pins=(	'AE26', # HEX0[0]
				'AE27', # HEX0[1]      
				'AE28', # HEX0[2]      
				'AG27', # HEX0[3]      
				'AF28', # HEX0[4]      
				'AG28', # HEX0[5]      
				'AH28', # HEX0[6]      
				)),	
	
	'7-seg_1': dict(pins=(	'AJ29', # HEX1[0]
				'AH29', # HEX1[1]      
				'AH30', # HEX1[2]      
				'AG30', # HEX1[3]      
				'AF29', # HEX1[4]      
				'AF30', # HEX1[5]      
				'AD27', # HEX1[6]      
				)),	
	
	'7-seg_2': dict(pins=(	'AB23', # HEX2[0]
				'AE29', # HEX2[1]      
				'AD29', # HEX2[2]      
				'AC28', # HEX2[3]      
				'AD30', # HEX2[4]      
				'AC29', # HEX2[5]      
				'AC30', # HEX2[6]      
				)),	
	
	'7-seg_3': dict(pins=(	'AD26', # HEX3[0]
				'AC27', # HEX3[1]      
				'AD25', # HEX3[2]      
				'AC25', # HEX3[3]      
				'AB28', # HEX3[4]      
				'AB25', # HEX3[5]      
				'AB22', # HEX3[6]      
				)),	
	
	'7-seg_4': dict(pins=(	'AA24', # HEX4[0]
				'Y23', # HEX4[1]      
				'Y24', # HEX4[2]      
				'W22', # HEX4[3]      
				'W24', # HEX4[4]      
				'V23', # HEX4[5]      
				'W25', # HEX4[6]      
				)),
	
	'7-seg_5': dict(pins=(	'V25', # HEX5[0]
				'AA28', # HEX5[1]      
				'Y27', # HEX5[2]      
				'AB27', # HEX5[3]      
				'AB26', # HEX5[4]      
				'AA26', # HEX5[5]      
				'AA25', # HEX5[6]      
				)),	


        # bi-directional GPIO, 
        # @todo: finish the GPIO pins
        'gpio': dict(pins=(     'AC18', # GPIO_0[0]
                                'Y17', # GPIO_0[1] 
                                'AD17', # GPIO_0[2]
                                'Y18', # GPIO_0[3]
                                'AK16',  # GPIO_0[4]
                                'AK18', # GPIO_0[5]
                                'AK19',  # GPIO_0[6]
                                'AJ19',  # GPIO_0[7]
                                'AJ17',  # GPIO_0[8]
                                'AJ16', # GPIO_0[9]
                                'AH18',  # GPIO_0[10]
                                'AH17', # GPIO_0[11]
                                'AG16', # GPIO_0[12]
                                'AE16', # GPIO_0[13]
                                'AF16', # GPIO_0[14]
                                'AG17', # GPIO_0[15]
                                'AA18', # GPIO_0[16]
                                'AA19', # GPIO_0[17]
                                'AE17', # GPIO_0[18]
                                'AC20', # GPIO_0[19]
                                'AH19', # GPIO_0[20]
                                'AJ20', # GPIO_0[21]
                                'AH20', # GPIO_0[22]
                                'AK21', # GPIO_0[23]
                                'AD19', # GPIO_0[24]
                                'AD20', # GPIO_0[25]
                                'AE18', # GPIO_0[26]
                                'AE19', # GPIO_0[27]
                                'AF20', # GPIO_0[28]
                                'AF21', # GPIO_0[29]
                                'AF19', # GPIO_0[30]
                                'AG21', # GPIO_0[31]
                                'AF18', # GPIO_0[32]
                                'AG20', # GPIO_0[33]
                                'AG18', # GPIO_0[34]
                                'AJ21', # GPIO_0[35]
        			'AB17', # GPIO_1[0]
                                'AA21', # GPIO_1[1] 
                                'AB21', # GPIO_1[2]
                                'AC23', # GPIO_1[3]
                                'AD24',  # GPIO_1[4]
                                'AE23', # GPIO_1[5]
                                'AE24',  # GPIO_1[6]
                                'AF25',  # GPIO_1[7]
                                'AF26',  # GPIO_1[8]
                                'AG25', # GPIO_1[9]
                                'AG26',  # GPIO_1[10]
                                'AH24', # GPIO_1[11]
                                'AH27', # GPIO_1[12]
                                'AJ27', # GPIO_1[13]
                                'AK29', # GPIO_1[14]
                                'AK28', # GPIO_1[15]
                                'AK27', # GPIO_1[16]
                                'AJ26', # GPIO_1[17]
                                'AK26', # GPIO_1[18]
                                'AH25', # GPIO_1[19]
                                'AJ25', # GPIO_1[20]
                                'AJ24', # GPIO_1[21]
                                'AK24', # GPIO_1[22]
                                'AG23', # GPIO_1[23]
                                'AK23', # GPIO_1[24]
                                'AH23', # GPIO_1[25]
                                'AK22', # GPIO_1[26]
                                'AJ22', # GPIO_1[27]
                                'AH22', # GPIO_1[28]
                                'AG22', # GPIO_1[29]
                                'AF24', # GPIO_1[30]
                                'AF23', # GPIO_1[31]
                                'AE22', # GPIO_1[32]
                                'AD21', # GPIO_1[33]
                                'AA20', # GPIO_1[34]
                                'AC22', # GPIO_1[35]
                                )),

        # ADC pins (names given in the user manula)
        #'adc_cs_n': dict(pins=('A10',)),
        #'adc_saddr': dict(pins=('B10',)),
        #'adc_sdat': dict(pins=('A9',)),
        #'adc_sclk': dict(pins=('B14',)),

        # I2C lines shared with accelerometer and EEPROM
        #'i2c_sclk': dict(pins=('F2',)),
        #'i2c_sdat': dict(pins=('F1',)),
        #'g_sensor_cs_n': dict(pins=('G5',)),
        	#'g_sensor_int': dict(pins=('M2',)),

        # LT24 pins 
        # @todo: use an extintf interface/object		DE1_SOC Board
        'lcd_on': dict(pins=('AC22',)),  				# GPIO 1 pin 
        'lcd_resetn': dict(pins=('AD21',)),				# GPIO 1 pin 
        'lcd_csn': dict(pins=('AA20',)),				# GPIO 1 pin 
        'lcd_rs': dict(pins=('AH27',)),					# GPIO 1 pin
        'lcd_wrn': dict(pins=('AH24',)),				# GPIO 1 pin
        'lcd_rdn': dict(pins=('AG26',)),				# GPIO 1 pin
        'lcd_data': dict(pins=('AF26', 'AF25', 'AE24', 'AE23',		# GPIO 1, Data 0:3
                               'AJ27', 'AK29', 'AK28',  'AK27',		# GPIO 1, Data 4:7
                               'AJ26', 'AK26', 'AH25', 'AJ25',		# GPIO 1, DAta 8:11
                               'AJ24', 'AK24', 'AG23', 'AK23',)),	# GPIO 1, DAta 12:15


	# VGA Pins added for the Onboard VGA DAC chip. ADV7123
	# triple 10 Bit High speed Video DAC by analog devices.
									#Red Data
	'VGA_R_data': dict(pins=('A13', 'C13', 'E13', 'B12',        # Data 0:3
                               'C12', 'D12', 'E12',  'F13',  )),       # Data 4:7

									#Green Data
	'VGA_G_data': dict(pins=('J9', 'J10', 'H12', 'G10',        # Data 0:3
                               'G11', 'G12', 'F11',  'E11', )),        # Data 4:7

									#Blue	
	'VGA_B_data': dict(pins=('B13', 'G13', 'H13', 'F14',        # Data 0:3
                               'H14', 'F15', 'G15',  'J14', )),        # Data 4:7
	
	'VGA_Clock': dict(pins=('A11',)),                          #  pin 
        'VGA_BLANK_N': dict(pins=('F10',)),                         #  pin 
        'VGA_HS': dict(pins=('B11',)),                            #  pin 
        'VGA_VS': dict(pins=('D11',)),                             #  pin
        'VGA_SYNC_N': dict(pins=('C10',)),                            #  pin


    }

    program_device_cli = (
        Template("quartus_pgm -c \"DE-SoC [1-1]\" -m jtag -o \"p;$bitfile.sof@2\" "),
             )
    # example quartus_pgm -c USB-Blaster -m jtag -o bpv:design.pof
    program_nonvolatile_cli = (Template(""),)

    def get_flow(self, top=None):
        return Quartus(brd=self, top=top)
