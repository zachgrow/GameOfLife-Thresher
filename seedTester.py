#!/usr/bin/env python3

# seedTester.py
# Authors: Zach Grow
# Written for CS445 at PSU, Spring 2022

# This program takes in a seed configuration for Conway's Game of Life and
# runs it through a specified set of simulation rules. When finished, it
# displays some simple output data, as well as the final game state.

# EXTERNALIA
import argparse
import random as rng
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as scp

# PRIMITIVES
liveChar = 'O'
deadChar = '.'
fullKernel = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
#orthoKernel = [[0, 1, 0], [1, 0, 1], [0, 1, 0]] #note: untested

# CLASSES
class GameOfLife:
	#__init__(self, seedString, sideLength, gameDuration, ruleset):
	# FIXME: Alternative rulesets cannot be specified yet
	def __init__(self, seedFilename, sideLength, gameDuration):
		# Acquire environment variables
		self.qtyLive = self.qtyDead = 0
		# duration, state, initialSeed, starting x/yPos
		self.duration = gameDuration
		self.currentTurn = 0
		# Build an empty game world
		self.state = np.zeros((sideLength, sideLength), dtype=bool)
		self.worldSize = sideLength ** 2
		# Obtain the seed config from the input file
		self.initialSeed = self.readSeedFile(seedFilename)
		# Apply the seed to the game world
		# The game world's geography wraps around
		# -> all starting positions are equally viable
		# -->> start from midpoint of field for simplicity
		xPos = int(sideLength / 2 - self.initialSeed.shape[0])
		yPos = int(sideLength / 2 - self.initialSeed.shape[1])
		for yOffset in range(self.initialSeed.shape[1]):
			for xOffset in range(self.initialSeed.shape[0]):
				self.state[(xPos + xOffset)][(yPos + yOffset)] = self.initialSeed[xOffset][yOffset]
		self.stability() # updates qtyLive, qtyDead

	def readSeedFile(self, filename):
		# Reads in the specified seed, printing any comments it discovers, and
		# then creates and returns a matching Numpy array
		seedLineIndex = 0
		seedVals = []
		with open(filename) as target:
			for line in target:
				# if the line starts with !, print it
				if (line.startswith('!')):
					print(line[1:], end='')
				# Otherwise, if it's got the right starting val, read it
				elif (line.startswith('.')) or (line.startswith('O')):
					seedVals.append(self.parsePlaintextLine(line))
				# Elsewise, there was an error
				else:
					print("! An invalid value was encountered while reading the seed file:", line.start())
					return 0
		# Use the seedVals to build the seedMx: list length, entry length
		mxWidth = len(seedVals[0])
		mxHeight = len(seedVals)
		mxSize = (mxWidth, mxHeight)
		seedMx = np.zeros(mxSize, dtype=bool)
		#for line in seedVals:
		for row in range(mxHeight):
			for col in range(mxWidth):
				seedMx[row][col] = seedVals[row][col]
		return seedMx

	def parsePlaintextLine(self, seedLine):
		# Reads in a string of . and O and returns an array of 0/1s
		seedValues = np.zeros(len(seedLine) - 1)
		target = 0
		for index in range(len(seedLine) - 1):
			if seedLine[index] == '.':
				seedValues[index] = 0
			elif seedLine[index] == 'O':
				seedValues[index] = 1
			else:
				print("ERROR: Discarding invalid char:", seedValues[index])
				pass
		return seedValues

	def displaySimpleGrid(self):
		# Primitive method for displaying the game grid, for troubleshooting
		for row in self.state:
			for entry in row:
				if entry == True: print(liveChar, end='')
				else: print(deadChar, end='')
			print('\n', end='')

	def calculate(self, inputMx, kernelMx):
		# Applies convolution to the supplied matrices
		# 1 For each entry in A,
		# 2 Apply 2d convolution of K with sub-matrix centered on entry_A
		# 3 Place result of convolution at entry_B
		# Returns a matrix where each entry is the count of its live neighbors
		outputMx = np.zeros(np.shape(inputMx), dtype=int)
		outputMx = scp.convolve2d(inputMx, kernelMx, mode='same', boundary='wrap')
		return outputMx

	def applyConwayRuleset(self, inputMx):
		# Uses the given matrix of convolution sums and the previous state
		# Applies the Conway default ruleset (FIXME: RLE code?)
		outputMx = np.zeros(np.shape(inputMx), dtype=bool)
		# Any tile with 2 OR 3 neighbors is ALIVE
		outputMx[np.where((inputMx == 2) & (self.state == 1))] = 1
		outputMx[np.where((inputMx == 3) & (self.state == 1))] = 1
		# Any DEAD tile with 2 neighbors is ALIVE
		outputMx[np.where((inputMx == 2) & (self.state == 0))] = 1
		return outputMx

	def stability(self):
		# Counts the number of living tiles in the game world to assess the
		# stability rating (the ratio between live/dead tiles)
		# If the stability rating is too low (D >>> L) or too high (D <<< L)
		# then this will return false
		# FIXME: set a smarter lower threshold to prevent too-early halting
		# FIXME: allow defn of ratio bounds for this at CLI
		continueFlag = True
		self.qtyLive = np.count_nonzero(self.state)
		self.qtyDead = self.worldSize - self.qtyLive
		popRatio = self.qtyLive / self.qtyDead
		#print(self.qtyLive, "/", self.qtyDead, ":", self.worldSize, "@", popRatio) # DEBUG
		if popRatio < 0.001 and self.currentTurn > 25: # underpopulated
			print("\nWorld terminated early due to underpopulation")
			continueFlag = False
		if popRatio > 0.99: # overpopulated
			print("\nWorld terminated early due to overpopulation")
			continueFlag = False
		return continueFlag

	def runSimulation(self, display=False):
		# Runs the GoL simulation process
		# Defaults to no display for faster processing times
		# Set display=True to observe the GoL simulation in realtime
		# FIXME: implement display code lol
		# METHOD
		# - Given the initial state A and a kernel matrix K,
		# 1 Count the number of LIVE neighbors at each entry to produce mx B
		# 2 Apply the specified ruleset to B to produce a new state C
		# 3 Define C as the new input A for the next iteration
		template = fullKernel # FIXME: allow runtime selection
		print("Starting simulation:")
		for iteration in range(self.duration):
			self.currentTurn += 1
			#print(iteration + 1, "/", self.duration, end='\r')
			print("Iteration:", self.currentTurn, "/", self.duration, end='\r')
			sumMatrix = self.calculate(self.state, template)
			newState = self.applyConwayRuleset(sumMatrix)
			# Information about the new state should be gathered at this point
			self.state = newState
			# if self.state is outside defns of stability
			if self.stability() == False:
				break
		print("\nSimulation is finished")

	def displayResults(self):
		# Shows the final results of the simulation
		print("Final world state:")
		self.displaySimpleGrid()

# MAIN
def main():
	# Process command line argVals
	cmdArgs = argparse.ArgumentParser(description="Runs Conway's Game of Life, given an initial seed configuration.",
			epilog="See the README for information about the seed file specification.")
	cmdArgs.add_argument('seedFile', type=str, help="the file that contains the initial seed")
	cmdArgs.add_argument('-s', '--size', type=int, default=100, help="sets the side length of the world grid")
	cmdArgs.add_argument('-t', '--time', type=int, default=100, help="sets the maximum number of turns to simulate")
	# FIXME: add flag to print contents of initial seed at program start?
	argVals = cmdArgs.parse_args()
	# Initialize a new game
	# Open the seed file and read it out into a string object
	currentWorld = GameOfLife(argVals.seedFile, argVals.size, argVals.time)
	currentWorld.runSimulation()
	#currentWorld.displayResults()

# The self-invocation method
if __name__ == "__main__":
	main()
# EOF
