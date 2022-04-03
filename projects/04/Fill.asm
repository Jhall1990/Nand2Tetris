// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
	(START)
		// Set and end val which is the start of the
		// the keyboard mem, not sure if this is the
		// best way to determine end of screen, but whatever.
		@KBD
		D=A
		@end
		M=D
		
		// Store addr as the location of of the screen mem
		@SCREEN
		D=A
		@addr
		M=D
		
		// See if any key is being held, if kb reg > 0
		// a key is being pressed.
		@KBD
		D=M
		
		// Set var fill to 1 if a key is being pressed otherwise 0
		// We'll use this later to fill the screen appropriately.
		@FILL
		D;JGT
		
		// Otherwise jump to @BLANK
		@BLANK
		D;JMP
	
	// Set the pix var to 1 then jump to the fill loop.
	(FILL)
		@pix
		M=-1
		@LOOP
		D;JMP
	
	// Set the pix var to 0 then jump to the fill loop.
	(BLANK)
		@pix
		M=0
		@LOOP
		D;JMP
		
	(LOOP)
		// Set the current @addr to the @pix val
		@pix
		D=M
		@addr
		A=M
		M=D
		
		// Increment addr
		@addr
		M=M+1
		
		// See if the screen is filled, jump to loop if it's
		// not, otherwise jump to start.
		@addr
		D=M
		@end
		D=D-M
		
		@START
		D;JEQ
		
		@LOOP
		D;JMP		