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
import queue
#Initialize variables
def initialize(n, num_ants, plot_stats):
    num_vertices = 2**n
    tic = time.time()
    adj_list = make_hypercube_matrix(n) #Adjacency list of the n-hypercube graph
    toc = time.time()
    if not plot_stats:
        print("Time taken to generate adjacency list is ",toc - tic, " seconds")
    return num_vertices, num_ants, adj_list # ,adj_list_random_colour, n_matchings_default


def add_to_edge_colors(u,v, curr_col, edge_cols):
    u_inv = invert_tuple(u)
    v_inv = invert_tuple(v)
    curr_col_inv = get_opp_color(curr_col)
    count = 0
    if u in edge_cols[curr_col]:
        edge_cols[curr_col][u].append(v)
    else:
        edge_cols[curr_col][u] = [v]
        
    if u_inv in edge_cols[curr_col_inv]:
        edge_cols[curr_col_inv][u_inv].append(v_inv)
    else:
        edge_cols[curr_col_inv][u_inv] =[v_inv]

    if v in edge_cols[curr_col]:
        edge_cols[curr_col][v].append(u)
    else:
        edge_cols[curr_col][v] = [u]

    if v_inv in edge_cols[curr_col_inv]:
        edge_cols[curr_col_inv][v_inv].append(u_inv)
    else:
        edge_cols[curr_col_inv][v_inv] =[u_inv]

    return edge_cols
    
    
def edge_visited(edge_colours,u,v):
    return v in edge_colours['red'].get(u,[]) or v in edge_colours['blue'].get(u,[])

def color_three_layers_by_batch(hypercube, start_vertex, edge_colours, new_start_vertices):
    color_choices = ['red', "blue"]
    count = 0
    n = len(start_vertex)
    chosen_1_stack = {}
    chosen_2_stack = {}
    for choice_vertex_1 in hypercube[start_vertex]:
        if edge_visited(edge_colours,start_vertex,choice_vertex_1):
            continue
        chosen_col1 = rd.choice(color_choices)
        chosen_1_stack[choice_vertex_1] = chosen_col1
        add_to_edge_colors(start_vertex,choice_vertex_1,chosen_col1,edge_colours)
    
    for choice_vertex_1 in chosen_1_stack:
        for choice_vertex_2 in hypercube[choice_vertex_1]:
            if edge_visited(edge_colours,choice_vertex_1,choice_vertex_2):
                continue
            chosen_col2 = get_opp_color(chosen_1_stack[choice_vertex_1])
            add_to_edge_colors(choice_vertex_1,choice_vertex_2,chosen_col2,edge_colours)
            chosen_2_stack[choice_vertex_2] = chosen_col2
            
    for choice_vertex_2 in chosen_2_stack:
        for choice_vertex_3 in hypercube[choice_vertex_2]:
            if edge_visited(edge_colours,choice_vertex_2,choice_vertex_3):
                continue
            new_start_vertices[choice_vertex_3]=True
            chosen_col3 = get_opp_color(chosen_2_stack[choice_vertex_2])
            add_to_edge_colors(choice_vertex_2,choice_vertex_3,chosen_col3,edge_colours)
            
    return new_start_vertices
    
        

def is_complete(edge_cols,n):
    count = 0
    num_edges = n*(2**(n-1))
    for col,u_vertices in edge_cols.items():
        for u,v_vertices in u_vertices.items():
            count+=len(v_vertices)
        break
    
    if count == num_edges:
        return True
    return False
        

def adversarial_coloring(adj_list, plot=False):
    edge_colors = {'red':{}, 'blue':{}}
    hypercube = {key:copy.deepcopy(value) for key,value in adj_list.items()}
    start_vertex = rd.choice(list(hypercube.keys()))
    n=len(start_vertex)
    new_start_vertices = {start_vertex:True}
    while len(new_start_vertices)>0:
        for key in new_start_vertices:
            start_vertex = key
            del new_start_vertices[key]
            break
        new_start_vertices = color_three_layers_by_batch(hypercube, start_vertex, edge_colors,new_start_vertices)
    if plot:
        plot_network_here(edge_colors)
    return edge_colors

        
def plot_network_here(adj_list_random_colour):
    hypercube = nx.Graph()
    edgelist = [("".join(map(str,node1)), "".join(map(str,node2)),  {'color':color}) for color in adj_list_random_colour for node1 in adj_list_random_colour[color] for node2 in adj_list_random_colour[color][node1]]
    hypercube.add_edges_from(edgelist)
    g = Network(height=2000,width=2000,notebook=False)
    g.toggle_hide_edges_on_drag(False)
    g.barnes_hut()
    g.from_nx(hypercube)
    g.show("ex.html")


adversarial_coloring(make_hypercube_matrix(7))
    




        
    
        
        
     
    
    
    
    