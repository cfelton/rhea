

/**
 * small wrapper for the MyHDL module
 */

module fpgalink_led_top
(
 input  wire  IFCLK,
 input  wire  RST,
 output wire  SLWR,
 output wire  SLRD,
 output wire  SLOE,
 inout  wire [7:0] FDIO,
 output wire [1:0] ADDR,
 input  wire FLAGA,
 input  wire FLAGB,
 input  wire FLAGC,
 input  wire FLAGD,
 output wire PKTEND,
 output wire [7:0] LEDS
);

   wire [7:0] fdi, fdo;
   wire       fds;
   assign fdi = FDIO;
   assign FDIO = (fds) ? fdo : 8'bz;

   fpgalink_led 
     U1
       (
	.IFCLK(IFCLK),
	.RST(RST),
	.SLWR(SLWR),
	.SLRD(SLRD),
	.SLOE(SLOE),
	.FDI(fdi),
	.FDO(fdo),
	.FDS(fds),
	.ADDR(ADDR),
	.FLAGA(FLAGA),
	.FLAGB(FLAGB),
	.FLAGC(FLAGC),
	.FLAGD(FLAGD),
	.PKTEND(PKTEND),
	.LEDS(LEDS) );  		   

endmodule
   