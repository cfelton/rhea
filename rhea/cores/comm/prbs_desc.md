
<!-- 
# Need a good description of characteristic polynomial, feedback
# polynomial, and how a psuedo random bit sequence is generted 
# from the generator polynomials.  This will move to the 
`prbs_generate` and `prbs_check` doc strings.
-->

Characteristic Polynomial Mapping
---------------------------------
To define the LFSR sequence a "characteristic" polynomial is required.
This modules expects the polynomial described by the "taps" list.  The
taps list is the delay elements that feed an XOR in a Galois LFSR
configuration.  Example:

    P(x) = x^4 + x^3 + x + 1 is taps=(0,2,)

The `taps` is used because it is a compact form, where as the common
Poly representation would be explicit.  For the P(x) example above
Poly=[1,1,0,1,1].  For large bit-width LFSRs the tap representation
is more compact.  To convert from characteristic polynomial to the taps
representation simply subtract one from the nomial order and discard
x^0 and x^N.
