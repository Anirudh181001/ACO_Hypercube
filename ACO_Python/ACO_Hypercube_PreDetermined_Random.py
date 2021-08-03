# from operator import invert
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
from pyvis.network import Network

def run_ants_on_hypercube_random_colors(n, num_ants, plot_network_graph):
    start = True
    #Initialize variables
    def initialize(n, num_ants):
        num_vertices = 2**n
        tic = time.time()
        adj_list = make_hypercube_matrix(n) #Adjacency list of the n-hypercube graph
        toc = time.time()
        print("Time taken to generate adjacency list is ",toc - tic, " seconds")
        tic = time.time()
        adj_list_random_colour = random_colouring(adj_list) #Randomized colouring of the n-hypercube graph
        toc = time.time()
        print("Time taken to generate randomized colouring is ",toc - tic, " seconds")
        return num_vertices, num_ants, adj_list, adj_list_random_colour


    if start:
        
        num_vertices, num_ants, adj_list, adj_list_random_colour = initialize(n, num_ants)
        
        currloc = generate_source(n) # n-tuple of zeros (origin)
        iterations = 500
        breaker = False
        
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
                new_ant = ants_list[ant]
                color_changer_correct = False
                if iter == 0:
                    choice_vertex = rd.choice(adj_list_random_colour['red'][currloc]) if currloc in adj_list_random_colour['red'] else rd.choice(adj_list_random_colour['blue'][currloc])  #Randomly select a vertex from the adjacency list
                    new_ant.add_to_visited(currloc)
                    
                    if ((currloc in adj_list_random_colour['red']) and (choice_vertex in adj_list_random_colour['red'][currloc])):
                        new_ant.set_curr_color('red')
                    else:
                        new_ant.set_curr_color('blue')

                else:
                    #try to continue colour 
                    choice_vertex = rd.choice(adj_list[new_ant.last_visited])

                    
                    if ((new_ant.last_visited not in adj_list_random_colour[new_ant.curr_color]) or ((choice_vertex not in adj_list_random_colour[new_ant.curr_color][new_ant.last_visited]) and not new_ant.has_changed_col)):
                        new_ant.set_has_changed_col()
                        new_ant.set_curr_color(get_opp_color(new_ant.curr_color))
                        print(f"{new_ant} is violated: ", new_ant.is_violated)
                        

                # Make sure the choice_edge has not already been visited. If the choice vertex in history, find a new one...
                if((new_ant.last_visited not in adj_list_random_colour[new_ant.curr_color]) or (choice_vertex not in adj_list_random_colour[new_ant.curr_color][new_ant.last_visited] and new_ant.has_changed_col)):
                    if iter ==0:
                        print("Nothing happens here")
                    else:

                        #possible vertices are the vertices that the ant can go to (not visited before)
                        # and vertices that would not violate the colour change rule
                        possible_vertices = set(adj_list[new_ant.last_visited]) - set(new_ant.history_vertices)
                        if new_ant.has_changed_col:
                            temp_var = set()
                            for i in possible_vertices:
                                if(i not in adj_list_random_colour[new_ant.curr_color][new_ant.last_visited]):
                                    temp_var.add(i)
                            possible_vertices -= temp_var
                        if len(possible_vertices) == 0:
                            print(f"{new_ant} getting reset")
                            new_ant.reset_to_last_color_change_state()
                            
                            break

                        choice_vertex = rd.choice(list(possible_vertices))
                        if ((new_ant.last_visited not in adj_list_random_colour[new_ant.curr_color]) or (choice_vertex not in adj_list_random_colour[new_ant.curr_color][new_ant.last_visited])):
                            new_ant.set_has_changed_col()
                            new_ant.set_curr_color(get_opp_color(new_ant.curr_color))

                        #if the end vertex (1-tuple) is in the possible vertices, then that is the choice
                        if invert_tuple(generate_source(n)) in possible_vertices:
                            choice_vertex = invert_tuple(generate_source(n))
                            break
                        
                        
                        '''
                        if the edge to the chosen vertex is the not of the same colour as the prev travelled edge, 
                        accept the colour change and keep track of it.
                        '''
                    
                if choice_vertex == invert_tuple(generate_source(n)): #Check if the choice_vertex is the end vertex
                    new_ant.add_to_visited(choice_vertex)
                    print(f"{new_ant} reached the end vertex first time")
                    
                    if plot_network_graph:
                        hypercube = nx.Graph()
                        edgelist = [("".join(map(str,node1)), "".join(map(str,node2)),  {'color':change_to_gray(color)}) for color in adj_list_random_colour for node1 in adj_list_random_colour[color] for node2 in adj_list_random_colour[color][node1]]
                        hypercube.add_edges_from(edgelist)
                        g = Network(height=2000,width=2000,notebook=False)
                        g.toggle_hide_edges_on_drag(False)
                        g.barnes_hut()

                        ant_edges = [("".join(map(str,new_ant.history_vertices[i-1])), "".join(map(str,new_ant.history_vertices[i])), {"color": "red"}) if ("".join(map(str,new_ant.history_vertices[i-1])), "".join(map(str,new_ant.history_vertices[i])), {'color': '#FFC2CB'}) in edgelist
                                    else  ("".join(map(str,new_ant.history_vertices[i-1])), "".join(map(str,new_ant.history_vertices[i])), {'color': 'blue'}) for i in range(1,len(new_ant.history_vertices))]
                        hypercube.add_edges_from(ant_edges)    
                        g.from_nx(hypercube)
                        g.show("ex.html")

                    breaker = True               
                    break        

                #Keep track of all the edges visited by the ant, and the corresponding edges that will be visited by the blue ants in dictionary
                new_ant.add_to_visited(choice_vertex)

                if choice_vertex == invert_tuple(generate_source(n)): #Check if the choice_vertex is the end vertex
                    new_ant.add_to_visited(choice_vertex)
                    print(f"{new_ant} reached the end vertex")
                    
                    if plot_network_graph:
                        hypercube = nx.Graph()
                        g = Network(height=2000,width=2000,notebook=False)
                        g.toggle_hide_edges_on_drag(False)
                        g.barnes_hut()
                        edgelist = [("".join(map(str,node1)), "".join(map(str,node2)),  {'color':change_to_gray(color)}) for color in adj_list_random_colour for node1 in adj_list_random_colour[color] for node2 in adj_list_random_colour[color][node1]]
                        hypercube.add_edges_from(edgelist)
                        

                        ant_edges = [("".join(map(str,new_ant.history_vertices[i-1])), "".join(map(str,new_ant.history_vertices[i])), {"color": "red"}) if ("".join(map(str,new_ant.history_vertices[i-1])), "".join(map(str,new_ant.history_vertices[i])), {'color': '#FFC2CB'}) in edgelist
                                    else  ("".join(map(str,new_ant.history_vertices[i-1])), "".join(map(str,new_ant.history_vertices[i])), {'color': 'blue'}) for i in range(1,len(new_ant.history_vertices))]

                        hypercube.add_edges_from(ant_edges)
                        g.from_nx(hypercube)
                        g.show("ex.html")   
                    breaker = True
                    break  

run_ants_on_hypercube_random_colors(7,10, True)