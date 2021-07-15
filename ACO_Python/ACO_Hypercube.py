from operator import invert
import numpy as np
import random as rd
from numpy.lib.utils import source
import copy
from numpy import inf
import sys
from aco_helper import *
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
import time

#Initialize variables
n = 12
num_vertices = 2**n
num_ants = n
tic = time.time()
adj_list = make_hypercube_matrix(n) #Adjacency list of the n-hypercube graph
toc = time.time()
print("Time taken to generate adjacency list is ",toc - tic, " seconds")
currloc = generate_source(n) # n-tuple of zeros (origin)
iterations = 500
currloc_dict = {}
breaker = False
#print(adj_list)
visited_red = {}
visited_blue = {}

# Set the start position for all ants to source
for ant in range(num_ants):
    currloc_dict[ant] = currloc

#The fun begins
for iter in range(iterations):
    print("iteration: ",iter)
    
    if (breaker == True):
        break
    
    for ant in range(num_ants):
        choice_vertex = rd.choice(adj_list[currloc_dict[ant]]) #Randomly select a vertex from the adjacency list
        if choice_vertex == invert_tuple(generate_source(n)): #Check if the choice_vertex is the end vertex
            print("Red ant reached the end vertex")
            breaker = True
            break        
        
        while (currloc, choice_vertex) in visited_red: # Make sure the choice_edge has not already been visited

            choice_vertex = rd.choice(adj_list[currloc_dict[ant]])
            if choice_vertex == invert_tuple(generate_source(n)): #Check if the choice_vertex is the end vertex
                print("Red ant reached the end vertex")
                breaker = True
                break  
        #Keep track of all the edges visited by the ant, and the corresponding edges that will be visited by the blue ants in dictionary
        visited_red[(currloc, choice_vertex)] = True #red edge
        visited_red[(choice_vertex, currloc)] = True #red edge (opp direction)
        visited_blue[(invert_tuple(currloc), invert_tuple(choice_vertex))] = True #blue edge
        visited_blue[(invert_tuple(choice_vertex), invert_tuple(currloc))] = True #blue edge (opp direction)
        
        intersection = set(visited_blue.keys()) & set(visited_red.keys()) #if red meets blue
        
        #Check if there is any intersection between the edges visited by red and blue ant
        if len(intersection) > 0:
            print("Intersection Found!")
            print("intersection: ", intersection)
            # print("blue ant path: ",visited_blue)
            # print("red ant path: ",visited_red)
            breaker = True
            break
        
        #Update current position of ant
        currloc = choice_vertex
        currloc_dict[ant] = currloc