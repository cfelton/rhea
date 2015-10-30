
"""
This file contains a general function to run the build for 
various boards. 

   >> python example_build_boards.py --board=<board name>
"""
import argparse

import rhea.build as build 
from rhea.build.boards import get_board
from rhea.build.boards import get_all_board_names
#from blink import blinky

# some boards don't have LEDs but they have IO that
# can drive LEDs.  The following maps the led port 
# to a set of pins for boards without an led port.
led_port_pin_map = {
    'xula':  dict(name='led', pins=(36, 37, 50, 52)),
    'xula2': dict(name='led', pins=('R7', 'R15', 'R16', 'M15',)),
    'pone': dict(name='led', pins=(18, 23, 26, 33)),
}


def print_board_info(args):
    boards = get_all_board_names()
    
    for bn in boards:
        brd = get_board(bn)
        
        has_led = False
        led = brd.get_port('led')
        if led is None:
            led = brd.get_port('leds')
        if led is not None:
            has_led = True
        numled = 0 if led is None else len(led.pins)
        ledpins = ' ' if led is None else led.pins
        ledname = ' ' if led is None else led.name
        
        # print some information
        print("{:12}: has led {:5}: {:5}, # led {}, led pins {} ".format(
              bn, str(has_led), str(ledname), numled, str(ledpins), ))
              
    return


def build_board(args):
    """
    """
    boards = get_all_board_names() if args.board == 'all' else [args.board]
    
    for bn in boards:        
        brd = get_board(bn)
        if brd in led_port_pin_map:
            brd.add_port(**led_port_pin_map[brd])
        # check the board definition has led port, if not add it from 
        # the board_table
        ledport = brd.get_port('led')
        
    return

        
def parseargs():
    boards = get_all_board_names() + ['all']
    parser = argparse.ArgumentParser()
    parser.add_argument('--board', default='xula', choices=boards,
                        help="select the board to build")
    parser.add_argument('--dump', default=False, action='store_true',
                        help="print information on all boards")
    args = parser.parse_args()
    return args
    
                        
def main():
    args = parseargs()
    print(vars(args))
    if args.dump:
        print_board_info(args)
    else:
        build_board(args)
    return 
    
    
if __name__ == '__main__':
    main()