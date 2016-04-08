# -------------------------------------------------------------------------- #
# clock contraints given clock def in design 
create_clock -period 20.0000000 [get_ports clock]

# Automatically apply a generate clock on the output of phase-locked loops (PLLs)
# This command can be safely left in the SDC even if no PLLs exist in the design
derive_pll_clocks

# Constrain the input I/O path
set_input_delay -clock clock -max 3 [all_inputs]
set_input_delay -clock clock -min 2 [all_inputs]

# Constrain the output I/O path
set_output_delay -clock clock 2 [all_outputs]

# -------------------------------------------------------------------------- #
