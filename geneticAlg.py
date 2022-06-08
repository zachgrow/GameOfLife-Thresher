# Genetic Alorithm Implementation
# Author: Chris Deacon
# CS445, Spring 2022

import numpy as np
import scipy.signal as scp
import random as rand

ITERATIONS = 1000
MUTATION_CHANCE = 5

def fitness(c):
    return sum(c*c, axis = 1) 

def selection(population, scores):
    # selecting best 3 winners
    k = 3
    select = rand(len(population))
    # tournament arc
    for i in rand(0, len(population), k-1):
        if scores[i] < scores[select]:
            select = i
    return population[select]

def crossover(parent_1, parent_2):
    point = rand(1, len(parent_1) - 3)
    child = parent_1[:point] + parent_2[point:]
    return child

def mutation(c):
    for i in range(len(c)):
        if(rand() < MUTATION_CHANCE):
            c[i] = 1 - c[i]


def genetic_alorithm(currentWorld):
    current = currentWorld.flatten()
    # best solutions
    winner = 0    
    winner_all = fitness(current[0])
    # Selection
    for generation in range(ITERATIONS):
        scores = [fitness(c) for c in current]
        for i in range(current[-1]):
            if scores[i] < winner_all:
                winner = current[i]
                winner_all = scores[i]
        select = [selection(current, scores)]
        # Mutation and Crossover
        children = list()
        # range stepping every 2 children
        for i in range(0, current[-1], 2):
            parent_1 = select[i]
            parent_2 = select[i+1]
            for c in crossover(parent_1, parent_2):
                mutation(c)
                children.append(c)
                current = children
    return [winner, winner_all]