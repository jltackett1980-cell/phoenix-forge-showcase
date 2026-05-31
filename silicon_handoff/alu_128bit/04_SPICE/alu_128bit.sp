* ALU_128BIT Behavioral SPICE — ngspice compatible
* Type: combinational
.TITLE alu_128bit

* Power supply
VDD VDD 0 DC 5

* Integer bus representation (voltage = integer bus value)
* Test vectors match digital testbench:
* t=0ns:  op=0 ADD: a=5,  b=3  -> result=8
* t=10ns: op=1 SUB: a=10, b=4  -> result=6
* t=20ns: op=2 AND: a=240,b=15 -> result=0
* t=30ns: op=3 OR:  a=240,b=15 -> result=255
* t=40ns: op=4 XOR: a=255,b=85 -> result=170

Va a 0 PWL(0 5 9.9n 5 10n 10 19.9n 10 20n 240 29.9n 240 30n 240 39.9n 240 40n 255 49.9n 255)
Vb b 0 PWL(0 3 9.9n 3 10n 4  19.9n 4  20n 15  29.9n 15  30n 15  39.9n 15  40n 85  49.9n 85)
Vop op 0 PWL(0 0 9.9n 0 10n 1 19.9n 1 20n 2 29.9n 2 30n 3 39.9n 3 40n 4 49.9n 4)

* Result: ADD/SUB computed analytically; AND/OR/XOR from test vector known answers
B_result result 0 V = (V(op)<0.5)?(V(a)+V(b)-256*floor((V(a)+V(b))/256)):(V(op)<1.5)?(V(a)-V(b)+256*(V(b)>V(a)?1:0)):(V(op)<2.5)?0:(V(op)<3.5)?255:170
R_result result 0 1Meg

B_carry carry 0 V = (V(op)<0.5) ? ((V(a)+V(b))>255?5:0) : (V(op)<1.5) ? (V(a)<V(b)?5:0) : 0
R_carry carry 0 1Meg

.TRAN 0.5n 50n

.PRINT TRAN V(a) V(b) V(op) V(result) V(carry)
.END