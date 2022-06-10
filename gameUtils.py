# gameUtils.py
# Authors: Zach Grow
# Written for CS445, Spring 2022

# Contains the base GameOfLife class and assorted utilities for interacting
# with it.

import numpy as np
import scipy.signal as scp

liveChar = 'O'
deadChar = '.'

def readSeedFile(filename):
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
				seedVals.append(parsePlaintextLine(line))
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
def mxToStringList(target):
	# Returns a string-list representation of a given matrix
	output = []
	for row in target:
		rowString = ''
		for entry in row:
			if entry: rowString += liveChar
			else: rowString += deadChar
		output.append(rowString)
	return output
def parsePlaintextLine(seedLine):
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

class GameOfLife:
	def __init__(self, seed, sideLength):
		# Define the internal environment variables
		self.qtyLive = 0
		self.qtyDead = 0
		self.density = 0
		self.popRatio = 0
		self.worldSize = sideLength ** 2
		# Build an empty game world
		self.state = np.zeros((sideLength, sideLength), dtype=bool)
		# Obtain the seed config from the input file
		#self.initialSeed = self.readSeedFile(seedFilename)
		self.initialSeed = seed
		# Apply the seed to the game world
		# The game world's geography wraps around
		# -> all starting positions are equally viable
		# -->> start from midpoint of field for simplicity
		xPos = int(sideLength / 2 - self.initialSeed.shape[0])
		yPos = int(sideLength / 2 - self.initialSeed.shape[1])
		for yOffset in range(self.initialSeed.shape[1]):
			for xOffset in range(self.initialSeed.shape[0]):
				self.state[(xPos + xOffset)][(yPos + yOffset)] = self.initialSeed[xOffset][yOffset]
		self.takeCensus() # updates qtyLive, qtyDead, popRatio with init vals
	def displaySimpleGrid(self):
		# Primitive method for displaying the game grid, for troubleshooting
		for row in self.state:
			for entry in row:
				if entry == True: print(liveChar, end='')
				else: print(deadChar, end='')
			print('\n', end='')
	def takeCensus(self):
		# Counts the number of live tiles in the game world and updates the
		# population counts of both live and dead tiles
		# Returns both values as a tuple
		self.qtyLive = np.count_nonzero(self.state)
		self.qtyDead = self.worldSize - self.qtyLive
		if self.qtyDead: self.popRatio = self.qtyLive / self.qtyDead
		return self.popRatio
	def calcDensity(self):
		# Calculates the density of the game world: liveTiles / totalTiles
		self.takeCensus()
		return self.qtyLive / self.worldSize
	def convolve(self, kernelMx):
		# Applies convolution to the supplied matrices
		# 1 For each entry in A,
		# 2 Apply 2d convolution of K with sub-matrix centered on entry_A
		# 3 Place result of convolution at entry_B
		# Returns a matrix where each entry is the count of its live neighbors
		outputMx = np.zeros(np.shape(self.state), dtype=int)
		outputMx = scp.convolve2d(self.state, kernelMx, mode='same', boundary='wrap')
		return outputMx
	def applyConwayRules(self, neighborMx):
		# Uses the given matrix of convolution sums and the previous state
		# Applies the Conway default ruleset (FIXME: RLE code?)
		outputMx = np.zeros(np.shape(neighborMx), dtype=bool)
		# Any tile with 2 OR 3 neighbors is ALIVE
		outputMx[np.where((neighborMx == 2) & (self.state == 1))] = 1
		outputMx[np.where((neighborMx == 3) & (self.state == 1))] = 1
		# Any DEAD tile with 2 neighbors is ALIVE
		outputMx[np.where((neighborMx == 2) & (self.state == 0))] = 1
		return outputMx

# EOF
