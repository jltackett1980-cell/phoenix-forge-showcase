* RISCV_CORE Behavioral SPICE — ngspice compatible
* Type: sequential
.TITLE riscv_core

* Power supply
VDD VDD 0 DC 5

Vclk clk 0 PULSE(0 5 0 1n 1n 5n 10n)
Vrst rst 0 PULSE(0 5 0 1n 1n 20n 40n)
Vinstr instr 0 PULSE(0 5 0 1n 1n 40n 80n)

B_pc pc 0 V = (V(rst)>2.5)?5:0
R_pc pc 0 10k

.TRAN 1n 320n

.PRINT TRAN V(clk) V(rst) V(instr) V(pc)
.END