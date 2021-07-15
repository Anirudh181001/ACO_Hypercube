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
n = 11
num_vertices = 2**n
num_ants = 25
tic = time.time()
adj_list = make_hypercube_matrix(n) #Adjacency list of the n-hypercube graph
toc = time.time()
print("Time taken to generate adjacency list is ",toc - tic, " seconds")
tic = time.time()
adj_list_random_colour = random_colouring(make_hypercube_matrix(n)) #Randomized colouring of the n-hypercube graph
toc = time.time()
print("Time taken to generate randomized colouring is ",toc - tic, " seconds")
currloc = generate_source(n) # n-tuple of zeros (origin)
iterations = 500
breaker = False
visited_red = {}
visited_blue = {}

#initialize ants 
ants_list = []
for i in range(num_ants):
    ants_list.append(Ant(i, None))


#The fun begins
for iter in range(iterations):
    print("iteration: ",iter)
    
    if (breaker == True):
        break
    
    for ant in range(num_ants):
        
        if iter == 0:
            choice_vertex = rd.choice(adj_list_random_colour['red'][currloc]) if currloc in adj_list_random_colour['red'] else rd.choice(adj_list_random_colour['blue'][currloc])  #Randomly select a vertex from the adjacency list
            new_ant = ants_list[ant]
            new_ant.add_to_visited(currloc)
            if(currloc in adj_list_random_colour['red'] and choice_vertex in adj_list_random_colour['red'][currloc]):
                new_ant.set_curr_color('red')
            else:
                new_ant.set_curr_color('blue')
            new_ant.add_to_visited(choice_vertex)

        else:
            #try to continue colour 
            choice_vertex = rd.choice(adj_list[new_ant.last_visited])
            
        if choice_vertex == invert_tuple(generate_source(n)): #Check if the choice_vertex is the end vertex
            
            print(f"{new_ant} reached the end vertex first time")
            breaker = True
            break        
        
        # check_can_continue_same_col = (currloc in adj_list_random_colour[new_ant.curr_color] and choice_vertex in adj_list_random_colour[new_ant.curr_color][currloc])
        counter = 0 
        while choice_vertex in new_ant.history_vertices: # Make sure the choice_edge has not already been visited
            counter += 1
            if counter == 20:
                new_ant.reset_to_last_color_change_state()
                break
            possible_vertices = set(adj_list_random_colour[new_ant.curr_color][new_ant.last_visited]) - set(new_ant.history_vertices)
            if invert_tuple(generate_source(n)) in possible_vertices:
                choice_vertex = invert_tuple(generate_source(n))
                break
            if len(possible_vertices.intersection(adj_list_random_colour[new_ant.curr_color])) == 0 or set(adj_list_random_colour[new_ant.curr_color][new_ant.last_visited]).issubset(set(new_ant.history_vertices)): #need to change colour
                if len(possible_vertices) == 0:
                    choice_vertex = rd.choice(adj_list_random_colour[get_opp_color(new_ant.curr_color)][new_ant.last_visited])
                else:
                    choice_vertex = rd.choice(list(possible_vertices))
                    
                new_ant.set_curr_color(get_opp_color(new_ant.curr_color))
                new_ant.set_has_changed_col()
                new_ant.add_to_history_colours(new_ant.curr_color)
                if new_ant.is_violated:
                    new_ant.reset_to_last_color_change_state()
            
            else:
                choice_vertex = rd.choice(list(possible_vertices))

        #Keep track of all the edges visited by the ant, and the corresponding edges that will be visited by the blue ants in dictionary
        new_ant.add_to_visited(choice_vertex)
        if choice_vertex == invert_tuple(generate_source(n)): #Check if the choice_vertex is the end vertex
                print(f"{new_ant} reached the end vertex")
                breaker = True
                break  