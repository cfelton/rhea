

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

    def process(self, glbl, lcd):
        """
        """
        self.update_cnt = 0

        # ...
        self.states = enum('init')

        @instance
        def beh():
            cmdbytes = []
            databytes = []
            while True:
                # wait for a new command
                yield lcd.csn.negedge
                wrn, rdn = bool(lcd.wrn), bool(lcd.rdn)
                command_in_progress = False
                numbytes = 0
                while not lcd.csn:
                    # check for rising edge of wrn or rdn
                    if not wrn and lcd.wrn:
                        if not lcd.dcn:
                            # a command
                            command_in_progress = True
                            cmd = lcd.data[8:]
                        else:
                            if command_in_progress:
                                cmdbytes[numbytes] = int(lcd.data[8:])
                            else:
                                databytes
                            numbytes += 1

                    wrn, rdn = bool(lcd.wrn), bool(lcd.rdn)
                    yield delay(2)

