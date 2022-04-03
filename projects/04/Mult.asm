// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

// Put your code here.
	// Initialize the product to 0
	@R2
	M=0

	// Check that X is > 0, then copy it to RAM[2]
	// as it will be used as the loop index
	@R0
	D=M
	@END
	D;JEQ
	@R3
	M=D    // Copy RAM[0] to RAM[2] this is our loop index
	
	// Check that Y is > 0
	@R1
	D=M
	@END
	D; JEQ	
	
	(LOOP)
		// See if index == 0, stop iteration if it is
		@END
		D;JEQ
		
		// Load Y then add it to the product
		@R1
		D=M
		@R2
		M=D+M
		
		// Decrement the index and start the loop again
		@R3
		D=M-1
		M=D
		@LOOP
		0;JMP  // Loop again		
	
	// Infinite loop to end the program so we don't run stuff
	// after we're done.
	(END)
	@END
	0;JMP