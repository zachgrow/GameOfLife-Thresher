# The Game Of Life Thresher
The "Game Of Life Thresher" looks for and tests stable seed configurations within Conway's Game of Life. 
Written for CS445/545 at Portland State University, Spring 2022

# Authors
Zach Grow, Logan Anderson, Chris Deacon, Daniel Tsegaw

# Usage
## Overview

Run the script 'generateSeed.py' to see a demonstration of the generator algorithms.

The generators themselves can be invoked from the commandline: try adding '-h' to see the command line options.

Invoke the seedTester from the command line by giving it a seed file to start with:

	seedTester.py testGlider.txt [-s size -t time]

The test program may also be added to your own Python program by including it and making a new object of the GameOfLife class; see the seedTester.py source for details.

## Seed Configuration

A "seed" or "pattern" in Conway's Game of Life is designated with a rectangular grid of "dark" and "lit" tiles. This program currently reads Plaintext-format patterns, which have a simple format: comments are specified on the line with a !, and the grid of cells is specified with . and O:

	!Name: Example Seed
	!This is some additional commentary.
	!
	.O.
	O.O
	.O.

The seed will be placed in the middle of the game world upon initialization. Invalid chars (ie anything that is not . or O) will be discarded from the input stream. Note that whitespace in the seed is significant: the above example is a 3x3 seed, but this one takes up a 5x5 space:

	.....
	..O..
	.O.O.
	..O..
	.....

 An example seed file has been included with this program: see testGlider.txt.

# Files
../.
	README.md			- this file
	generateSeeds.sh	- the demonstration script
	seedTester.py		- the Game of Life simulator and testing methods
	patterns/			- the set of pregenerated patterns
		testGlider.txt
	outputs/			- contains generated seed files (set fileFlag = True to enable saving seeds)
	geneticGenerator.py	- candidate GA algorithms
	geneticAlg.py
	neuralNetwork.py	- candidate NN algorithms	
	neural.py
	
