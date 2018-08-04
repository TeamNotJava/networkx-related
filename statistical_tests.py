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
import sys
import networkx as nx
import networkx.algorithms.isomorphism as iso
from networkx.algorithms import isomorphism
from test_data_creation import create_data
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge
from planar_graph_sampler.grammar.grammar_utils import Counter
counter = Counter()

# Define colors for output
COLOR_RED = '\033[91m'
COLOR_GREEN = '\033[92m'
COLOR_BLUE = '\033[94m'
COLOR_END = '\033[0m'

def ___test_combinatorial_class(comb_class, data, objects, size):
    # Calculate average number of trials to get the right size
    ___get_avr_num_trials(data)
    ___get_avr_time(data)
    ___calculate_number_of_possible_graphs(size, comb_class)
    # Convert to netwokrx graphs
    nx_g = [o.to_networkx_graph(False) for o in objects]
    nx_obj_dict = ___non_isomorphic_graphs_dict(nx_g)
    dist = ___test_uniform_distribution(nx_obj_dict)

    # Tests specific for a certain graph class
    if comb_class is not "binary_tree":
        ___test_for_special_graphs
    elif comb_class is "binary_tree":
        ___get_avr_btree_height(objects, size)

    ___draw_distribution_diagram(nx_obj_dict)
 
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
    # graphs = list(data.keys())
    graphs = data
    heights = []
    for g in graphs:
        init_half_edge = g.half_edge
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
    print("Avr. height of sampled tree..............{}".format(avr))

def ___get_tree_height(init_half_edge, height=0):
    if init_half_edge is None:
        return height - 1

    left = ___get_tree_height(init_half_edge.next.opposite, height+1)
    right = ___get_tree_height(init_half_edge.prior.opposite, height+1)

    if left > right:
        return left
    else:
        return right

# Returns a dictonary of pairwise non-isomorphic graphs with
# frequencies 
def ___non_isomorphic_graphs_dict(objects, node_id=True, colors=True):
    nx_objects =  [nx.relabel.convert_node_labels_to_integers(o) for o in objects]
    graphs = dict() 
    # Add labels as attributes
    for g in nx_objects:
        label = 0
        for n in g.nodes():
            g.nodes[n]['number'] = label
            label += 1

    # Filter out isomorphic graphs
    cm = iso.categorical_node_match('color',(0,'#999999'))
    nm = iso.numerical_node_match('number',0)
    for g1 in nx_objects:
        graphs[g1] = 1
        for g2 in reversed(nx_objects):
            if node_id and colors:
                # The nodes have to have the same id and color
                if g2 is not g1 and iso.is_isomorphic(g1,g2,node_match=cm) and iso.is_isomorphic(g1,g2,node_match=nm):
                    nx_objects.remove(g2)
                    graphs[g1] += 1
            elif node_id and not colors:
                # The nodes have to have the same id but not color
                if g2 is not g1 and iso.is_isomorphic(g1,g2,node_match=nm):
                    nx_objects.remove(g2)
                    graphs[g1] += 1
            elif not node_id and colors:
                # The nodes have to have the same colors but not ids
                if g2 is not g1  and iso.is_isomorphic(g1,g2,node_match=cm):
                    nx_objects.remove(g2)
                    graphs[g1] += 1
            else:
                raise Exception("Isomorphism criterion wrong!")
        nx_objects.remove(g1)
    return graphs

# Tests if the graphs frequencies are uniformly distributed using
# Kolmogorov-Smirnov test
def ___test_uniform_distribution(graphs):  
    total_num = 0
    graphs_num = len(graphs)
    test_data = list(graphs.values())
    for i in test_data:
        total_num += i
    target = float(total_num / graphs_num)  
    print("Avr. No. graphs per size.................{}".format(target))
    print("No. non-isom. graphs.....................{}".format(graphs_num))

    loc, scale = stats.uniform.fit(test_data)
    u = stats.uniform(loc=loc, scale=scale)
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
def ___test_poisson_distribution(data):
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
    #loc, scale = stats.poisson.fit(test_data)
    #pois = stats.poisson(loc=loc, scale=scale)
    d, p = stats.kstest(test_data, pois.cdf)
    print("KS-test p-value..........................{}".format(p))
    alpha = 0.05
    if p <= alpha:
        print(COLOR_RED + "Kolmogorov-Smirnov Test..................failed" + COLOR_END)
        return False
    print(COLOR_GREEN + "Kolmogorov-Smirnov Test..................passed" + COLOR_END)   
    return True

def ___draw_distribution_diagram(data):
    x_data = [x for x in range(len(data))]
    y_data = list(data.values())
    mean = 0
    for y in y_data:
        mean += y
    mean = mean / len(data)
    _, ax = plt.subplots()
    # Draw bars, position them in the center of the tick mark on the x-axis
    ax.bar(x_data, y_data, color = '#539caf', align = 'center')
    ax.axhline(mean, color='green', linewidth=2)
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
        sizes = [1, 2, 6, 24]
    elif object_class is "three_connected":
        # 	Number of labeled 3-connected graphs with n nodes. 
        sizes = [1, 25, 1227, 84672, 7635120, 850626360]
    elif object_class is "two_connected":
        # Number of 2-connected planar graphs on n labeled nodes
        sizes = [1, 10, 237, 10707, 774924, 78702536, 10273189176, 1631331753120]
    elif object_class is "one_connected":
        # Number of connected labeled graphs with n nodes. 
        sizes = [1, 1, 1, 4, 38, 728, 26704, 1866256, 251548592, 66296291072, 34496488594816]
    elif object_class is "planar_graph":
        # Number of planar graphs on n labeled nodes.
        sizes =[1, 1, 4, 38, 727, 26013, 1597690, 149248656]
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
    graphs = ___non_isomorphic_graphs_dict(nx_objects, colors=False)

    dist = ___test_uniform_distribution(graphs)
    ___draw_distribution_diagram(graphs)

    data = []
    with open("fusy_stat_btrees_5.txt") as file:
        for l in file:
            line_list = l.split(' ')
            data.append(tuple(line_list))
    print("No. sampled graphs.......................{}".format(len(data)))
    labels = ["trials", "nodes", "time"]
    data_frame = pd.DataFrame.from_records(data, columns = labels)
    ___get_avr_num_trials(data_frame)

    return dist

# Convert graphs sampled by our code into
# a list.            
def ___parse_data(file_name):
    data = []
    with open(file_name) as file:
        for l in file:
            line_list = l.split(' ')
            line_list.remove('\n')
            data.append(tuple(line_list))
    print("No. sampled graphs.......................{}".format(len(data)))
    return data

# Convert a list of graphs sampled by Fusy's code
# into a list.
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

# Convert graphs sampled by Fusy's code into
#  netowkrx graphs
def ___fusy_graphs_to_networkx(file_name):
    fusy_graphs = ___parse_fusy_graphs(file_name)
    ntwx_graphs = []

    for elist in fusy_graphs:
        G = nx.Graph()
        G.add_edges_from(elist)
        ntwx_graphs.append(G)

    return ntwx_graphs

# Convert a .txt file into a pandas data frame
def ___file_to_data_frame(file_name):
    data = ___parse_data(file_name)
    labels = []
    if file_name is "binary_tree":
        labels = ["nodes", "leaves", "trials", "time"]
    else:
        labels = ["nodes", "edges", "trials", "time"]

    data_frame = pd.DataFrame.from_records(data, columns = labels)
    return data_frame

# This class compares different kinds of graphs sampled by our code
# and the ones sampled by Fusy's code.
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

    args = argparser.parse_args()
    logging.basicConfig(level=args.loglevel)

    sample_num = args.samples
    samples_size = args.size
    passed = False
    comb_class = None

    if args.binary_tree:
        comb_class = "binary tree"
        tree_list = create_data("binary_tree", sample_num, samples_size)
        data = ___file_to_data_frame("binary_tree")     
        passed = ___test_combinatorial_class("binary_tree", data, tree_list, samples_size)
    elif args.three_connectd:
        print(COLOR_BLUE + "              THREE-CONNECTED TEST" + COLOR_END)
        comb_class = "three-connected"
        graph_list = create_data("three_connected", sample_num, samples_size)
        data = ___file_to_data_frame("three_connected")
        passed = ___test_combinatorial_class("three_connected", data, graph_list, samples_size)
    elif args.two_connected:
        print(COLOR_BLUE + "                  TWO-CONNECTED TEST" + COLOR_END)
        comb_class = "two-connected"
        graph_list = create_data("two_connected", sample_num, samples_size)
        data = ___file_to_data_frame("two_connected")
        passed = ___test_combinatorial_class("two_connected", data, graph_list, samples_size)
    elif args.one_connected:
        print(COLOR_BLUE + "                  ONE-CONNECTED TEST" + COLOR_END)
        comb_class = "one-connected"
        graph_list = create_data("one_connected", sample_num, samples_size)
        data = ___file_to_data_frame("one_connected")
        passed = ___test_combinatorial_class("one_connected", data, graph_list, samples_size)
    elif args.planar_graph:
        print(COLOR_BLUE + "                 PLANAR GRAPH TEST" + COLOR_END)
        comb_class = "planar graph"
        graph_list = create_data("planar_graph", sample_num, samples_size)
        data = ___file_to_data_frame("planar_graph")
        passed = ___test_combinatorial_class("planar_graph", data, graph_list, samples_size)
    elif args.analyse_fusy:
        print(COLOR_BLUE + "                ANALYSE FUSYS DATA" + COLOR_END)
        ___analyse_fusys_data("fusy_graphs_btree_5.txt")
    else:
        raise Exception("Wrong combinatorial class.")

    if passed:
        print(COLOR_GREEN + '{} test.........................PASSED'.format(comb_class) + COLOR_END)
    else:
        print(COLOR_RED + '{} test.........................FAILED'.format(comb_class) + COLOR_END) 

if __name__ == '__main__':
    main()


