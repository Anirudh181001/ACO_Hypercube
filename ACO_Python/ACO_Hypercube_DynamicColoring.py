# from operator import invert
from networkx.algorithms.centrality.load import newman_betweenness_centrality
from networkx.readwrite.adjlist import generate_adjlist
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
    return num_vertices, num_ants, adj_list # ,adj_list_random_colour, n_matchings_default

def color_three_layers_by_batch(hypercube, start_vertex, edge_colours):
    color_choices = ['red', "blue"]
    print("start vertex is ", start_vertex)
    count = 0
    n = len(start_vertex)
    vertices_to_be_deleted = []
    num_vertices_in_third_layer = n*(n-1)**2
    new_start_vertex_ind = rd.randint(0,num_vertices_in_third_layer-1)
    new_start_vertex = -1
    for choice_vertex_1 in hypercube[start_vertex]:
        #first layer (randomly colouring edge colours) + opposite edges with opposite colours
        if choice_vertex_1 not in hypercube:
            continue
        chosen_color_1 = rd.choice(color_choices)
        edge_colours[chosen_color_1][start_vertex] = [choice_vertex_1]
        edge_colours[chosen_color_1][choice_vertex_1] = [start_vertex]
        edge_colours[get_opp_color(chosen_color_1)][invert_tuple(choice_vertex_1)] = [invert_tuple(start_vertex)]
        edge_colours[get_opp_color(chosen_color_1)][invert_tuple(start_vertex)] = [invert_tuple(choice_vertex_1)]
        print(f"choice vertex 1 is {choice_vertex_1}")
        print("edge_cols is ", edge_colours)
        for choice_vertex_2 in hypercube[choice_vertex_1]:
            if choice_vertex_2 not in hypercube:
                continue
            if hamming_distance(start_vertex, choice_vertex_2) !=2 or (choice_vertex_2 in edge_colours["red"].get(choice_vertex_1,[]) or choice_vertex_2 in edge_colours["blue"].get(choice_vertex_1,[])):
                continue
            chosen_color_2 = get_opp_color(chosen_color_1)
            edge_colours[chosen_color_2][choice_vertex_1] = [choice_vertex_2]
            edge_colours[chosen_color_2][choice_vertex_2] = [choice_vertex_1]
            edge_colours[get_opp_color(chosen_color_2)][invert_tuple(choice_vertex_2)] = [invert_tuple(choice_vertex_1)]
            edge_colours[get_opp_color(chosen_color_2)][invert_tuple(choice_vertex_1)] = [invert_tuple(choice_vertex_2)]
            print(f"choice vertex 2 is {choice_vertex_2}")
            print("edge_cols is ", edge_colours)
            for choice_vertex_3 in hypercube[choice_vertex_2]:
                if choice_vertex_3 not in hypercube:
                    continue
                if hamming_distance(start_vertex, choice_vertex_3) !=3 or (choice_vertex_3 in edge_colours["red"].get(choice_vertex_2,[]) or choice_vertex_3 in edge_colours["blue"].get(choice_vertex_2,[])):
                    continue
                chosen_color_3 = get_opp_color(chosen_color_2)
                edge_colours[chosen_color_3][choice_vertex_2] = [choice_vertex_3]
                edge_colours[chosen_color_3][choice_vertex_3] = [choice_vertex_2]
                edge_colours[get_opp_color(chosen_color_3)][invert_tuple(choice_vertex_3)] = [invert_tuple(choice_vertex_2)]
                edge_colours[get_opp_color(chosen_color_3)][invert_tuple(choice_vertex_2)] = [invert_tuple(choice_vertex_3)]
                print(f"choice vertex 3 is {choice_vertex_3}")
                print("edge_cols is ", edge_colours)
                print("hypercube is ",hypercube)
                if count == new_start_vertex_ind:
                    new_start_vertex = choice_vertex_3
                count+=1
            #remove layer 2 vertices and opp

            vertices_to_be_deleted+=[choice_vertex_2, invert_tuple(choice_vertex_2)]
            print(f"{vertices_to_be_deleted=}")
            

        #remove layer 1 vertices and opp
        vertices_to_be_deleted+=[choice_vertex_1, invert_tuple(choice_vertex_1)]
        print(f"{vertices_to_be_deleted=}")

    #remove start vertex and opp
    vertices_to_be_deleted+=[start_vertex, invert_tuple(start_vertex)]
    print(f"{vertices_to_be_deleted=}")

    for i in set(vertices_to_be_deleted):
        print("deleting ", i)
        del hypercube[i]
        

    return hypercube, new_start_vertex
    

def adversarial_coloring(adj_list):
    edge_colors = {'red':{}, 'blue':{}}
    hypercube = {key:copy.deepcopy(value) for key,value in adj_list.items()}
    start_vertex = rd.choice(list(hypercube.keys()))
    count = 0
    
    while len(hypercube)> 0:
        hypercube, start_vertex = color_three_layers_by_batch(hypercube, start_vertex, edge_colors)
    plot_network_here(edge_colors)
    return edge_colors
        
def plot_network_here(adj_list_random_colour):
    hypercube = nx.Graph()
    edgelist = [("".join(map(str,node1)), "".join(map(str,node2)),  {'color':color}) for color in adj_list_random_colour for node1 in adj_list_random_colour[color] for node2 in adj_list_random_colour[color][node1]]
    hypercube.add_edges_from(edgelist)
    g = Network(height=2000,width=2000,notebook=False)
    g.toggle_hide_edges_on_drag(False)
    g.barnes_hut()
    
    # ant_edges = [("".join(map(str,ant.history_vertices[i-1])), "".join(map(str,ant.history_vertices[i])), {"color": "red"}) if ("".join(map(str,ant.history_vertices[i-1])), "".join(map(str,ant.history_vertices[i])), {'color': '#FFC2CB'}) in edgelist
    #             else  ("".join(map(str,ant.history_vertices[i-1])), "".join(map(str,ant.history_vertices[i])), {'color': 'blue'}) for i in range(1,len(ant.history_vertices))]
    # hypercube.add_edges_from(ant_edges)    
    g.from_nx(hypercube)
    g.show("ex.html")

print(adversarial_coloring(make_hypercube_matrix(3)))
    




        
    
        
        
     
    
    
    
    