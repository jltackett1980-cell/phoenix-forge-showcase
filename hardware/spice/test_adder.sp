* HALF_ADDER - ngspice behavioral simulation
.TITLE half_adder

* Power supply
VDD VDD 0 DC 5

* Input stimulus (0V=logic0  5V=logic1)
Va a 0 PULSE(0 5 0 1n 1n 10n 20n)
Vb b 0 PULSE(0 5 0 1n 1n 40n 80n)

* Behavioral output sources (B sources)
* Threshold: >2.5V = logic 1

B_sum sum 0 V = (((V(a)>2.5)&&(V(b)<2.5))||((V(a)<2.5)&&(V(b)>2.5)))?5:0
B_carry carry 0 V = ((V(a)>2.5)&&(V(b)>2.5))?5:0

R_sum sum 0 10k
R_carry carry 0 10k

.TRAN 1n 160n

.PRINT TRAN V(a) V(b) V(sum) V(carry)
.END