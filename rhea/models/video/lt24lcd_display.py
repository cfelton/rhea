
from __future__ import absolute_import

from copy import copy

import myhdl
from myhdl import Signal, intbv, enum, instance, delay, now
from .video_display import VideoDisplay


class LT24LCDDisplay(VideoDisplay):
    def __init__(self):
        """
        """
        self.resolution = res = (240, 320)
        self.color_depth = cd = (5, 6, 5)
        super(LT24LCDDisplay, self).__init__(resolution=res, color_depth=cd)
        self.name = 'lt24lcd'                

    @myhdl.block
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

            while True:
                command_in_progress = False
                # numbytes actually the number of transfers
                numbytes, cmdbytes = 0, []
                self.reset_cursor()

                # wait for a new command
                # @todo: add timing checks
                yield lcd.csn.negedge
                wrn, rdn = bool(lcd.wrn), bool(lcd.rdn)

                # handle a transaction (csn low pulse)
                while not lcd.csn or command_in_progress:
                    if lcd.csn and command_in_progress:
                        regfile[cmd] = copy(cmdbytes)
                        command_in_progress = False
                        print("{:<10d}:LT24: cmd 0x{:02X}, numdata {}, data {}".format(
                            now(), cmd, numbytes, list(map(hex, cmdbytes[:])), ))
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
                                if cmd == 0x2C:
                                    self.update_next_pixel(int(lcd.data))
                                else:
                                    cmdbytes += [int(lcd.data[8:])]
                                numbytes += 1
                            else:
                                assert False, "Unexpected data!"

                    wrn, rdn = bool(lcd.wrn), bool(lcd.rdn)
                    yield delay(2)

        return beh
