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
import gameUtils # The custom set of GoL tools

# PRIMITIVES
fullKernel = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
#orthoKernel = [[0, 1, 0], [1, 0, 1], [0, 1, 0]] #note: untested

def runSimulation(seed, sideLength=10, maxDuration=1000):
	# Performs a GoL simulation run using the inputs
	# The seed should be a numpy matrix of boolean/binary values
	# WARN: The seed will NOT be reshaped! Flattened arrays produce flat seeds
	#print(seed)
	#print(seed.shape)
	assert seed.shape[0] < sideLength, "Seed is too big for the game world!"
	assert seed.shape[1] < sideLength, "Seed is too big for the game world!"
	# FIXME: allow realtime display of the simulation
	# Returns the vital stats of the simulation run:
	#	a tuple containing the live cell counts and world size (produces density)
	#	the set of stability rates generated across the sim lifetime
	# Setting the kernel is equivalent to choosing which neighbors will be
	# counted when convolving the world state
	# FIXME: allow selection of other rulesets (kernels)
	kernel = fullKernel
	# Initialize a new game
	currentWorld = gameUtils.GameOfLife(seed, sideLength)
	# Begin the simulation process
	convolutions = 0
	stabilityRates = []
	stabilityRates.append(calcStability(currentWorld, 1))
	stabilityDelta = 0.0005 # FIXME: add this to CLI args
	previousStability = 0
	#print("Running simulation...") # DEBUG
	for step in range(1, maxDuration):
		#print("Iteration: ", step, "/", maxDuration, end='\r') # DEBUG
		neighborMx = currentWorld.convolve(kernel)
		convolutions += 1
		newState = currentWorld.applyConwayRules(neighborMx)
		# Update to the new world state
		currentWorld.state = newState
		# Check the current stability and chart it
		stabilityRates.append(calcStability(currentWorld, convolutions))
		# calc the new stability average and check the rate of change on the
		# last ten stability rates
		if len(stabilityRates) > 10:
			averageStability = sum(stabilityRates[-10:-1]) / 10
			if abs(averageStability - previousStability) < stabilityDelta:
				break
		# If the world's become unstable, then halt
		if currentWorld.qtyLive == 0:
			# halt due to extinction
			break
		if currentWorld.calcDensity() > 0.9998:
			break
	#print("Simulation has finished") # DEBUG
	return ((currentWorld.qtyLive, currentWorld.worldSize), stabilityRates)

def checkStability(target, currentTurn):
	# Counts the number of living tiles in the game world to assess the
	# stability rating (the ratio between live/dead tiles)
	# If the stability rating is too low (D >>> L) or too high (D <<< L)
	# then this will return false
	# FIXME: set a smarter lower threshold to prevent too-early halting
	# FIXME: allow defn of ratio bounds for this at CLI
	stability = calcStability(target, currentTurn)
	if stability < 0.0001 and currentTurn > 10:
		print("\nWorld terminated early due to underpopulation")
		return False
	if stability > 0.9998:
		print("\nWorld terminated due to overpopulation")
		return False
	return True

def calcStability(target, currentTurn):
	return (target.calcDensity() / currentTurn)

def strToSeed(seedStr, width):
	# Generates a numpy matrix from the given binary or Plaintext string
	# Handles rectangular seeds by calculating the second dim of the array
	size = len(seedStr)
	height = int(size / width)
	assert (width * height) == size, "Dimension mismatch encountered!"
	seedMx = np.zeros(size, dtype=int)
	for index in range(size):
		if seedStr[index] == '1': seedMx[index] = True # binary True
		if seedStr[index] == 'O': seedMx[index] = True # Plaintext LIVE
	seedMx = np.reshape(seedMx, (width, height))
	return seedMx

def displayResults(target):
	# Shows the final results of the simulation
	print("Final world state:")
	finalState = target.mxToStringList(target.state)
	for line in finalState:
		print(line)

# MAIN
def main():
	# Allows running this program as a CLI tool, for script automation
	# Process command line argVals
	cmdArgs = argparse.ArgumentParser(description="Runs Conway's Game of Life, given an initial seed configuration.",
			epilog="See the README for information about the seed file specification.")
	cmdArgs.add_argument('seedFile', type=str, help="the file that contains the initial seed")
	cmdArgs.add_argument('-s', '--size', type=int, default=100, help="sets the side length of the world grid")
	cmdArgs.add_argument('-t', '--time', type=int, default=100, help="sets the maximum number of turns to simulate")
	# FIXME: add flag to print contents of initial seed at program start?
	print("Initializing environment...")
	argVals = cmdArgs.parse_args()
	maxDuration = argVals.time
	# FIXME: allow selection of other kernel matrices
	kernel = fullKernel
	# Initialize a new game
	# FIXME: need to fix loading seeds from file for demo mode
	# ie load the seed from file and THEN pass to the call below
	#currentWorld = gameUtils.GameOfLife(argVals.seedFile, argVals.size)
	assert currentWorld, "Sorry, this is broken right now :( "
	# Begin the simulation process
	convolutions = 0
	stabilityRates = []
	stabilityDelta = 0.0001 # FIXME: add this to CLI args
	previousStability = 0
	print("Running simulation...")
	for step in range(1, maxDuration):
		#print("Iteration: ", step, "/", maxDuration, end='\r') # DEBUG
		neighborMx = currentWorld.convolve(kernel)
		convolutions += 1
		newState = currentWorld.applyConwayRules(neighborMx)
		# Check the current stability and chart it
		stabilityRates.append(calcStability(currentWorld, convolutions))
		# Update to the new world state
		currentWorld.state = newState
		# If the world's become unstable, then halt
		if stabilityRates[-1] < 0.0001 and step > 10:
			# early termination due to extinction
			break
		if stabilityRates[-1] > 0.9998:
		# termination due to overpopulation
			break
		# calc the new stability average and check the rate of change
		if len(stabilityRates) > 10:
			averageStability = sum(stabilityRates[-10:-1]) / 10
			if abs(averageStability - previousStability) < stabilityDelta:
				break
	print("Simulation has finished")
	#displayResults(currentWorld)
	print("Final Results:")
	print("Stability: ", stabilityRates[-1])
	print("Density: ", currentWorld.calcDensity(), "(", currentWorld.qtyLive, "/", currentWorld.qtyDead, ")")
	print("Runtime: ", convolutions, "iterations")

# The self-invocation method
if __name__ == "__main__":
	main()
# EOF
