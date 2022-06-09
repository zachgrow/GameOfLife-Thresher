#!/usr/bin/env python3

# geneticGenerator.py
# Author: Zach Grow
# CS445, Spring 2022

# This program uses GA methods to produce a maximally stable GoL seed.
# Adapted from methods originally written by zGrow for CS441, Winter 2022

# EXTERNALIA
import argparse
import math
import random as rng
import numpy as np
#import geneticAlg as galgo
import seedTester as st

# FIXME: hardcoded values are here for debugging purposes
geneSize = 16
seedWidth = 4
mutationRate = 100
fileFlag = False # set this to True to write output seeds to files

# PRIMITIVES
def randomGene(length):
	# Creates a random gene string of binary digits of the given length
	newGene = ''
	for index in range(length):
		newGene += str(rng.randint(0, 1))
	return newGene

def randomPopnStrings(geneSize, popSize):
	# Creates and returns a set of candidate genes from the givens
	# - give each one a random solution string
	# - generate the fitness value of the child
	genPop = list();
	for index in range(popSize):
		newGene = randomGene(geneSize)
		genPop.append((newGene, fitness(newGene)))
	return genPop

def randomPopnMatrix(geneSize, popSize):
	# Creates and returns a NumPy matrix containing the set of genes
	genPop = np.zeros((popSize, geneSize))
	for i in range(popSize):
		for j in range(geneSize):
			genPop[i, j] = rng.randint(0, 1)
	return genPop

def fitness(gene):
	# Calculates the fitness of a genetic seed by running it through the tester
	# Obtain the raw performance data: (live tiles, world size), [stability rates]
	# Note that len(stability rates) == total convolutions of simulation
	fitnessData = st.runSimulation(st.strToSeed(gene, seedWidth))
	# We choose to define a "fit" gene as one that is stable:
	# - it should not over/underpopulate, but should settle at some nonzero
	# population count, ie the average density does not fluctuate (much)
	# - it should reach that non-fluctuation point quickly: if two seeds have
	# equal density rates, the seed with a shorter sim duration is better
	density = fitnessData[0][0] / fitnessData[0][1]
	duration = len(fitnessData[1])
	return ((density / duration), duration)

def propagate(foo, bar):
	# Performs a propagation operation on the two given GameStates
	# Returns the created child GameStates as a tuple of States
	geneLength = len(foo)
	assert len(foo) == len(bar), "Gene length mismatch!"
	crossover = rng.randint(0, geneLength - 1)
	#print("1: ", foo, " + 2: ", bar, " @", crossover) # DEBUG
	firstChild = ''
	secondChild = ''
	for i in range(geneLength):
		if i < crossover:
			firstChild += foo[i]
			secondChild += bar[i]
		else:
			firstChild += bar[i]
			secondChild += foo[i]
	#print("N1:", firstChild) # DEBUG
	#print("N2:", secondChild) # DEBUG
	return (firstChild, secondChild)

def mutate(subject):
	# Performs a requested mutation on a randomly chosen gene of the subject
	#print("Mutating", subject) # DEBUG
	genePosition = rng.randint(0, len(subject) - 1)
	if subject[genePosition] == '0':
		subject = subject[:genePosition] + '1' + subject[genePosition+1:]
	else:
		subject = subject[:genePosition] + '0' + subject[genePosition+1:]
	#print("! Mutated", subject, "@", genePosition) # DEBUG
	return subject

def printAsSeed(seedStr, width, liveChar='O', deadChar='.'):
	# Displays the given seed string as a formatted GoL seed
	currentCol = 0
	lineStr = ''
	for entry in seedStr:
		if entry == '0':
			lineStr += deadChar
		elif entry == '1':
			lineStr += liveChar
		else:
			lineStr += 'X'
		currentCol += 1
		if currentCol == width:
			lineStr += '\n'
			currentCol = 0
	print(lineStr)

def saveToPlaintext(target, width, filename=''):
	# Saves the given seed as a Plaintext file
	# If a filename is not specified, then will be saved with timestamp
	#print("T:", target) # DEBUG
	import hashlib
	seedhash = hashlib.md5(target[0].encode('utf-8')).hexdigest()
	import time
	datestamp = time.strftime("%Y%m%d")
	timestamp = time.strftime("%H%M%S")
	if filename == '':
		filename = datestamp + '-' + timestamp + '_' + 'seed-' + seedhash[:8] + '.txt'
	#print(filename)
	newFile = open("outputs/" + filename, "w")
	newFile.write("! seed: " + seedhash + '\n')
	newFile.write("! This seed was created with geneticGenerator.py\n")
	newFile.write("! Generated on " + time.strftime("%c") + " at " + time.strftime("%X") + '\n')
	newFile.write("! Runtime: " + str(target[1][1]) + " iterations\n")
	newFile.write("! Stability (density/time): " + str(target[1][0]) + '\n')
	col = 0
	for entry in target[0]:
		newFile.write(entry)
		col += 1
		if col == width:
			col = 0
			newFile.write('\n')
	newFile.close()

# FIXME: a fxn that builds candidates from a given gene

# MAIN
def main():
	# Parse the command line arguments
	cmdArgs = argparse.ArgumentParser(description="Uses genetic algorithms to produce a maximally stable seed.")
	cmdArgs.add_argument('-f', '--file', type=str, help="Use a Plaintext seed as the starting input.")
	cmdArgs.add_argument('-p', '--population', type=int, default=20, help="Specify the size of the starting population of genetic candidates.")
	cmdArgs.add_argument('-s', '--size', type=int, default=16, help="Sets the length of the genetic strings, if no file is specified.")
	argVals = cmdArgs.parse_args()
	# FIXME: need handling for seed file inputs
	populationSize = argVals.population
	#geneSize = argVals.size # FIXME: has been hardcoded at top of file!
	#mutationRate = argVals.rate # FIXME: has been hardcoded at top of file!
	# METHOD
	# Generate the initial population from the specified parameters
	# either from a random seed with given params or from a specified seed file
	# population[]: (seed string, fitness value)
	population = randomPopnStrings(geneSize, populationSize)
	# Determine how many parents will be in the propagation pool
	# Always produce a whole integer
	parentPoolSize = math.floor(len(population) / 2)
	# Round down to nearest even value if needed
	if parentPoolSize % 2 == 1:
		parentPoolSize -= 1
	# *** GENERATIONAL LOOP STARTS HERE
	# Sort the population in descending order by their fitness rating
	population.sort(reverse = True, key = lambda x: x[1])
	# Slice the pool of candidate parents from the general population
	parentPool = population[0:parentPoolSize]
	#print("P:", len(parentPool)) # DEBUG
	# Calculate the sum total fitness of the propagation pool
	groupFitness = 0
	for single in parentPool:
		groupFitness += single[1][0]
	# Add parents to the pool, selecting proportional to their fitness
	# To obtain a normalized probability: p = this.fitness / groupFitness
	# LOOP METHOD
	# Is the current parent's fitness LOWER or HIGHER than the selValue?
	# If parent.fitness < selValue
	# -> check next parent
	# If parent.fitness >= selValue
	# -> select this parent
	# where parent.fitness = (sum of all previous fitnesses)
	remainingParents = parentPoolSize
	while remainingParents > 0:
		# The lucky singles in the front get to be the defaults
		firstParent = parentPool[0]
		secondParent = parentPool[1]
		# Begin randomized selection
		selection = rng.uniform(0.0, 1.0)
		#print("selvalue: ", selection) # DEBUG
		currentProbability = 0
		for j in parentPool:
			currentProbability += (j[1][0] / groupFitness)
			#print("C1: ", currentProbability) # DEBUG
			if selection <= currentProbability:
				firstParent = j
				remainingParents -= 1
				break
		#print(firstParent) # DEBUG
		#select second
		selection = rng.uniform(0.0, 1.0)
		#print("selvalue: ", selection) # DEBUG
		currentProbability = 0
		for k in parentPool:
			currentProbability += (k[1][0] / groupFitness)
			#print("C2: ", currentProbability) # DEBUG
			if selection <= currentProbability:
				# select this one, as long as it's not the same as 1st
				if k[0] != firstParent[0]:
					secondParent = k
					remainingParents -= 1
					break
		#print(secondParent.genes) # DEBUG
		# Propagate the parents to produce two children
		#print("PROPAGATE: ", firstParent[0], secondParent[0]) # DEBUG
		newKids = propagate(firstParent[0], secondParent[0])
		#print("New children:", newKids[0], newKids[1]) # DEBUG
		# Check to see if any of the children genes mutate
		firstChance = rng.randint(0, 100)
		#print("chance value:", mutateChance, "mutation rate:", mutationRate) # DEBUG
		if firstChance < mutationRate:
			#print("Mutating first child") # DEBUG
			mutate(newKids[0])
		secondChance = rng.randint(0, 100)
		if secondChance < mutationRate:
			#print("Mutating second child") # DEBUG
			mutate(newKids[1])
		#print("New children:", newKids[0], newKids[1]) # DEBUG
		population.append((newKids[0], fitness(newKids[0])))
		population.append((newKids[1], fitness(newKids[1])))
		#print("New citizens:", population[-1], population[-2]) # DEBUG
		# Repeat until no more parents left
	# *** GENERATIONAL LOOP END
	# Sort one final time so as to place the most fit specimens at the top
	population.sort(reverse = True, key = lambda x: x[1])
	bestSeed = population[0]
	# Display the results for the top three contenders
	print("RESULTS:")
	for index in range(3):
		if population[index] == population[index + 1]: index += 1 # uniques only
		print("Stability:", population[index][1][0], ", Sim duration:", population[index][1][1])
		printAsSeed(population[index][0], seedWidth)
		if fileFlag == True: saveToPlaintext(population[index], seedWidth)

# The self-invocation method
if __name__ == "__main__":
	main()
# EOF
