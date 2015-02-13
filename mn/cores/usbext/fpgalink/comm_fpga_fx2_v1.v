//
// Copyright (C) 2009-2012 Chris McClelland
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
module
   comm_fpga_fx2_v1(
		 input wire 	   clk_in, // 48MHz clock from FX2LP
		 input wire 	   reset_in, // synchronous active-high reset
		 
		 // FX2LP interface ---------------------------------------------------------------------------
		 output reg 	   fx2FifoSel_out, // select FIFO: '0' for EP2OUT, '1' for EP6IN
		 //inout wire [7:0]  fx2Data_io, // 8-bit data to/from FX2LP
		 input wire [7:0]  fx2Data_in,
		 output wire [7:0]  fx2Data_out,
		 output wire fx2Data_sel,
		 
		 // When EP2OUT selected:
		 output wire 	   fx2Read_out, // asserted (active-low) when reading from FX2LP
		 input wire 	   fx2GotData_in, // asserted (active-high) when FX2LP has data for us
		 
		 // When EP6IN selected:
		 output wire 	   fx2Write_out, // asserted (active-low) when writing to FX2LP
		 input wire 	   fx2GotRoom_in, // asserted (active-high) when FX2LP has room for more data from us
		 output reg 	   fx2PktEnd_out, // asserted (active-low) when a host read needs to be committed early
		 
		 // Channel read/write interface --------------------------------------------------------------
		 output wire [6:0] chanAddr_out, // the selected channel (0-127)
		 
		 // Host >> FPGA pipe:
		 output wire [7:0] h2fData_out, // data lines used when the host writes to a channel
		 output reg 	   h2fValid_out, // '1' means "on the next clock rising edge, please accept the data on h2fData_out"
		 input wire 	   h2fReady_in, // channel logic can drive this low to say "I'm not ready for more data yet"
		 
		 // Host << FPGA pipe:
		 input wire [7:0]  f2hData_in, // data lines used when the host reads from a channel
		 input wire 	   f2hValid_in, // channel logic can drive this low to say "I don't have data ready for you"
		 output reg 	   f2hReady_out     // '1' means "on the next clock rising edge, put your next byte of data on f2hData_in"
		 );
   
   // The read/write nomenclature here refers to the FPGA reading and writing the FX2LP FIFOs, and is therefore
   // of the opposite sense to the host's read and write. So host reads are fulfilled in the S_WRITE state, and
   // vice-versa. Apologies for the confusion.
   localparam[3:0] S_IDLE                    = 4'h0;     // wait for requst from host & register chanAddr & isWrite
   localparam[3:0] S_GET_COUNT0              = 4'h1;     // register most significant byte of message length
   localparam[3:0] S_GET_COUNT1              = 4'h2;     // register next byte of message length
   localparam[3:0] S_GET_COUNT2              = 4'h3;     // register next byte of message length
   localparam[3:0] S_GET_COUNT3              = 4'h4;     // register least significant byte of message length
   localparam[3:0] S_BEGIN_WRITE             = 4'h5;     // switch direction of FX2LP data bus
   localparam[3:0] S_WRITE                   = 4'h6;     // write data to FX2LP EP6IN FIFO, one byte at a time
   localparam[3:0] S_END_WRITE_ALIGNED       = 4'h7;     // end an aligned write (do not assert fx2PktEnd_out)
   localparam[3:0] S_END_WRITE_NONALIGNED    = 4'h8;     // end a nonaligned write (assert fx2PktEnd_out)
   localparam[3:0] S_READ                    = 4'h9;     // read data from FX2LP EP2OUT FIFO, one byte at a time
   
   localparam[1:0] FIFO_READ                 = 2'b10;    // assert fx2Read_out (active-low)
   localparam[1:0] FIFO_WRITE                = 2'b01;    // assert fx2Write_out (active-low)
   localparam[1:0] FIFO_NOP                  = 2'b11;    // assert nothing
   localparam      OUT_FIFO                  = 2'b0;     // EP2OUT
   localparam      IN_FIFO                   = 2'b1;     // EP6IN
   reg [3:0] 			   state_next, state         = S_IDLE;
   reg [1:0] 			   fifoOp                    = FIFO_NOP;
   reg [31:0] 			   count_next, count         = 32'h0;    // read/write count
   reg [6:0] 			   chanAddr_next, chanAddr   = 7'h00;    // channel being accessed (0-127)
   reg 				   isWrite_next, isWrite     = 1'b0;     // is this FX2LP FIFO access a write or a read?
   reg 				   isAligned_next, isAligned = 1'b0;     // is this FX2LP FIFO write block-aligned?
   reg [7:0] 			   dataOut;                              // data to be driven on fx2Data_io
   reg 				   driveBus;                             // whether or not to drive fx2Data_io
   
   // Infer registers
   always @(posedge clk_in)
     begin
	if ( reset_in == 1'b1 )
	  begin
	     state <= S_IDLE;
	     count <= 32'h0;
	     chanAddr <= 7'h00;
	     isWrite <= 1'b0;
	     isAligned <= 1'b0;
	  end
	else
	  begin
	     state <= state_next;
	     count <= count_next;
	     chanAddr <= chanAddr_next;
	     isWrite <= isWrite_next;
	     isAligned <= isAligned_next;
	  end
     end
   
   // Next state logic
   always @*
     begin
	state_next = state;
	count_next = count;
	chanAddr_next = chanAddr;
	isWrite_next = isWrite;       // is the FPGA writing to the FX2LP?
	isAligned_next = isAligned;   // does this FIFO write end on a block (512-byte) boundary?
	dataOut = 8'h00;
	driveBus = 1'b0;              // don't drive fx2Data_io by default
	fifoOp = FIFO_READ;           // read the FX2LP FIFO by default
	fx2PktEnd_out = 1'b1;         // inactive: FPGA does not commit a short packet.
	f2hReady_out = 1'b0;
	h2fValid_out = 1'b0;
	
	case ( state )
	  S_GET_COUNT0:
	    begin
	       fx2FifoSel_out = OUT_FIFO;  // Reading from FX2LP
	       if ( fx2GotData_in == 1'b1 )
		 begin
		    // The count high word high byte will be available on the next clock.
		    count_next[31:24] = fx2Data_in;
		    state_next = S_GET_COUNT1;
		 end
	    end
	  
	  S_GET_COUNT1:
	    begin
	       fx2FifoSel_out = OUT_FIFO;  // Reading from FX2LP
	       if ( fx2GotData_in == 1'b1 )
		 begin
		    // The count high word low byte will be available on the next clock.
		    count_next[23:16] = fx2Data_in;
		    state_next = S_GET_COUNT2;
		 end
	    end
	  
	  S_GET_COUNT2:
	    begin
	       fx2FifoSel_out = OUT_FIFO;  // Reading from FX2LP
	       if ( fx2GotData_in == 1'b1 )
		 begin
		    // The count low word high byte will be available on the next clock.
		    count_next[15:8] = fx2Data_in;
		    state_next = S_GET_COUNT3;
		 end
	    end
	  
	  S_GET_COUNT3:
	    begin
	       fx2FifoSel_out = OUT_FIFO;  // Reading from FX2LP
	       if ( fx2GotData_in == 1'b1 )
		 begin
		    // The count low word low byte will be available on the next clock.
		    count_next[7:0] = fx2Data_in;
		    if ( isWrite == 1'b1 )
		      state_next = S_BEGIN_WRITE;
		    else
		      state_next = S_READ;
		 end
	    end
	  
	  S_BEGIN_WRITE:
	    begin
	       fx2FifoSel_out = IN_FIFO;   // Writing to FX2LP
	       fifoOp = FIFO_NOP;
	       if ( count[8:0] == 9'b000000000 )
		 isAligned_next = 1'b1;
	       else
		 isAligned_next = 1'b0;
	       state_next = S_WRITE;
	    end
	  
	  S_WRITE:
	    begin
	       fx2FifoSel_out = IN_FIFO;   // Writing to FX2LP
	       if ( fx2GotRoom_in == 1'b1 )
		 f2hReady_out = 1'b1;
	       if ( fx2GotRoom_in == 1'b1 && f2hValid_in == 1'b1 )
		 begin
		    fifoOp = FIFO_WRITE;
		    dataOut = f2hData_in;
		    driveBus = 1'b1;
		    count_next = count - 1;
		    if ( count == 32'h1 )
		      begin
			 if ( isAligned == 1'b1 )
			   state_next = S_END_WRITE_ALIGNED;  // don't assert fx2PktEnd
			 else
			   state_next = S_END_WRITE_NONALIGNED;  // assert fx2PktEnd to commit small packet
		      end
		 end
	       else
		 fifoOp = FIFO_NOP;
	    end
	  
	  S_END_WRITE_ALIGNED:
	    begin
	       fx2FifoSel_out = IN_FIFO;   // Writing to FX2LP
	       fifoOp = FIFO_NOP;
	       state_next = S_IDLE;
	    end
	  
	  S_END_WRITE_NONALIGNED:
	    begin
	       fx2FifoSel_out = IN_FIFO;   // Writing to FX2LP
	       fifoOp = FIFO_NOP;
	       fx2PktEnd_out = 1'b0;       // Active: FPGA commits the packet early.
	       state_next = S_IDLE;
	    end
	  
	  S_READ:
	    begin
	       fx2FifoSel_out = OUT_FIFO;  // Reading from FX2LP
	       if ( fx2GotData_in == 1'b1 && h2fReady_in == 1'b1 )
		 begin
		    // A data byte will be available on the next clock
		    h2fValid_out = 1'b1;
		    count_next = count - 1;
		    if ( count == 32'h1 )
		      state_next = S_IDLE;
		 end
	       else
		 fifoOp = FIFO_NOP;
	    end
	  
	  // S_IDLE and others
	  default:
	    begin
	       fx2FifoSel_out = OUT_FIFO;  // Reading from FX2LP
	       if ( fx2GotData_in == 1'b1 )
		 begin
		    // The read/write flag and a seven-bit channel address will be available on
		    // the next clock edge.
		    chanAddr_next = fx2Data_in[6:0];
		    isWrite_next = fx2Data_in[7];
		    state_next = S_GET_COUNT0;
		 end
	    end
	endcase
     end
   
   // Drive stateless signals
   assign fx2Read_out = fifoOp[0];
   assign fx2Write_out = fifoOp[1];
   assign chanAddr_out = chanAddr;
   assign h2fData_out = fx2Data_in;
   //assign fx2Data_io = driveBus ? dataOut : 8'hZZ;
   assign fx2Data_out = dataOut;
   assign fx2Data_sel = driveBus;
   
			
endmodule