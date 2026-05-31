# SDC for fpu_ieee754 (sequential)
create_clock -name clk -period 10.0 [get_ports clk]
set_clock_uncertainty -setup 0.3 [get_clocks clk]
set_clock_uncertainty -hold  0.1 [get_clocks clk]
set_input_delay  -clock clk 2.0 [get_ports {a b}]
set_output_delay -clock clk 2.0 [get_ports {}]
set_load 0.05 [all_outputs]
