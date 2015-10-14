
# Examples
This directory contains examples for certain FPGA development
boards and conversion examples.  The FPGA examples build a system 
with the `rhea` cores and execute the FPGA toolflow.  

Most of the conversion examples are *core builders*, 
the conversion scipts will accept a handful of command-line arguments
that determine configuration of the converted core.  These can 
be used to create Verilog of VHDL version of the cores.

The examples are structured in the following directories:

   * **boards**:  This contains examples specific to FPGA development boards.
   
   * **build**:  Simple examples using the `rhea.build` FPGA toolflow automation. 
   
   * **cores**: Mainly conversion scripts for various cores. 
   
<!--
Thinking this should be removed and the current example here should be 
moved to a specific board.  In addition in `rhea` a submodules subpackage
should be created for common submodules.  The button-led toy example 
can be moved to the submodules and a thin top-lelel for various board 
exmamples ???
   * **design**: Design based 
-->   
   

<!--
Conversion example 
-->

<!--
FPGA board example
-->
