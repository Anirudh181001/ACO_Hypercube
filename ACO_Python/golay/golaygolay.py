# from operator import invert
from networkx.algorithms.centrality.load import newman_betweenness_centrality
from networkx.readwrite.adjlist import generate_adjlist
import numpy as np
import random as rd
import copy
from numpy import inf
import sys
from golay_helper import *
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
import time
import queue


#Initialize variables
def initialize(num_ants, plot_stats):
    num_vertices = 2**24
    tic = time.time()
    adj_list = make_hypercube_matrix(24) #Adjacency list of the n-hypercube graph
    toc = time.time()
    if not plot_stats:
        print("Time taken to generate adjacency list is ",toc - tic, " seconds")
    return num_vertices, num_ants, adj_list # ,adj_list_random_colour, n_matchings_default


def add_to_edge_colors(u,v, curr_col, edge_cols):
    # u_inv = invert_tuple(u)
    # v_inv = invert_tuple(v)
    # curr_col_inv = get_opp_color(curr_col)

    if u in edge_cols[curr_col]:
        edge_cols[curr_col][u].append(v)
    else:
        edge_cols[curr_col][u] = [v]
        
    # if u_inv in edge_cols[curr_col_inv]:
    #     edge_cols[curr_col_inv][u_inv].append(v_inv)
    # else:
    #     edge_cols[curr_col_inv][u_inv] =[v_inv]

    if v in edge_cols[curr_col]:
        edge_cols[curr_col][v].append(u)
    else:
        edge_cols[curr_col][v] = [u]

    # if v_inv in edge_cols[curr_col_inv]:
    #     edge_cols[curr_col_inv][v_inv].append(u_inv)
    # else:
    #     edge_cols[curr_col_inv][v_inv] =[u_inv]

    return edge_cols
    
    
def edge_visited(edge_colours,u,v):
    return v in edge_colours['red'].get(u,[]) or v in edge_colours['blue'].get(u,[])

def color_four_layers_by_batch(hypercube, start_vertex, edge_colours):
    # get the colour based on proj weight
    # do we need to colour opposite edges or will this colouring scheme take care of it for us?
    
    curr_layer_color = None
    # n = 24
    chosen_1_stack = set()
    chosen_2_stack = set()
    chosen_3_stack = set()
    for choice_vertex_1 in hypercube[start_vertex]:
        if edge_visited(edge_colours,start_vertex,choice_vertex_1):
            print("collision 1")
            continue
        # chosen_col1 = rd.choice(color_choices)
        chosen_1_stack.add(choice_vertex_1)
        add_to_edge_colors(start_vertex,choice_vertex_1,curr_layer_color,edge_colours)
    
    for choice_vertex_1 in chosen_1_stack:
        for choice_vertex_2 in hypercube[choice_vertex_1]:
            if edge_visited(edge_colours,choice_vertex_1,choice_vertex_2):
                print("collision 2")
                continue
            curr_layer_color = get_opp_color(curr_layer_color)
            add_to_edge_colors(choice_vertex_1,choice_vertex_2,curr_layer_color,edge_colours)
            chosen_2_stack.add(choice_vertex_2)
            
    for choice_vertex_2 in chosen_2_stack:
        for choice_vertex_3 in hypercube[choice_vertex_2]:
            if edge_visited(edge_colours,choice_vertex_2,choice_vertex_3):
                print("collision 3")
                continue
            curr_layer_color = get_opp_color(curr_layer_color)
            add_to_edge_colors(choice_vertex_2,choice_vertex_3,curr_layer_color,edge_colours)
            chosen_3_stack.add(choice_vertex_3)
            
    for choice_vertex_3 in chosen_3_stack:
        for choice_vertex_4 in hypercube[choice_vertex_3]:
            if edge_visited(edge_colours,choice_vertex_3,choice_vertex_4):
                print("collision 4")
                continue
            curr_layer_color = get_opp_color(curr_layer_color)
            add_to_edge_colors(choice_vertex_3,choice_vertex_4,curr_layer_color,edge_colours)
            
    return f"Hamming ball at {start_vertex} is done"
    
        

def is_complete(edge_cols,n):
    count = 0
    num_edges = n*(2**(n-2)) #half of the total number of edges
    for col,u_vertices in edge_cols.items():
        for u,v_vertices in u_vertices.items():
            count+=len(v_vertices)
        break
    
    if count == num_edges:
        return True
    return False
        

def color_hamming_balls(adj_list,golay_codewords): # change to colour from list of codewords
    edge_colors = {'red':{}, 'blue':{}}
    # hypercube = {key:copy.deepcopy(value) for key,value in adj_list.items()}
    for codeword in golay_codewords:
        color_four_layers_by_batch(adj_list, codeword, edge_colors)

    assert is_complete(edge_colors, 24)

    return edge_colors
