#
#
# ISE implementation script
# create: Fri, 01 Apr 2016 02:14:49 +0000
# by: ex_xula.py
#
#
# set compile directory:
set compile_directory .
set top_name xula2
set top xula2
# set Project:
set proj xula2
# change to the directory:
cd xilinx/
# set ucf file:
set constraints_file xula2.ucf
# set variables:
project new xula2.xise
project set family spartan6
project set device XC6SLX25
project set package FTG256
project set speed -2

# add hdl files:
xfile add xula2.ucf
xfile add xula2.v
# test if set_source_directory is set:
if { ! [catch {set source_directory $source_directory}]} {
  project set "Macro Search Path"
 $source_directory -process Translate
}
project set "Create Binary Configuration File" "true" -process "Generate Programming File"
 project set "FPGA Start-Up Clock" "JTAG Clock" -process "Generate Programming File" 
# run the implementation:
process run "Synthesize" 
process run "Translate" 
process run "Map" 
process run "Place & Route" 
process run "Generate Programming File" 
# close the project:
project close
