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

def checkStability(target, currentTurn):
	# Counts the number of living tiles in the game world to assess the
	# stability rating (the ratio between live/dead tiles)
	# If the stability rating is too low (D >>> L) or too high (D <<< L)
	# then this will return false
	# FIXME: set a smarter lower threshold to prevent too-early halting
	# FIXME: allow defn of ratio bounds for this at CLI
	continueFlag = True
	currentRatio = target.takeCensus()
	if currentRatio < 0.001 and currentTurn > 25: # underpopulated
		print("\nWorld terminated early due to underpopulation")
		continueFlag = False
	if currentRatio > 0.99: # overpopulated
		print("\nWorld terminated early due to overpopulation")
		continueFlag = False
	return continueFlag

def displayResults(target):
	# Shows the final results of the simulation
	print("Final world state:")
	finalState = target.mxToStringList(target.state)
	for line in finalState:
		print(line)

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
	maxDuration = argVals.time
	# FIXME: allow selection of other kernel matrices
	kernel = fullKernel
	# Initialize a new game
	currentWorld = gameUtils.GameOfLife(argVals.seedFile, argVals.size)
	# Begin the simulation process
	print("Starting simulation...")
	for step in range(maxDuration):
		print("Iteration: ", step + 1, "/", maxDuration, end='\r')
		neighborMx = currentWorld.calculate(kernel)
		newState = currentWorld.applyConwayRules(neighborMx)
		# Gather info about new world state HERE if desired
		currentWorld.state = newState
		if checkStability(currentWorld, step) == False:
			break
	print("\nSimulation has finished")
	displayResults(currentWorld)

# The self-invocation method
if __name__ == "__main__":
	main()
# EOF
