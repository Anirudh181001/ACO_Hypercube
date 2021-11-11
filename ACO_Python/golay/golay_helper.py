#Helper functions
import networkx
from networkx.generators.random_graphs import fast_gnp_random_graph
import numpy as np
import random as rd
import copy
import math
from numpy import inf
import sys
from scipy.spatial import distance

def hamming_distance(arr_1,arr_2):
    norm_dist = distance.hamming(arr_1, arr_2)
    return len(arr_1) * norm_dist

def get_opp_color(color):
    if color == "blue":
        return "red"
    else:
        return "blue"
    
def make_hypercube_matrix(n):
    matrix = networkx.to_dict_of_lists(networkx.generators.lattice.hypercube_graph(n))
    return matrix

def invert_tuple(vertex):
    ans = []
    for i in vertex:
        if i== 0:
            ans.append(1)
        else:
            ans.append(0)
    return tuple(ans)


def generate_source(n):
    ans = []
    choices = [0,1]
    for i in range(n):
        ans.append(rd.choice(choices))
    return tuple(ans)


def get_col(adj_list_random_colour, start_vertex, end_vertex):
    if end_vertex in adj_list_random_colour['red'].get(start_vertex, []):
        return 'red'
    else:
        return 'blue'

def get_proj_weight(binary_code):
    return sum(binary_code[:-1])

def get_hamming_ball_col(proj_weight):
    return 'blue' if proj_weight % 2 == 1 else 'red'

def is_point_in_ham_ball(point,hamming_center):
    return hamming_distance(point,hamming_center) <= 4


def getbin(n, s=['']):
    if n > 0:
        return [
            *getbin(n - 1, [i + '0' for i in s]),
            *getbin(n - 1, [j + '1' for j in s])
        ]
    return s


def get_golay_codewords():
    all_bin = getbin(12)
    A = [
        [0,1,1,1,1,1,1,1,1,1,1,1],
        [1,1,1,0,1,1,1,0,0,0,1,0],
        [1,1,0,1,1,1,0,0,0,1,0,1],
        [1,0,1,1,1,0,0,0,1,0,1,1],
        [1,1,1,1,0,0,0,1,0,1,1,0],
        [1,1,1,0,0,0,1,0,1,1,0,1],
        [1,1,0,0,0,1,0,1,1,0,1,1],
        [1,0,0,0,1,0,1,1,0,1,1,1],
        [1,0,0,1,0,1,1,0,1,1,1,0],
        [1,0,1,0,1,1,0,1,1,1,0,0],
        [1,1,0,1,1,0,1,1,1,0,0,0],
        [1,0,1,1,0,1,1,1,0,0,0,1]
    ]

    I = np.identity(12)

    C = np.concatenate((I, A),axis =1 )

    codewords = []
    for i in all_bin:
        bin_code = np.array(list(map(int, list(i))))
        res = bin_code@C
        res = list(map(lambda x: x%2, res))
        codewords.append(res)

    return codewords