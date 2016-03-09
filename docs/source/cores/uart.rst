uart
----

The myHDL implementation of the  Universal Asynchronous 
Receiver/ Transmitter module
, which is a standard serial communication module between
devices. Uses a FIFOBus interface to communicate with other modules 
externally and also to communicate with other devices. The baudwith 
of the module can be set by setting the baudwidth parameter. UART
reads bit-wise starting on a low signal after which a fixed length
(baudwidth) no of bits can be read, after which the stop high 
signal is received(transmitted).

.. code-block:: python

    from rhea.cores.uart import uartlite
    from rhea.system import FIFOBus

    # ...
    # fpgalink interface
    # si - serial in, so - serial out line
    fifobu = FIFOBus()
    uart_inst = uartlite(glbl, fifobus, si, so)
    
    #comp is another core component or module
    comp = comp_inst(...)
    @always_comb
    def sync_read()
        comp.read_line.next = fifobus.read_data
        comp.read_strobe.next = not fifobus_empty
        comp.validity_check = fifobus.read_valid

    @always_comb
    def sync_write()
        fifobus.write_data.next = comp.write_line
        fifobus.write.next = comp.write_strobe    

    # ...


and so on(look into the examples for more). Note 
that the serial in/out lines are those from the UART's 
perspective.

Internally, the UART uses two FIFOBus interfaces for communication
between the the UART and the actual RX/TX fifos from which the data
is read.The UART has a uartlite module which instantiates the respective 
FIFOs and synchronises between the external FIFOBus interface and 
the interface to the two fifos.
