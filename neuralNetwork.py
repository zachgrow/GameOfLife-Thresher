#!/usr/bin/env python3

# neuralNetwork.py
# Authors: Logan Anderson, Zach Grow
# Written for CS445, Spring 2022

# This is the neural network approach to finding stable seeds

import argparse
import numpy as np
import random as rng
import seedTester as st
import gameUtils

#FIXME: magic numbers
seedWidth = 3 #FIXME: indexing goes bad for n > 3?
fileFlag = False

class neuralNetwork:
    def __init__(self, sideLength, hiddenLayerSize):
        self.worldSize = int(sideLength**2)
        #For the following lists, [0] is for the input layer and [1] is the hidden layer
        self.weights = []
        self.weights.append((np.random.rand(self.worldSize, hiddenLayerSize) * 0.1) - 0.05)
        self.weights.append((np.random.rand(hiddenLayerSize, self.worldSize) * 0.1) - 0.05)
        self.biases = []#Biases are using an implied 1. Since 1*w = w, the biases value is just w
        self.biases.append((np.random.rand(hiddenLayerSize) * 0.1) - 0.05)
        self.biases.append((np.random.rand(self.worldSize) * 0.1) - 0.05)
        self.weightChange = []
        self.weightChange.append(np.zeros([self.worldSize, hiddenLayerSize]))
        self.weightChange.append(np.zeros([hiddenLayerSize, self.worldSize]))
        self.biasesChange = []
        self.biasesChange.append(np.zeros(hiddenLayerSize))
        self.biasesChange.append(np.zeros(self.worldSize))
        self.momentum = 0.9
        self.learningRate = 0.1
        self.error = []
        self.activation = []
        self.layerOutputs = []

    def sigmoid(self, x):
        return 1.0/(1.0 + np.exp(-x)) #np.exp is better than ** cause you can pass it a vector/matrix

    def applyWeights(self, inputGame):
        sideLen = int(np.sqrt(self.worldSize))
        newGame = []
        for i in range(sideLen):
            newGame.append([[] for x in range(sideLen)])

        inputGameArray = []
        for i in range(self.worldSize):
            inputTile = inputGame[i//sideLen][i%sideLen]
            inputTile = 0.9 if inputTile == "O" else 0.1
            inputGameArray.append(inputTile)

        self.layerOutputs = []
        self.layerOutputs.append(self.sigmoid(inputGameArray@self.weights[0] + self.biases[0]))
        self.layerOutputs.append(self.sigmoid(self.layerOutputs[0]@self.weights[1] + self.biases[1]))

        for i in range(self.worldSize):
            newGame[i//sideLen][i%sideLen] = "O" if self.layerOutputs[1][i] >= .5 else "."
        return newGame

    def updateaWeights(self, inputGame, moreStableGame):
        sideLen = int(np.sqrt(self.worldSize))
        inputGameArray = []
        for i in range(self.worldSize):
            inputTile = inputGame[i//sideLen][i%sideLen]
            inputTile = 0.9 if inputTile == "O" else 0.1
            inputGameArray.append(inputTile)

        moreStableGameArray = []
        for i in range(self.worldSize):
            inputTile = moreStableGame[i//sideLen][i%sideLen]
            inputTile = 0.9 if inputTile == "O" else 0.1
            moreStableGameArray.append(inputTile)

        self.error = []
        self.activation = self.layerOutputs[1]
        self.error.append(self.activation * (1.0-self.activation) * (moreStableGameArray-self.activation))
        self.activation = self.layerOutputs[0]
        self.error.insert(0, self.activation * (1-self.activation) * (self.error[0]@np.transpose(self.weights[1])))

        errorVec = np.reshape(self.error[0], (1,-1))
        cur = np.reshape(inputGameArray, (-1,1))
        self.weightChange[0] = (self.learningRate) * (cur@errorVec) + self.momentum * self.weightChange[0]
        self.weights[0] += self.weightChange[0]
        self.biasesChange[0] = (self.learningRate) * (self.error[0]) + self.momentum * self.biasesChange[0]
        self.biases[0] += self.biasesChange[0]

        errorVec = np.reshape(self.error[1], (1,-1))
        cur = np.reshape(self.layerOutputs[0], (-1,1))
        self.weightChange[1] = (self.learningRate) * (cur@errorVec) + self.momentum * self.weightChange[1]
        self.weights[1] += self.weightChange[1]
        self.biasesChange[1] = (self.learningRate) * (self.error[1]) + self.momentum * self.biasesChange[1]
        self.biases[1] += self.biasesChange[1]

    def getOutputAsStr(self):
        sideLen = int(np.sqrt(self.worldSize))
        col = 0
        seedStr = ''
        for entry in self.layerOutputs[1]:
            if entry < 0.5:
                seedStr += 'O'
            else:
                seedStr += '.'
            col += 1
            if col == sideLen:
                seedStr += '\n'
                col = 0
        return seedStr

    def toSeed(self, values):
        seedMx = np.zeros((seedWidth, seedWidth))
        for i in range(len(values)):
            for j in range(len(values[i])):
                if values[i][j] == 'O': seedMx[i, j] = True # PLAINTEXT Live
        return seedMx

    def toString(self, values):
        seedStr = ''
        for i in range(len(values)):
            for j in range(len(values[i])):
                if values[i][j] == 'O': seedStr += 'O' # PLAINTEXT Live
                elif values[i][j] == '.': seedStr += '.' # PLAINTEXT Dead
            seedStr += '\n'
        return seedStr

    def calcFitness(self, values):
        density = values[0][0] / values[0][1]
        duration = len(values[1])
        return ((density / duration), duration)

    def loadPlaintext(self, path):
        print("Loading seed from", path)
        newSeed = []
        newMx = gameUtils.readSeedFile(path)
        newSeed = gameUtils.mxToStringList(newMx)
        return newSeed

    def saveToPlaintext(self, target, width, filename=''):
        # Saves the given seed as a Plaintext file
        # If a filename is not specified, then will be saved with timestamp
        #print("T:", target) # DEBUG
        import hashlib
        seedStr = self.toString(target[0])
        seedhash = hashlib.md5(seedStr.encode('utf-8')).hexdigest()
        import time
        datestamp = time.strftime("%Y%m%d")
        timestamp = time.strftime("%H%M%S")
        if filename == '':
            filename = datestamp + '-' + timestamp + '_' + 'Nseed-' + seedhash[:8] + '.txt'
        #print(filename)
        newFile = open("outputs/" + filename, "w")
        newFile.write("! seed: " + seedhash + '\n')
        newFile.write("! This seed was created with neuralNetwork.py\n")
        newFile.write("! Generated on " + time.strftime("%c") + " at " + time.strftime("%X") + '\n')
        newFile.write("! Runtime: " + str(target[1][1]) + " iterations\n")
        newFile.write("! Stability (density/time): " + str(target[1][0]) + '\n')
        #col = 0
        #for entry in target[0]:
        #    newFile.write(entry)
        #    col += 1
        #    if col == width:
        #        col = 0
        #        newFile.write('\n')
        newFile.write(seedStr)
        newFile.close()

    def generateRandomSeed(self):
        newSeed = []
        for i in range(seedWidth):
            row = []
            for j in range(seedWidth):
                chance = rng.randint(0, 1)
                if chance == True: row.append('O')
                else: row.append('.')
            newSeed.append(row)
        return newSeed

def main():
    cmdArgs = argparse.ArgumentParser(description="Uses a neural network algorithm to generate maximally stable seeds.")
    cmdArgs.add_argument('-f', '--file', type=str, help="Use a Plaintext seed as the starting input.")
    argVals = cmdArgs.parse_args()
    n = neuralNetwork(seedWidth, 20)
    if argVals.file is not None: newGame = n.loadPlaintext(argVals.file)
    else: newGame = n.generateRandomSeed()
    geneStr = ''
    resultList = []
    #print("N:", n.toSeed(newGame)) # DEBUG
    # Perform an initial run to populate the results
    fitnessData = st.runSimulation(n.toSeed(newGame))
    fitStats = n.calcFitness(fitnessData)
    resultList.append((newGame, fitStats)) # add initial state
    #print(resultList[0]) # DEBUG
    #FIXME: change loop condition
    for i in range(5):
        newGame = n.applyWeights(newGame) # run the network forward
        #print(newGame) # DEBUG
        fitnessData = st.runSimulation(n.toSeed(newGame)) # test the new seed
        fitStats = n.calcFitness(fitnessData) # check how it did
        resultList.append((newGame, fitStats)) # add the results to the list
        resultList.sort(reverse = True, key = lambda x: x[1]) #sort the list of results
        #print(resultList[0][0]) # DEBUG
        n.updateaWeights(newGame, resultList[0][0]) #backprop with the most stable seed
    resultList.sort(reverse = True, key = lambda x: x[1]) #sort one last time
    # Display top three most stable results
    print("Neural Network RESULTS:")
    for index in range(3):
        print("Stability:", resultList[index][1][0], ", Sim duration:", resultList[index][1][1])
        print(n.toString(resultList[index][0]))
        if fileFlag == True: n.saveToPlaintext(resultList[index], seedWidth)

# The self-invocation method
if __name__ == "__main__":
    main()
# EOF
