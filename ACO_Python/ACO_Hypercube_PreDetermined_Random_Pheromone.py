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

def run_ants_on_hypercube_random_colors_optimized(n, num_ants, plot_network_graph = True, plot_stats = False): #  returns ((ant.number, path_length), iter)
    start = True
    def generate_values_to_plot(new_ant):
        path_length = len(new_ant.history_vertices) - new_ant.num_resets
        return new_ant.number, path_length -1
    n_matchings = {i:[] for i in range(num_ants)}
    alpha = 2
    beta = 1
    
    def select_choice_vertex(ant, adj_list, colored_adj_list, alpha, beta, possible_vertices = None):
        probs = calc_hypercube_prob(ant, adj_list, colored_adj_list, alpha, beta, possible_vertices)
        random_num = rd.random()

        cumsum_probs = dict(zip(np.cumsum(np.multiply(list(probs.keys()), [len(i) for i in probs.values()])), list(probs.values())))
        for prob in cumsum_probs:
            if random_num < prob:
                return rd.choice(cumsum_probs[prob])

        
    #Initialize variables
    def initialize(n, num_ants):
        num_vertices = 2**n
        tic = time.time()
        adj_list = make_hypercube_matrix(n) #Adjacency list of the n-hypercube graph
        toc = time.time()
        if not plot_stats:
            print("Time taken to generate adjacency list is ",toc - tic, " seconds")
        tic = time.time()
        adj_list_random_colour = random_colouring(adj_list) #Randomized colouring of the n-hypercube graph
        toc = time.time()
        n_matchings_default = generate_n_matchings(adj_list)
        if not plot_stats:
            print("Time taken to generate randomized colouring is ",toc - tic, " seconds")
        return num_vertices, num_ants, adj_list, adj_list_random_colour, n_matchings_default
    
    def plot_network(new_ant, adj_list_random_colour):
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

    if start:        
        num_vertices, num_ants, adj_list, adj_list_random_colour, n_matchings_default = initialize(n, num_ants)
        currloc = generate_source(n) # n-tuple of zeros (origin)
        iterations = 500
        breaker = False
                
        #initialize ants 
        ants_list = []
        for i in range(num_ants):
            ants_list.append(Ant(i, None))

        #The fun begins
        for iter in range(iterations):
            if not plot_stats:
                print("iteration: ",iter)
            
            if (breaker == True):
                break
            
            for ant in range(num_ants):
                new_ant = ants_list[ant]
                
                if iter == 0:
                    choice_vertex = rd.choice(adj_list_random_colour['red'][currloc]) if currloc in adj_list_random_colour['red'] else rd.choice(adj_list_random_colour['blue'][currloc])  #Randomly select a vertex from the adjacency list
                    new_ant.add_to_visited(currloc)
                    
                    if ((currloc in adj_list_random_colour['red']) and (choice_vertex in adj_list_random_colour['red'][currloc])):
                        new_ant.set_curr_color('red')
                    else:
                        new_ant.set_curr_color('blue')

                else:
                    #try to continue colour 
                    choice_vertex = select_choice_vertex(new_ant, adj_list, adj_list_random_colour, alpha, beta)
                    
                    if ((new_ant.last_visited not in adj_list_random_colour[new_ant.curr_color]) or ((choice_vertex not in adj_list_random_colour[new_ant.curr_color][new_ant.last_visited]) and not new_ant.has_changed_col)):
                        new_ant.set_has_changed_col()
                        new_ant.set_curr_color(get_opp_color(new_ant.curr_color))
                        if not plot_stats:
                            print(f"{new_ant} is violated: ", new_ant.is_violated)
                        

                # Make sure the choice_edge has not already been visited. If the choice vertex in history, find a new one...
                if((new_ant.last_visited not in adj_list_random_colour[new_ant.curr_color]) or (choice_vertex not in adj_list_random_colour[new_ant.curr_color][new_ant.last_visited] and new_ant.has_changed_col)):
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
                        if not plot_stats:
                            print(f"{new_ant} getting reset")
                        new_ant.reset_to_last_color_change_state()
                        n_matchings[new_ant.number] = n_matchings[new_ant.number][:len(new_ant.history_vertices) - 1]
                        break

                    choice_vertex = select_choice_vertex(new_ant, adj_list, adj_list_random_colour, alpha, beta, list(possible_vertices))
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
                    
                if choice_vertex == invert_tuple(generate_source(n)):#Check if the choice_vertex is the end vertex
                    for ind in n_matchings_default:
                        if n_matchings_default[ind][new_ant.last_visited] == choice_vertex:
                            n_matchings[new_ant.number].append(ind)
                    new_ant.add_to_visited(choice_vertex)
                    # print("n_matchings is ", n_matchings[new_ant.number])
                    if not plot_stats:
                        print(f"{new_ant} reached the end vertex first time")
                        print("n_matchings is ",n_matchings[new_ant.number])
                    
                    if plot_stats:
                        return generate_values_to_plot(new_ant), iter
                    
                    if plot_network_graph:
                       plot_network(new_ant, adj_list_random_colour)

                    breaker = True               
                    break        
                
                for ind in n_matchings_default:
                    if n_matchings_default[ind][new_ant.last_visited] == choice_vertex:
                        n_matchings[new_ant.number].append(ind)
                #Keep track of all the edges visited by the ant, and the corresponding edges that will be visited by the blue ants in dictionary
                new_ant.add_to_visited(choice_vertex)
                if choice_vertex == invert_tuple(generate_source(n)): #Check if the choice_vertex is the end vertex
                    for ind in n_matchings_default:
                        if n_matchings_default[ind][new_ant.last_visited] == choice_vertex:
                            n_matchings[new_ant.number].append(ind)
                    # print("n_matchings is ",n_matchings[new_ant.number])
                    new_ant.add_to_visited(choice_vertex)
                    if not plot_stats:
                        print(f"{new_ant} reached the end vertex")
                        print("n_matchings is ",n_matchings[new_ant.number])
                    
                    if plot_stats: 
                        return generate_values_to_plot(new_ant), iter
                    
                    if plot_network_graph:
                        plot_network(new_ant, adj_list_random_colour)
                    breaker = True
                    break  
    if plot_stats:
        return ((-1, -1),501)

# print(run_ants_on_hypercube_random_colors_optimized(n=5,num_ants=7, plot_network_graph=True, plot_stats=False))