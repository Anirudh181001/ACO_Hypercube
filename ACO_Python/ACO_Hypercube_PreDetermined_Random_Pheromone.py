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


#Initialize variables
def initialize(n, num_ants, plot_stats):
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


def select_choice_vertex(ant, adj_list, colored_adj_list, alpha, beta, possible_vertices = None):
    probs = calc_hypercube_prob(ant, adj_list, colored_adj_list, alpha, beta, possible_vertices)
    random_num = rd.random()
    cumsum_probs = dict(zip(np.cumsum(np.multiply(list(probs.keys()), [len(i) for i in probs.values()])), list(probs.values())))
    for prob in cumsum_probs:
        if random_num < prob:
            return rd.choice(cumsum_probs[prob])


def plot_network(ant, adj_list_random_colour):
    hypercube = nx.Graph()
    edgelist = [("".join(map(str,node1)), "".join(map(str,node2)),  {'color':change_to_gray(color)}) for color in adj_list_random_colour for node1 in adj_list_random_colour[color] for node2 in adj_list_random_colour[color][node1]]
    hypercube.add_edges_from(edgelist)
    g = Network(height=2000,width=2000,notebook=False)
    g.toggle_hide_edges_on_drag(False)
    g.barnes_hut()
    
    ant_edges = [("".join(map(str,ant.history_vertices[i-1])), "".join(map(str,ant.history_vertices[i])), {"color": "red"}) if ("".join(map(str,ant.history_vertices[i-1])), "".join(map(str,ant.history_vertices[i])), {'color': '#FFC2CB'}) in edgelist
                else  ("".join(map(str,ant.history_vertices[i-1])), "".join(map(str,ant.history_vertices[i])), {'color': 'blue'}) for i in range(1,len(ant.history_vertices))]
    hypercube.add_edges_from(ant_edges)    
    g.from_nx(hypercube)
    g.show("ex.html")


def ant_first_step(ant, start_vertex, adj_list, adj_list_random_colour):
    choice_vertex = rd.choice(adj_list[start_vertex])
    ant.add_to_visited(start_vertex)
    if choice_vertex in adj_list_random_colour['red'].get(start_vertex):
        ant.set_curr_color('red')
    else:
        ant.set_curr_color('blue')


def find_possible_vertices(ant, adj_list, adj_list_random_colour):
    possibe_vertices = set(adj_list[ant.last_visited]) - set(ant.history_vertices)
    if ant.has_changed_col:
        temp_var = set()
        for i in possibe_vertices:
            if i not in adj_list_random_colour[ant.curr_color][ant.last_visited]:
                temp_var.add(i)
        possibe_vertices -= temp_var
    return possibe_vertices


def run_ants_on_hypercube_random_colors_optimized(n, num_ants, plot_network_graph = True, plot_stats = False): #  returns ((ant.number, path_length), iter)
    n_matchings = {i:[] for i in range(num_ants)}
    alpha = 2
    beta = 1
    num_vertices, num_ants, adj_list, adj_list_random_colour, n_matchings_default = initialize(n, num_ants, plot_stats)
    start_vertex = generate_source(n) # n-tuple of zeros (origin)
    iterations = 500
    breaker = False
            
    #initialize ants 
    ants_list = [Ant(i, None) for i in range(num_ants)]

    #The fun begins
    for iter in range(iterations):
        if not plot_stats:
            print("iteration: ", iter)
        
        if breaker:
            break
        
        for ant_number in range(num_ants):
            curr_ant = ants_list[ant_number]
            
            if iter == 0:
                ant_first_step(curr_ant, start_vertex, adj_list, adj_list_random_colour)
                continue
            else:
                choice_vertex = select_choice_vertex(curr_ant, adj_list, adj_list_random_colour, alpha, beta)
                test_condition_1 = curr_ant.last_visited not in adj_list_random_colour[curr_ant.curr_color]
                print(f"{test_condition_1 = }")
                test_condition_2 = choice_vertex not in adj_list_random_colour[curr_ant.curr_color][curr_ant.last_visited]
                print(f"{test_condition_2 = }")
                if test_condition_1 or test_condition_2 and not curr_ant.has_changed_col:
                    # check this condition again...
                    curr_ant.set_has_changed_col()
                    curr_ant.set_curr_color(get_opp_color(curr_ant.curr_color))
                    if not plot_stats:
                        print(f"{curr_ant} is violated: ", curr_ant.is_violated)
                    

            # Make sure the choice_edge has not already been visited. If the choice vertex in history, find a new one...
            if ((curr_ant.last_visited not in adj_list_random_colour[curr_ant.curr_color]) or (choice_vertex not in adj_list_random_colour[curr_ant.curr_color][curr_ant.last_visited] and curr_ant.has_changed_col)):
                # possible vertices are the vertices that the ant has not visited before
                # and vertices that would not violate the colour change rule
                possible_vertices = find_possible_vertices(curr_ant, adj_list, adj_list_random_colour)
  
                if len(possible_vertices) == 0: 
                    #need to reset to last colour change
                    if not plot_stats:
                        print(f"{curr_ant} getting reset")
                    curr_ant.reset_to_last_color_change_state()
                    n_matchings[curr_ant.number] = n_matchings[curr_ant.number][:len(curr_ant.history_vertices) - 1]
                    break
               
                elif invert_tuple(generate_source(n)) in possible_vertices:
                    #if the end vertex (1-tuple) is in the possible vertices, then that is the choice
                    choice_vertex = invert_tuple(generate_source(n))

                else:
                    choice_vertex = select_choice_vertex(curr_ant, adj_list, adj_list_random_colour, alpha, beta, list(possible_vertices))
                    if ((curr_ant.last_visited not in adj_list_random_colour[curr_ant.curr_color]) or (choice_vertex not in adj_list_random_colour[curr_ant.curr_color][curr_ant.last_visited])):
                        curr_ant.set_has_changed_col()
                        curr_ant.set_curr_color(get_opp_color(curr_ant.curr_color))
                               

            for ind in n_matchings_default:
                if n_matchings_default[ind][curr_ant.last_visited] == choice_vertex:
                    n_matchings[curr_ant.number].append(ind)
            curr_ant.add_to_visited(choice_vertex)

            if choice_vertex == invert_tuple(generate_source(n)): 
                #Check if the choice_vertex is the end vertex
                if plot_network_graph:
                    plot_network(curr_ant, adj_list_random_colour)
                if plot_stats: 
                    return curr_ant.get_path_len(), iter
                else:
                    print(f"{curr_ant} reached the end vertex")
                    print("n_matchings is ", n_matchings[curr_ant.number])
                breaker = True
                break  
    
    if plot_stats:
        return ((-1, -1),501)


if __name__ == '__main__':
    print(run_ants_on_hypercube_random_colors_optimized(n=5, num_ants=10, plot_network_graph=True, plot_stats=False))
