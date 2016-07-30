
Video interfaces
----------------

.. autoclass:: rhea.cores.video.VideoMemory

.. autoclass:: rhea.cores.video.VGA

.. autoclass:: rhea.cores.video.HDMI


LT24 LCD display driver
-----------------------

.. Todo::

    general comments about the driver

.. autofunction:: rhea.cores.video.lt24lcd



VGA driver
----------
In ``rhea.cores.video`` is a basic VGA driver ``vga_sync``.  This
driver will read from an :class:`VideoMemory` interface and generate
the VGA signals to the :class:`VGA`.  The VGA controller is a simple
circuit that generates the required VGA signals from a small number of
parameters.  These parameters in turn generate the video region map
that defines the monitor.

The VGA driver generates a bunch of *timing parameters* based on the
monitor attributes previously defined.  The following is an example
of the timing parameters generated given the parameters:

    resolution: 800 x 600
    refresh_rate: 60 Hz
    line_rate: 31250

    Video parameters in ticks
      period ........................ 125000000.000, 8e-09
      hticks ........................ 4000.000000
      vticks ........................ 2083333.333333
      A: full line: ................. 3999, (31250.00 Hz)
      B: horizontal pulse width: .... 500
      C: horizontal back porch:...... 250
      D: horizontal active: ......... 3124
      E: horizontal front porch: .... 125
      F: full screen ................ 2083333, (60.00 Hz)
      P: vertical pulse width ....... 8000
      Q: vertical back porch ........ 112833
      R: all lines .................. 1919999
      S: vertical front porch ....... 42500
      X: pixel clock count .......... 5.000
      Z: pixel count: ............... 307200


The timing parameters are defined in clock ticks unless otherwise
specified.  The above has a system clock of 125MHz, the full screen
(including porches) is 2083333 clock ticks @ 60 Hz.  From these
timing parameters the vertical sync and horizontal sync signals
are generated.


.. autofunction:: rhea.cores.video.vga_sync



