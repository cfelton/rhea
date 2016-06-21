

import myhdl
from myhdl import always
from my_board_def import MyCustomBoard


@myhdl.block
def xula_button_blink(clock, leds, btns):
    
    @always(clock.posedge)
    def beh_blink():
        leds.next = btns
        
    return beh_blink
    

def build(args=None):
    brd = MyCustomBoard()
    flow = brd.get_flow(top=xula_button_blink)
    flow.run()
    
    
def main():
    build()
    
    
if __name__ == '__main__':
    main()