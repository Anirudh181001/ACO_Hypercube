from ACO_Hypercube_PreDetermined_Random import run_ants_on_hypercube_random_colors
from ACO_Hypercube_PreDetermined_Random_Pheromone import run_ants_on_hypercube_random_colors_optimized

def hypercube_monte_carlo_random(num_points = 100, N = 7, num_ants = 10, fn = run_ants_on_hypercube_random_colors):
    iter_list = []
    path_len_list = []
    ant_winner_list = []
    n_matchings_list = []
    for iter in range(num_points):
        (ant_winner, path_len), iter,  n_matchings = fn(N, num_ants, False, True)
        iter_list.append(iter)
        path_len_list.append(path_len)
        ant_winner_list.append(ant_winner)
        n_matchings_list.append(n_matchings)
    return (iter_list, path_len_list, ant_winner_list, n_matchings_list)


def hypercube_monte_carlo_optimised(num_points = 100, N = 7, num_ants = 10, fn = run_ants_on_hypercube_random_colors_optimized):
    iter_list = []
    path_len_list = []
    ant_winner_list = []
    n_matchings_list = []
    for iter in range(num_points):
        (ant_winner, path_len), iter,  n_matchings = fn(N, num_ants, False, True)
        iter_list.append(iter)
        path_len_list.append(path_len)
        ant_winner_list.append(ant_winner)
        n_matchings_list.append(n_matchings)
    return (iter_list, path_len_list, ant_winner_list, n_matchings_list)