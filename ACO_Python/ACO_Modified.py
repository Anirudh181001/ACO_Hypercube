import numpy as np
import random as rd
from python_tsp.exact import solve_tsp_dynamic_programming
import copy
from numpy import inf
import sys
from aco_helper import *
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm

#init
m_ants = 10
n_cities = 7
pheremone = (0.01)*np.ones((n_cities, n_cities)) #initially pheremone trail along the edges should be equal
city = make_sym_matrix(n_cities, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]) #OD distance matrix
alpha = 2
beta= 2
source_vertex = 0 #where the ants start from
pathlen = np.zeros((1,m_ants)) # list of the distances travelled by each ant
ants_pheremone = np.zeros((m_ants,n_cities,2)) # an m x n matrix of "tuples" -> (city, pheremone) to keep track of the path taken by each ant
iterations = 500 
temp_AP = copy.deepcopy(ants_pheremone)
probs = np.zeros((1,n_cities))
curlocarr = np.zeros((iterations,m_ants,n_cities))

for i in range(n_cities): # a large number to prevent ants from going back to where they came from and avoid division by zero
    city[i][i] = 0.1

#initial probabilities of taking a particular path
probs = calc_prob(n_cities, pheremone, city, source_vertex, probs, alpha, beta)
#need to check if probs are correct***

#Begin the loops

for iter in tqdm(range(iterations)):
    # Reset in every iteration
    pathlen = np.zeros((1,m_ants))
    ants_pheremone = copy.deepcopy(temp_AP)
    temp_AP=np.zeros((m_ants,n_cities,2))
    visited = {}
    
    for ant in range(m_ants):
        fakecity = copy.deepcopy(city)
        
        for node in range(n_cities):
            
            currloc = int(temp_AP[ant][node][0])
            if ant not in visited: 
                visited[ant] = [currloc]

            curlocarr[iter][ant][node] = currloc #keeping track of the cities visited by each ant sequentially
            fakeprobs= np.cumsum(probs[0]) 
            
            random_float = rd.random() #random num generator to see which path ant will take 
            choice_city = calc_choice_city(probs,n_cities,temp_AP,ant,node)
            # print("choice city for ant ",ant," is ", choice_city) 
            while (choice_city in visited[ant]):
                # print("choice city is ", choice_city," for ant ", ant)
                # print("visited is ",visited)
                choice_city = calc_choice_city(probs,n_cities,temp_AP,ant,node)
                if len(visited[ant]) == n_cities:
                    choice_city = 0
                    break        
            
            visited[ant].append(choice_city)
                        
            pathlen[0][ant]+= fakecity[currloc][choice_city]
            #new probs
            probs = calc_prob(n_cities, pheremone, fakecity, currloc, probs, alpha, beta)
    
    for i in range(m_ants):
        for j in range(n_cities):
            
            temp_AP[i][j][1] = 1/pathlen[0][i] # 1/distance
            city1 = int(temp_AP[i][int(j%n_cities)][0])
            city2 = int(temp_AP[i][int((j+1)%n_cities)][0])
            
            pheremone[city1][city2]+=temp_AP[i][int(j%n_cities)][1] #update pheremones based on distance, shorter distance = higher pheremone

ants_pheremone = temp_AP        
#print(ants_pheremone)
# print(probs)
#print(curlocarr)
# print("currloc length is ", len(curlocarr))
print("pathlen ",pathlen)
optimal_ant = np.argmin(pathlen[0])
print(visited)
print("optimal path length via ACO is ",visited[optimal_ant]," length is ",pathlen[0][optimal_ant])

permutation, distance = solve_tsp_dynamic_programming(city)
print(city)
print("Optimal path is ",permutation, "of length ", distance)
