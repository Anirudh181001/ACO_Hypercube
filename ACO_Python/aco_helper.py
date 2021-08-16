#Helper functions
import networkx
from networkx.generators.random_graphs import fast_gnp_random_graph
import numpy as np
import random as rd
import copy
import math
from numpy import inf
import sys
import dataclasses

def make_sym_matrix(n,vals):
    m = np.zeros([n,n])
    xs,ys = np.triu_indices(n,k=1)
    m[xs,ys] = vals
    m[ys,xs] = vals
    return m


distance_matrix1 = np.array([
    [0,  5, 4, 10],
    [5,  0, 8,  5],
    [4,  8, 0,  3],
    [10, 5, 3,  0]
])

def calc_prob(n_cities, pheremone, city, current_position, probs, alpha, beta):
    sumprob=0
    
    for j in range(n_cities): #sum of all the paths the ant can take ( denominator )
        sumprob += ((pheremone[current_position][j])**alpha)*(1/(city[current_position][j]**beta)) 
        
    for i in range(n_cities): #probability for each path
        probs[0][i] = ((pheremone[current_position][i]**alpha)*(1/(city[current_position][i]**beta)))/sumprob     
    return probs

def calc_choice_city(probs,n_cities,temp_AP,ant,node):

    fakeprobs= np.cumsum(probs[0])        
    random_float = rd.random() #random num generator to see which path ant will take 
    
    for i in range(n_cities):        
        if(fakeprobs[i]>=random_float):
            next_city = i
            if(node+1<n_cities):
                temp_AP[ant][node+1][0] = next_city
            break
    return next_city

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
    for i in range(n):
        ans.append(0)
    return tuple(ans)

def random_colouring(hypercube_main):
    hypercube = {key:copy.deepcopy(value) for key,value in hypercube_main.items()}
    edge_colours = {"red": {}, "blue": {}}
    while len(hypercube) != 0:
        random_vertex_start = rd.choice(list(hypercube.keys()))
        random_vertex_end = rd.choice(hypercube[random_vertex_start])
        
        if random_vertex_start in edge_colours['red']:
            edge_colours['red'][random_vertex_start].append(random_vertex_end)
        else:
            edge_colours['red'][random_vertex_start] = [random_vertex_end]

        if random_vertex_end in edge_colours['red']:
            edge_colours['red'][random_vertex_end].append(random_vertex_start)
        else:
            edge_colours['red'][random_vertex_end] =[random_vertex_start]
        
        if invert_tuple(random_vertex_start) in edge_colours['blue']:
            edge_colours['blue'][invert_tuple(random_vertex_start)].append(invert_tuple(random_vertex_end))
        else:
            edge_colours['blue'][invert_tuple(random_vertex_start)] = [invert_tuple(random_vertex_end)]
            
        if invert_tuple(random_vertex_end) in edge_colours['blue']:
            edge_colours['blue'][invert_tuple(random_vertex_end)].append(invert_tuple(random_vertex_start))
        else:
            edge_colours['blue'][invert_tuple(random_vertex_end)] = [invert_tuple(random_vertex_start)]
            
        hypercube[random_vertex_start].remove(random_vertex_end)
        if len(hypercube[random_vertex_start]) == 0:
            del hypercube[random_vertex_start]
            
        hypercube[random_vertex_end].remove(random_vertex_start)
        if len(hypercube[random_vertex_end]) == 0:
            del hypercube[random_vertex_end]
            
        hypercube[invert_tuple(random_vertex_start)].remove(invert_tuple(random_vertex_end))
        if len(hypercube[invert_tuple(random_vertex_start)]) == 0:
            del hypercube[invert_tuple(random_vertex_start)]
            
        hypercube[invert_tuple(random_vertex_end)].remove(invert_tuple(random_vertex_start))
        if len(hypercube[invert_tuple(random_vertex_end)]) == 0:
            del hypercube[invert_tuple(random_vertex_end)]
    
    return edge_colours

def invert_num(n):
    if n ==0: return 1
    return 0

def generate_n_matchings(adj_list):
    n = int(math.log(len(adj_list),2))
    ans = {}
    for i in range(n):
        ans[i] = {key:list(key) for key in adj_list}

    for ind in ans:
        for key, value in ans[ind].items(): 
            value[ind] = invert_num(value[ind])
            ans[ind][key] = tuple(value)
    return ans

def calc_hypercube_prob(ant, adj_list, colored_adj_list, alpha, beta, possible_vertices):
    curr_vertex = ant.last_visited
    def is_same_col(ant, choice_vertex, colored_adj_list):
        curr_col = ant.curr_color
        if curr_vertex in colored_adj_list[curr_col]: 
            if choice_vertex in colored_adj_list[curr_col][curr_vertex]:
                return True
            return False
    probs = {} #keys -> probs; vals -> connected vertices
    sumprob=0
    n = int(math.log(len(adj_list),2))
    for j in range(len(possible_vertices)): #sum of all the paths the ant can take ( denominator )

        temp_connected_vertex = possible_vertices[j] #one of the connected vertices
        same_col_weight = 1 if is_same_col(ant, temp_connected_vertex, colored_adj_list) else 0.8
        dist_from_end = n - sum(temp_connected_vertex) if n - sum(temp_connected_vertex) != 0 else 0.5
        sumprob += ((1/dist_from_end)**alpha)*(same_col_weight**beta) 

    for j in range(len(possible_vertices)): #probability for each path

        temp_connected_vertex = possible_vertices[j] #one of the connected vertices
        same_col_weight = 1 if is_same_col(ant, temp_connected_vertex, colored_adj_list) else 0.8
        dist_from_end = n - sum(temp_connected_vertex) if n - sum(temp_connected_vertex) != 0 else 0.5
        probs_key = (((1/dist_from_end)**alpha)*(same_col_weight**beta))/sumprob
        if probs_key not in probs:
            probs[probs_key] = [temp_connected_vertex]
        else:
            probs[probs_key].append(temp_connected_vertex)

    probs = dict(sorted(probs.items(), key=lambda item: item[0]))
    return probs


class Ant:
    def __init__(self, number, curr_color = None) -> None:
        self.has_changed_col = False
        self.number = number
        self.curr_color = curr_color
        self.history_vertices = []
        self.is_violated = False
        self.last_visited = {}
        self.history_colours = []
        self.last_vertex_before_color_change = None

    def __str__(self):
        return f"Ant {self.number}"

    def set_curr_color(self, col):
        self.curr_color = col
        self.history_colours.append(col)
        
    def set_has_changed_col(self):
        if self.has_changed_col:
            self.is_violated = True
        self.has_changed_col = True
        
    def add_to_visited(self, end_vertex):
    
        self.history_vertices.append(end_vertex)
        if not self.has_changed_col:
            self.last_vertex_before_color_change = end_vertex
        self.last_visited = end_vertex
        
    def add_to_history_colours(self, col):
        self.history_colours.append(col) 
        
    def reset_to_last_color_change_state(self):
        self.last_visited = self.last_vertex_before_color_change
        # self.is_violated = True
        self.history_vertices = self.history_vertices[: self.history_vertices.index(self.last_vertex_before_color_change)+1]
        self.has_changed_col = False
        self.add_to_history_colours(get_opp_color(self.curr_color))
        self.curr_color = get_opp_color(self.curr_color)
        
    def status(self):
        print(f"self.number: {self.number}")
        print(f"self.curr_color: {self.curr_color}")
        print(f"self.history_vertices: {self.history_vertices}")
        print(f"self.is_violated: {self.is_violated}")
        print(f"self.last_visited: {self.last_visited}")
        print(f"self.history_colours: {self.history_colours}")
        print(f"self.last_vertex_before_color_change: {self.last_vertex_before_color_change}")
        return

    def get_path_len(self):
        path_length = len(self.history_vertices)
        return self.number, path_length -1


def get_col(adj_list_random_colour, start_vertex, end_vertex):
    if end_vertex in adj_list_random_colour['red'].get(start_vertex, []):
        return 'red'
    else:
        return 'blue'

def get_opp_color(color):
    if color == "blue":
        return "red"
    else:
        return "blue"
    
def change_to_gray(color):
    if color == 'blue':
        return "#8CD8FF"
    else:
        return "#FFC2CB"

    
#JUST ADDING FOR FUN!