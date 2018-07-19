# -*- coding: utf-8 -*-
#    Copyright (C) 2018 by
#    Marta Grobelna <marta.grobelna@rwth-aachen.de>
#    Petre Petrov <petrepp4@gmail.com>
#    Rudi Floren <rudi.floren@gmail.com>
#    Tobias Winkler <tobias.winkler1@rwth-aachen.de>
#    All rights reserved.
#    BSD license.
#
# Authors:  Marta Grobelna <marta.grobelna@rwth-aachen.de>
#           Petre Petrov <petrepp4@gmail.com>
#           Rudi Floren <rudi.floren@gmail.com>
#           Tobias Winkler <tobias.winkler1@rwth-aachen.de>

import argparse
import logging
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from math import fabs, sqrt
import copy
import networkx as nx
import networkx.algorithms.isomorphism as iso
from networkx.algorithms import isomorphism
from test_data_creation import create_data
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge
from framework.utils import Counter
counter = Counter()

# Define colors for output
COLOR_RED = '\033[91m'
COLOR_GREEN = '\033[92m'
COLOR_BLUE = '\033[94m'
COLOR_END = '\033[0m'


def ___stat_test_binary_trees(data, trees, size, tolerance):
    print(COLOR_BLUE + "                  BINARY TREE TEST" + COLOR_END)
    ___get_avr_num_trials(data)
    ___get_avr_time(data)
    num_graphs = ___calculate_number_of_possible_graphs(size, 'binary_tree')
    graphs = ___non_isomorphic_graphs_dict(trees)
    if size != 0:
        dist = ___test_uniform_distribution(graphs, tolerance)
    else:
        dist = ___test_poisson_distribution(graphs, tolerance) 
    ___draw_size_distribution_diagram(graphs, tolerance)

    return dist

def ___get_avr_num_trials(data):  
    trials = data.copy().trials
    avr = 0
    for l in trials:
        avr += int(l)
    avr = avr / len(trials)
    print("Avr. No. trials..........................{}".format(avr))

def ___get_avr_time(data):
    times = data.copy().time
    avr = 0
    for l in times:
        avr += float(l)
    avr = avr / len(times)
    print("Avr. comp. time..........................{}".format(avr))

def ___get_avr_btree_height(data, size):
    # Average height of a btree is asymptotic to 2* sqrt(pi * n)
    avr = 2 * sqrt(2 * size)
    print("Avr. binary tree height..................{}".format(avr))

    # Check what average height our trees have
    graphs = list(data.keys())
    heights = []
    for g in graphs:
        init_half_edge = g.get_half_edge()
        if init_half_edge.opposite is not None:
            half_edge_list = init_half_edge.list_half_edges()
            for h in half_edge_list:
                if h.opposite is None:
                    init_half_edge = h
                    break
        g_height = ___get_tree_height(init_half_edge)
        heights.append(g_height)
    avr = 0
    for h in heights:
        avr += h
    avr = avr / len(heights)
    print("Avr. sampled tree height.................{}".format(avr))


def ___get_tree_height(init_half_edge, height=0):
    if init_half_edge is None:
        return height - 1

    left = ___get_tree_height(init_half_edge.next.opposite, height+1)
    right = ___get_tree_height(init_half_edge.prior.opposite, height+1)

    if left > right:
        return left
    else:
        return right

def ___stat_test_three_connected_graphs(data, graphs, size, tolerance):
    print(COLOR_BLUE + "              THREE CONNECTED TEST" + COLOR_END)
    # Calculate average number of trials to get the right size
    ___get_avr_num_trials(data)
    ___get_avr_time(data)
    #___calculate_number_of_possible_graphs(size, "three_connected")
    dist, graphs = ___test_uniform_distribution(graphs, tolerance) 
 
    return dist
    
def ___stat_test_two_connected_graphs(data, graphs, size, tolerance):
    print(COLOR_BLUE + "                TWO CONNECTED TEST" + COLOR_END)
    # Calculate average number of trials to get the right size
    ___get_avr_num_trials(data)
    ___get_avr_time(data)
    #___calculate_number_of_possible_graphs(size, "three_connected")
    dist, graphs = ___test_uniform_distribution(graphs, tolerance) 
 
    return dist

def ___stat_test_one_connected_graphs(data, graphs, size, tolerance):
    print(COLOR_BLUE + "                 ONE CONNECTED TEST" + COLOR_END)
    # Calculate average number of trials to get the right size
    ___get_avr_num_trials(data)
    ___get_avr_time(data)
    #___calculate_number_of_possible_graphs(size, "three_connected")
    dist, graphs = ___test_uniform_distribution(graphs, tolerance) 
 
    return dist

def ___stat_test_planar_graphs(data, graphs, size, tolerance):
    special_graphs = ___test_for_special_graphs(graphs, size) 
    return special_graphs

# Returns a dictonary of pairwise non-isomorphic graphs with
# frequencies 
def ___non_isomorphic_graphs_dict(objects):
    # Convert to netwokrx graphs
    nx_objects = [o.to_networkx_graph() for o in objects]
    graphs = dict()
    nm = iso.categorical_node_match('color',['black','white'])
    # Filter out isomorphic graphs
    for g1 in nx_objects:
        graphs[g1] = 1
        for g2 in reversed(nx_objects):
            if g2 is not g1 and iso.is_isomorphic(g1,g2,node_match=nm):
                nx_objects.remove(g2)
                graphs[g1] += 1
        nx_objects.remove(g1)
 
    # for g in graphs:
    #     nx.draw(g, with_labels=True)
    #     plt.show()
    return graphs

# Tests if the graphs frequencies are uniformly distributed using
# Kolmogorov-Smirnov test
def ___test_uniform_distribution(graphs, tolerance):  
    total_num = 0
    graphs_num = len(graphs)
    test_data = list(graphs.values())
    for i in test_data:
        total_num += i
    target = float(total_num / graphs_num)  
    print("Avr. No. graphs per size.................{}".format(target))
    print("No. non-isom. graphs.....................{}".format(graphs_num))

    u = stats.uniform(0, target)
    d, p = stats.kstest(test_data, u.cdf)
    print("KS-test p-value..........................{}".format(p))
    alpha = 0.05
    if p <= alpha:
        print(COLOR_RED + "Kolmogorov-Smirnov Test..................failed" + COLOR_END)
        return False
    print(COLOR_GREEN + "Kolmogorov-Smirnov Test..................passed" + COLOR_END)   
    return True

# Tests if the graphs frequencies are poisson distributed using
# Kolmogorov-Smirnov test
def ___test_poisson_distribution(data, tolerance):
    total_num = 0
    graphs_num = len(data)
    test_data = list(data.values())
    for i in test_data:
        total_num += i
    # Target has to be the maximum likelihood estimator!
    target = float(total_num / graphs_num)
    print("Avr. No. graphs per size.................{}".format(target))
    print("No. non-isom. graphs.....................{}".format(graphs_num))

    pois = stats.poisson(1)
    d, p = stats.kstest(test_data, pois.cdf)
    print("KS-test p-value..........................{}".format(p))
    alpha = 0.05
    if p <= alpha:
        print(COLOR_RED + "Kolmogorov-Smirnov Test..................failed" + COLOR_END)
        return False
    print(COLOR_GREEN + "Kolmogorov-Smirnov Test..................passed" + COLOR_END)   
    return True

def ___draw_size_distribution_diagram(data, tolerance):
    x_data = [x for x in range(len(data))]
    y_data = list(data.values())
    mean = 0
    for y in y_data:
        mean += y
    mean = mean / len(data)
    tolerance = mean * tolerance
    _, ax = plt.subplots()
    # Draw bars, position them in the center of the tick mark on the x-axis
    ax.bar(x_data, y_data, color = '#539caf', align = 'center')
    ax.axhline(mean, color='green', linewidth=2)
    ax.axhline(mean+tolerance, color='green', linewidth=1)
    ax.axhline(mean-tolerance, color='green', linewidth=1)
    ax.set_ylabel("Number of graphs")
    ax.set_xlabel("Graph type")
    ax.set_title("Occurance of Different Graph Types")
    plt.show()

def ___draw_most_frequent_graph(graphs):
    max_number = -1
    max_graph = None
    for g in graphs:
        if graphs[g] > max_number:
            max_number = graphs[g]
            max_graph = g
    nx.draw(max_graph)
    plt.title('The Most Frequent Graph')
    plt.show()

def ___draw_least_frequent_graph(graphs):
    min_number = float("inf")
    min_graph = None
    for g in graphs:
        if graphs[g] < min_number:
            min_number = graphs[g]
            min_graph = g
    nx.draw(min_graph)
    plt.title('The Least Frequent Graph')
    plt.show()
    
def ___calculate_number_of_possible_graphs(size, object_class):
    # Verify if this numbers are really correct
    if object_class is "binary_tree":
        sizes = [1, 1, 1, 1, 4, 6, 12, 20, 30]
    elif object_class is "three_connected":
        # 	Number of labeled 3-connected graphs with n nodes. 
        sizes = [1, 26, 1768, 225096, 51725352, 21132802544, 15463799747936]
    elif object_class is "two_connected":
        # Number of 2-connected planar graphs on n labeled nodes
        sizes = [1, 10, 237, 10707, 774924, 78702536, 10273189176, 1631331753120]
    elif object_class is "one_connected":
        # Number of connected labeled graphs with n nodes. 
        sizes = [1, 1, 1, 4, 38, 728, 26704, 1866256, 251548592, 66296291072, 34496488594816]
    elif object_class is "planar_graph":
        # Number of planar graphs on n labeled nodes.
        sizes =[1, 1, 2, 8, 64, 1023, 32071, 1823707, 163947848, 20402420291]
    else:
        raise Exception("No such object.")
    
    if len(sizes) < size:
        print("No. graphs...............................unknown")
        return None
    else:
        print("No.graphs................................{}".format(sizes[size - 1]))
        return sizes[size - 1]

def ___test_for_special_graphs(graphs, size):
    cycle = nx.cycle_graph(size)   
    path = nx.path_graph(size)
    star = nx.star_graph(size)
    cycl_ladder = nx.circular_ladder_graph(size)
    ladder = nx.ladder_graph(size)
    wheel = nx.wheel_graph(size)

    cycle_found = False
    path_found = False
    star_found = False
    cycl_ladder_found = False
    ladder_found = False
    wheel_found = False

    # Check if we sampled on of this special graphs
    for g in graphs:
        if nx.is_isomorphic(g, cycle):
            cycle_found = True         
        if nx.is_isomorphic(g, path):
            path_found = True
        if nx.is_isomorphic(g, star):
            star_found = True
        if nx.is_isomorphic(g, cycl_ladder):
            cycl_ladder_found = True
        if nx.is_isomorphic(g, ladder):
            ladder_found = True
        if nx.is_isomorphic(g, wheel):
            wheel_found = True


    print("Sampled cycle............................{}".format(cycle_found))
    print("Sampled path.............................{}".format(path_found))
    print("Sampled star.............................{}".format(star_found))
    print("Sampled circular ladder..................{}".format(cycl_ladder_found))
    print("Sampled ladder...........................{}".format(ladder_found))
    print("Sampled wheel............................{}".format(wheel_found))

    passed = cycle_found and path_found and star_found and cycl_ladder_found and ladder_found and wheel_found
    return passed

def ___analyse_fusys_data(file_name):
    nx_objects = ___fusy_graphs_to_networkx(file_name)
    graphs = dict()
    # Filter out isomorphic graphs
    for g1 in nx_objects:
        graphs[g1] = 1
        for g2 in reversed(nx_objects):
            if g2 is not g1 and iso.is_isomorphic(g1,g2):
                nx_objects.remove(g2)
                graphs[g1] += 1
        nx_objects.remove(g1)

    print("No. of graphs............................{}".format(len(graphs)))
    dist = ___test_uniform_distribution(graphs, 20)
    ___draw_size_distribution_diagram(graphs, 20)

    data = []
    with open("fusy_stat.txt") as file:
        for l in file:
            line_list = l.split(' ')
            data.append(tuple(line_list))
    print("No. sampled graphs.......................{}".format(len(data)))
    labels = ["trials", "nodes"]
    data_frame = pd.DataFrame.from_records(data, columns = labels)

    ___get_avr_num_trials(data_frame)

            
def ___parse_data(file_name):
    data = []
    with open(file_name) as file:
        for l in file:
            line_list = l.split(' ')
            line_list.remove('\n')
            data.append(tuple(line_list))
    print("No. sampled graphs.......................{}".format(len(data)))
    return data

def ___parse_fusy_graphs(file_name):
    data = []
    create_new_list = True
    with open(file_name) as file:      
        for l in file:
            if l != '\n':
                if l[0] == 'P':  
                    if create_new_list:
                        graph = []
                        create_new_list = False
                    else:
                        data.append(graph)
                        graph = []
                else:
                    line_list = l.split(' ')
                    node1 = int(line_list[0])
                    node2 = int(line_list[1])                 
                    if node1 != node2:
                        edge = (node1, node2)
                        graph.append(edge)
    return data

def ___fusy_graphs_to_networkx(file_name):
    fusy_graphs = ___parse_fusy_graphs(file_name)
    ntwx_graphs = []

    for elist in fusy_graphs:
        G = nx.Graph()
        G.add_edges_from(elist)
        ntwx_graphs.append(G)

    return ntwx_graphs

def ___file_to_data_frame(file_name):
    data = ___parse_data(file_name)
    labels = []
    if file_name is "binary_tree":
        labels = ["nodes", "leaves", "trials", "time"]
    elif file_name is "fusy_stat.txt":
        labels = ["trials", "nodes", "edges"]
    elif file_name is "fusy_stat_btree.txt":
        labels = ["trials", "nodes"]
    else:
        labels = ["nodes", "edges", "trials", "time"]

    data_frame = pd.DataFrame.from_records(data, columns = labels)
    return data_frame

def main():
    argparser = argparse.ArgumentParser(description='Test stuff')
    argparser.add_argument('-d', dest='loglevel', action='store_const', const=logging.DEBUG, help='Print Debug info')
    argparser.add_argument('-b', '--binary-tree', action='store_true', help='Make statistical tests for binary trees')
    argparser.add_argument('-three', '--three_connectd', action='store_true', help='Make statistical tests for three connected graphs')
    argparser.add_argument('-two', '--two_connected', action='store_true', help='Make statistical tests for two connected graphs')
    argparser.add_argument('-one', '--one_connected', action='store_true', help='Make statistical tests for one connected graphs')
    argparser.add_argument('-planar', '--planar_graph', action='store_true', help='Make statistical tests for planar graphs')
    argparser.add_argument('-plot', '--plot_distribution', action='store_true', help='Plot the distribution of the different graph types')
    argparser.add_argument('-fusy', '--analyse_fusy', action='store_true', help='Analyse data produced by Fusy`s implementation')
    argparser.add_argument('samples', type=int, help="Sample x number of time.")
    argparser.add_argument('size', type=int, help="Sample object of a certain size.")
    argparser.add_argument('tolerance', type=int, help="Tolerance for test")

    args = argparser.parse_args()
    logging.basicConfig(level=args.loglevel)

    sample_num = args.samples
    samples_size = args.size
    tolerance = args.tolerance / 100
    passed = False
    comb_class = None

    if args.binary_tree:
        comb_class = "binary tree"
        tree_list = create_data("binary_tree", sample_num, samples_size)
        data = ___file_to_data_frame("binary_tree")
        passed = ___stat_test_binary_trees(data, tree_list, samples_size, tolerance)     
    elif args.three_connectd:
        print(COLOR_BLUE + "              THREE-CONNECTED TEST" + COLOR_END)
        comb_class = "three-connected"
        graph_list = create_data("three_connected", sample_num, samples_size)
        data = ___file_to_data_frame("three_connected")
        passed = ___stat_test_three_connected_graphs(data, graph_list, samples_size, tolerance)
    elif args.two_connected:
        print(COLOR_BLUE + "                  TWO-CONNECTED TEST" + COLOR_END)
        comb_class = "two-connected"
        graph_list = create_data("two_connected", sample_num, samples_size)
        data = ___file_to_data_frame("two_connected")
        passed = ___stat_test_two_connected_graphs(data, graph_list, samples_size, tolerance)
    elif args.one_connected:
        print(COLOR_BLUE + "                  ONE-CONNECTED TEST" + COLOR_END)
        comb_class = "one-connected"
        graph_list = create_data("one_connected", sample_num, samples_size)
        data = ___file_to_data_frame("one_connected")
        passed = ___stat_test_one_connected_graphs(data, graph_list, samples_size, tolerance)
    elif args.planar_graph:
        print(COLOR_BLUE + "                 PLANAR GRAPH TEST" + COLOR_END)
        comb_class = "planar graph"
        graph_list = create_data("planar_graph", sample_num, samples_size)
        data = ___file_to_data_frame("planar_graph")
        passed = ___stat_test_planar_graphs(data, graph_list, samples_size, tolerance)
    elif args.analyse_fusy:
        print(COLOR_BLUE + "                ANALYSE FUSYS DATA" + COLOR_END)
        ___analyse_fusys_data("fusy_graphs_btree.txt")
    else:
        raise Exception("Wrong combinatorial class.")

    if passed:
        print(COLOR_GREEN + '{} test.........................PASSED'.format(comb_class) + COLOR_END)
    else:
        print(COLOR_RED + '{} test.........................FAILED'.format(comb_class) + COLOR_END) 


def ___small_test_tree_black():
    half_edges = [HalfEdge() for i in range(15)]

    number = next(counter)
    half_edges[0].opposite = None
    half_edges[0].next = half_edges[1]
    half_edges[0].prior = half_edges[2]
    half_edges[0].node_nr = number
    half_edges[0].color = 'black'

    half_edges[1].opposite = half_edges[3]
    half_edges[1].next = half_edges[2]
    half_edges[1].prior = half_edges[0]
    half_edges[1].node_nr = number
    half_edges[1].color = 'black'

    half_edges[2].opposite = half_edges[6]
    half_edges[2].next = half_edges[0]
    half_edges[2].prior = half_edges[1]
    half_edges[2].node_nr = number
    half_edges[2].color = 'black'

    number = next(counter)
    half_edges[3].opposite = half_edges[1]
    half_edges[3].next = half_edges[4]
    half_edges[3].prior = half_edges[5]
    half_edges[3].node_nr = number
    half_edges[3].color = 'white'

    half_edges[4].opposite = None
    half_edges[4].next = half_edges[5]
    half_edges[4].prior = half_edges[3]
    half_edges[4].node_nr = number
    half_edges[4].color = 'white'

    half_edges[5].opposite = None
    half_edges[5].next = half_edges[3]
    half_edges[5].prior = half_edges[4]
    half_edges[5].node_nr = number
    half_edges[5].color = 'white'

    number = next(counter)
    half_edges[6].opposite = half_edges[2]
    half_edges[6].next = half_edges[7]
    half_edges[6].prior = half_edges[8]
    half_edges[6].node_nr = number
    half_edges[6].color = 'white'

    half_edges[7].opposite = half_edges[9]
    half_edges[7].next = half_edges[8]
    half_edges[7].prior = half_edges[6]
    half_edges[7].node_nr = number
    half_edges[7].color = 'white'

    half_edges[8].opposite = half_edges[12]
    half_edges[8].next = half_edges[6]
    half_edges[8].prior = half_edges[7]
    half_edges[8].node_nr = number
    half_edges[8].color = 'white'

    number = next(counter)
    half_edges[9].opposite = half_edges[7]
    half_edges[9].next = half_edges[10]
    half_edges[9].prior = half_edges[11]
    half_edges[9].node_nr = number
    half_edges[9].color = 'black'

    half_edges[10].opposite = None
    half_edges[10].next = half_edges[11]
    half_edges[10].prior = half_edges[9]
    half_edges[10].node_nr = number
    half_edges[10].color = 'black'

    half_edges[11].opposite = None
    half_edges[11].next = half_edges[9]
    half_edges[11].prior = half_edges[10]
    half_edges[11].node_nr = number
    half_edges[11].color = 'black'

    number = next(counter)
    half_edges[12].opposite = half_edges[8]
    half_edges[12].next = half_edges[13]
    half_edges[12].prior = half_edges[14]
    half_edges[12].node_nr = number
    half_edges[12].color = 'black'

    half_edges[13].opposite = None
    half_edges[13].next = half_edges[14]
    half_edges[13].prior = half_edges[12]
    half_edges[13].node_nr = number
    half_edges[13].color = 'black'

    half_edges[14].opposite = None
    half_edges[14].next = half_edges[12]
    half_edges[14].prior = half_edges[13]
    half_edges[14].node_nr = number
    half_edges[14].color = 'black'

    return half_edges[0]

def ___small_test_tree_white():
    half_edges = [HalfEdge() for i in range(15)]

    number = next(counter)
    half_edges[0].opposite = None
    half_edges[0].next = half_edges[1]
    half_edges[0].prior = half_edges[2]
    half_edges[0].node_nr = number
    half_edges[0].color = 'white'

    half_edges[1].opposite = half_edges[3]
    half_edges[1].next = half_edges[2]
    half_edges[1].prior = half_edges[0]
    half_edges[1].node_nr = number
    half_edges[1].color = 'white'

    half_edges[2].opposite = half_edges[6]
    half_edges[2].next = half_edges[0]
    half_edges[2].prior = half_edges[1]
    half_edges[2].node_nr = number
    half_edges[2].color = 'white'

    number = next(counter)
    half_edges[3].opposite = half_edges[1]
    half_edges[3].next = half_edges[4]
    half_edges[3].prior = half_edges[5]
    half_edges[3].node_nr = number
    half_edges[3].color = 'black'

    half_edges[4].opposite = None
    half_edges[4].next = half_edges[5]
    half_edges[4].prior = half_edges[3]
    half_edges[4].node_nr = number
    half_edges[4].color = 'black'

    half_edges[5].opposite = None
    half_edges[5].next = half_edges[3]
    half_edges[5].prior = half_edges[4]
    half_edges[5].node_nr = number
    half_edges[5].color = 'black'

    number = next(counter)
    half_edges[6].opposite = half_edges[2]
    half_edges[6].next = half_edges[7]
    half_edges[6].prior = half_edges[8]
    half_edges[6].node_nr = number
    half_edges[6].color = 'black'

    half_edges[7].opposite = half_edges[9]
    half_edges[7].next = half_edges[8]
    half_edges[7].prior = half_edges[6]
    half_edges[7].node_nr = number
    half_edges[7].color = 'balck'

    half_edges[8].opposite = None
    half_edges[8].next = half_edges[6]
    half_edges[8].prior = half_edges[7]
    half_edges[8].node_nr = number
    half_edges[8].color = 'black'

    number = next(counter)
    half_edges[9].opposite = half_edges[7]
    half_edges[9].next = half_edges[10]
    half_edges[9].prior = half_edges[11]
    half_edges[9].node_nr = number
    half_edges[9].color = 'white'

    half_edges[10].opposite = None
    half_edges[10].next = half_edges[11]
    half_edges[10].prior = half_edges[9]
    half_edges[10].node_nr = number
    half_edges[10].color = 'white'

    half_edges[11].opposite = None
    half_edges[11].next = half_edges[9]
    half_edges[11].prior = half_edges[10]
    half_edges[11].node_nr = number
    half_edges[11].color = 'white'

    number = next(counter)
    half_edges[12].opposite = half_edges[8]
    half_edges[12].next = half_edges[13]
    half_edges[12].prior = half_edges[14]
    half_edges[12].node_nr = number
    half_edges[12].color = 'white'

    half_edges[13].opposite = None
    half_edges[13].next = half_edges[14]
    half_edges[13].prior = half_edges[12]
    half_edges[13].node_nr = number
    half_edges[13].color = 'white'

    half_edges[14].opposite = None
    half_edges[14].next = half_edges[12]
    half_edges[14].prior = half_edges[13]
    half_edges[14].node_nr = number
    half_edges[14].color = 'white'

    return half_edges[0]

def ___test_tree():
    half_edges = [HalfEdge() for i in range(27)]

    number = next(counter)
    half_edges[0].opposite = None
    half_edges[0].next = half_edges[1]
    half_edges[0].prior = half_edges[2]
    half_edges[0].node_nr = number

    half_edges[1].opposite = half_edges[3]
    half_edges[1].next = half_edges[2]
    half_edges[1].prior = half_edges[0]
    half_edges[1].node_nr = number

    half_edges[2].opposite = half_edges[12]
    half_edges[2].next = half_edges[0]
    half_edges[2].prior = half_edges[1]
    half_edges[2].node_nr = number

    number = next(counter)
    half_edges[3].opposite = half_edges[1]
    half_edges[3].next = half_edges[4]
    half_edges[3].prior = half_edges[5]
    half_edges[3].node_nr = number

    half_edges[4].opposite = half_edges[6]
    half_edges[4].next = half_edges[5]
    half_edges[4].prior = half_edges[3]
    half_edges[4].node_nr = number

    half_edges[5].opposite = half_edges[9]
    half_edges[5].next = half_edges[3]
    half_edges[5].prior = half_edges[4]
    half_edges[5].node_nr = number

    number = next(counter)
    half_edges[6].opposite = half_edges[4]
    half_edges[6].next = half_edges[7]
    half_edges[6].prior = half_edges[8]
    half_edges[6].node_nr = number

    half_edges[7].opposite = None
    half_edges[7].next = half_edges[8]
    half_edges[7].prior = half_edges[6]
    half_edges[7].node_nr = number

    half_edges[8].opposite = None
    half_edges[8].next = half_edges[6]
    half_edges[8].prior = half_edges[7]
    half_edges[8].node_nr = number

    number = next(counter)
    half_edges[9].opposite = half_edges[5]
    half_edges[9].next = half_edges[10]
    half_edges[9].prior = half_edges[11]
    half_edges[9].node_nr = number

    half_edges[10].opposite = None
    half_edges[10].next = half_edges[11]
    half_edges[10].prior = half_edges[9]
    half_edges[10].node_nr = number

    half_edges[11].opposite = half_edges[21]
    half_edges[11].next = half_edges[9]
    half_edges[11].prior = half_edges[10]
    half_edges[11].node_nr = number

    number = next(counter)
    half_edges[12].opposite = half_edges[2]
    half_edges[12].next = half_edges[13]
    half_edges[12].prior = half_edges[14]
    half_edges[12].node_nr = number

    half_edges[13].opposite = None
    half_edges[13].next = half_edges[14]
    half_edges[13].prior = half_edges[12]
    half_edges[13].node_nr = number

    half_edges[14].opposite = half_edges[15]
    half_edges[14].next = half_edges[12]
    half_edges[14].prior = half_edges[13]
    half_edges[14].node_nr = number

    number = next(counter)
    half_edges[15].opposite = half_edges[14]
    half_edges[15].next = half_edges[16]
    half_edges[15].prior = half_edges[17]
    half_edges[15].node_nr = number

    half_edges[16].opposite = half_edges[18]
    half_edges[16].next = half_edges[17]
    half_edges[16].prior = half_edges[15]
    half_edges[16].node_nr = number

    half_edges[17].opposite = None
    half_edges[17].next = half_edges[15]
    half_edges[17].prior = half_edges[16]
    half_edges[17].node_nr = number

    number = next(counter)
    half_edges[18].opposite = half_edges[16]
    half_edges[18].next = half_edges[19]
    half_edges[18].prior = half_edges[20]
    half_edges[18].node_nr = number

    half_edges[19].opposite = None
    half_edges[19].next = half_edges[20]
    half_edges[19].prior = half_edges[18]
    half_edges[19].node_nr = number

    half_edges[20].opposite = None
    half_edges[20].next = half_edges[19]
    half_edges[20].prior = half_edges[18]
    half_edges[20].node_nr = number

    number = next(counter)
    half_edges[21].opposite = half_edges[11]
    half_edges[21].next = half_edges[22]
    half_edges[21].prior = half_edges[23]
    half_edges[21].node_nr = number

    half_edges[22].opposite = half_edges[24]
    half_edges[22].next = half_edges[23]
    half_edges[22].prior = half_edges[21]
    half_edges[22].node_nr = number

    half_edges[23].opposite = None
    half_edges[23].next = half_edges[21]
    half_edges[23].prior = half_edges[22]
    half_edges[23].node_nr = number

    number = next(counter)
    half_edges[24].opposite = half_edges[22]
    half_edges[24].next = half_edges[25]
    half_edges[24].prior = half_edges[26]
    half_edges[24].node_nr = number

    half_edges[25].opposite = None
    half_edges[25].next = half_edges[26]
    half_edges[25].prior = half_edges[24]
    half_edges[25].node_nr = number

    half_edges[26].opposite = None
    half_edges[26].next = half_edges[24]
    half_edges[26].prior = half_edges[25]
    half_edges[26].node_nr = number

    return half_edges[0]

if __name__ == '__main__':
    main()


