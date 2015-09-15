
from __future__ import absolute_import

from copy import copy

from myhdl import Signal, intbv, enum, instance, delay
from PIL import Image

from ._video_display import VideoDisplay


class LT24LCDDisplay(VideoDisplay):
    def __init__(self):
        """
        """
        self.resolution = res = (240, 320)
        self.color_depth = cd = (5, 6, 5)
        super(LT24LCDDisplay, self).__init__(resolution=res, color_depth=cd)
        self.name = 'lt24_lcd'

    def process(self, glbl, lcd):
        """
        """
        self.update_cnt = 0

        # ...
        self.states = enum('init')
        
        # use a dictionary to capture all the 
        regfile = {}

        # emulate the behavior of the LT24 LCD interface, the min pulses
        # (strobes) is 15ns and require 15ns between, the max write rate 
        # is 33 Mpix/sec.  Most (all) commands accept 4 bytes (4 writes)
        # for a command.
        @instance
        def beh():
            cmdbytes = []
            databytes = []

            while True:
                command_in_progress = False
                data_in_progress = False
                numbytes = 0

                # wait for a new command
                yield lcd.csn.negedge
                wrn, rdn = bool(lcd.wrn), bool(lcd.rdn)

                # handle a transaction (csn low pulse)
                while not lcd.csn and command_in_progress:
                    if not lcd.csn and command_in_progress:
                        regfile[cmd] = copy(cmdbytes)
                        command_in_progress = False
                    # check for rising edge of wrn or rdn
                    if not wrn and lcd.wrn:
                        if not lcd.dcn:
                            # a command received
                            command_in_progress = True
                            cmd = int(lcd.data[8:])
                            if cmd not in regfile:
                                regfile[cmd] = []
                        else:
                            if command_in_progress:
                                cmdbytes[numbytes] = int(lcd.data[8:])
                            else:
                                databytes[numbytes] = int(lcd.data)
                            numbytes += 1

                    wrn, rdn = bool(lcd.wrn), bool(lcd.rdn)
                    yield delay(2)

