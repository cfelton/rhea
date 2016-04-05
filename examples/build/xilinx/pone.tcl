#
#
# ISE implementation script
# create: Fri, 01 Apr 2016 02:14:51 +0000
# by: ex_pone.py
#
#
# set compile directory:
set compile_directory .
set top_name pone
set top pone
# set Project:
set proj pone
# change to the directory:
cd xilinx/
# set ucf file:
set constraints_file pone.ucf
# set variables:
project new pone.xise
project set family spartan3e
project set device XC3S500e
project set package VQ100
project set speed -4

# add hdl files:
xfile add pone.ucf
xfile add pone.v
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
