* FPU_IEEE754 Behavioral SPICE — ngspice compatible
* Type: sequential
.TITLE fpu_ieee754

* Power supply
VDD VDD 0 DC 5

Vclk clk 0 PULSE(0 5 0 1n 1n 5n 10n)
Va a 0 PULSE(0 5 0 1n 1n 20n 40n)
Vb b 0 PULSE(0 5 0 1n 1n 40n 80n)


.TRAN 1n 320n

.PRINT TRAN V(clk) V(a) V(b)
.END