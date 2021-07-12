#Helper functions
import networkx
from networkx.generators.random_graphs import fast_gnp_random_graph
import numpy as np
import random as rd
import copy
from numpy import inf
import sys

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
print(make_hypercube_matrix(3))

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

def random_colouring(hypercube):
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

print("edge colours is ")
print(random_colouring(make_hypercube_matrix(3)))

class Ant:
    def __init__(self, number, curr_color = None) -> None:
        self.has_changed_col = False
        self.number = number
        self.curr_color = curr_color
        self.history_vertices = []
        self.last_visited = {}
        self.history_colours = [self.curr_color]
        self.last_vertex_before_color_change = None

    def __str__(self):
        return f"Ant {self.number}"

    def set_curr_color(self, col):
        self.curr_color = col
        self.history_colours.append(col)
        
    def set_has_changed_col(self):
        self.has_changed_col = True
        
    def add_to_visited(self, end_vertex):
        self.history_vertices.append(end_vertex)
        if not self.has_changed_col:
            self.last_vertex_before_color_change = self.history_vertices[-1]
        self.last_visited = self.history_vertices[-1]
        
    def add_to_history_colours(self, col):
        self.history_colours.append(col) 
        
    def reset_to_last_color_change_state(self):
        self.last_visited = self.last_vertex_before_color_change
        self.history_vertices = self.history_vertices[: self.history_vertices.index(self.last_visited)+1]
        self.has_changed_col = False
        # self.add_to_history_colours(get_opp_color(self.curr_color))
        # self.curr_color = get_opp_color(self.curr_color)
        

def get_col(adj_list_random_colour, start_vertex, end_vertex):
    if start_vertex in adj_list_random_colour['red'] and end_vertex in adj_list_random_colour['red'][start_vertex]:
        return 'red'
    else:
        return 'blue'

def get_opp_color(color):
    if color == "blue":
        return "red"
    else:
        return "blue"
    
    
    