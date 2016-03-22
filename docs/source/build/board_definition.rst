
Board definitions 
=================

The `rhea.build` contains a large list of board definitions.  The
board definitions define an FPGA and its configuration for a particular
board.  The board definitions define the default port list for the 
FPGA on a particular board.  The following is a guideline on how to 
add a new board definition. 

The information needed to create a board definition comes from the 
boards datasheet and/or schematic.  To make it easy to trace back 
to the original documentation the port names should match the net 
names in the documentation / schematic with a few exceptions.  The 
port names should be lowercase (this will be one difference from 
the documentation / schematic).  

The board definitions are a subclass of the `FPGA` class.  The FPGA 
information is captured in the class attributes. 



Example: XESS CAT board
-----------------------
The following is a minimal example creating a board definition for 
the XESS CAT board.  From the `CAT board schematics`_ the port
definitions can be defined.

.. code-block:: python


    class CATBoard(FPGA):
        vendor = 'lattice'
        family = 'ice40'
        device = 'HX8K'
        packet = 'CT256'
        _name = 'catboard'
    
        default_clocks = {
            'clock': dict(freqeuncy=100e6, pins=('C8',))    
        }
    
        default_ports = {
            'led': dict(pins=('A9', 'B8', 'A7', 'B7',)),
            'sw': dict(pins=('A16', 'B9',)),
            'dipsw': dict(pins=('C6', 'C5', 'C4', 'C3',)),
            'hdr1': dict(pins=('J1', 'K1', 'H1', 'J2', )),
        }
        
        
.. _CAT board schematics : https://github.com/xesscorp/CAT-Board


Extending definitions
----------------------
In many situations the top-level module ports might not match the 
default ports in the board definition or the user might want to 
create a different board definition.  

Mapping port names
^^^^^^^^^^^^^^^^^^
There are two functions available in a specific board definition 
object:  ``add_port`` and ``add_port_name``.  When the pin is known
use ``add_port`` and when the default port name is known but a
different name is desired use ``add_port_name`` to add a new port
name that maps to the properties of an existing port.  See the 
``pone`` example for an ``add_port_name`` use.

Creating a custom board definition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Custom board defintions can be created from the standard board
definitions contained in the `rhea.build.boards` collection.
For example, a board might
have many connectors or generic IO.  The user could have a boards
with specific hardware attached.  In these cases the user many
wish to create a new custom board definition. 

.. code-block:: python


     class MyCustomBoard(Xula2):
         # overriding the default ports, inherit the default 
         # clocks.  The default ports in this cause reprsent
         # the various widgets connected to the Xula2+stickit
         default_ports = {
             'leds': dict(pins=('R7', 'R15', 'R16', 'M15',)),
             'btns': dict(pins=('F1', 'F2', 'E1', 'E2',))
         }

