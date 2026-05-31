# SDC for alu_128bit (combinational — no clock)
create_clock -name vclk -period 20.0
set_input_delay  -clock vclk 2.0 [get_ports {a b op}]
set_output_delay -clock vclk 2.0 [get_ports {result carry zero}]
set_max_delay 15.0 -from [all_inputs] -to [all_outputs]
set_load 0.05 [all_outputs]
