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
import random
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from math import fabs, sqrt
import sys
import networkx as nx
import networkx.algorithms.isomorphism as iso
from networkx.algorithms import isomorphism
from test_data_creation import create_data
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge
from planar_graph_sampler.grammar.grammar_utils import Counter
from planar_graph_sampler.grammar.planar_graph_decomposition import bij_connected_comps
counter = Counter()

# Define colors for output
COLOR_RED = '\033[91m'
COLOR_GREEN = '\033[92m'
COLOR_BLUE = '\033[94m'
COLOR_END = '\033[0m'

def ___test_combinatorial_class(comb_class, data, nx_objects, size, btrees=None):
    # Calculate average number of trials to get the right size
    ___get_avr_num_trials(data)
    ___get_avr_time(data)
    ___calculate_number_of_possible_graphs(size, comb_class)

    # Remove all pairwise isomorphic graphs
    nx_obj_dict = ___non_isomorphic_graphs_dict(nx_objects)

    # Calculate edges/nodes ratio for each of the sampled graphs
    ___ratio_edges_vertices(list(nx_obj_dict.keys()))

    # Draw the distribution of node degrees
    ___vertex_degrees_distributions(list(nx_obj_dict.keys()))

    # Tests specific for a certain graph class
    if comb_class is not "binary_tree":
        ___test_for_special_graphs(nx_obj_dict, size)
    elif comb_class is "binary_tree" and btrees is not None:
        ___get_avr_btree_height(btrees, size)

    ___draw_distribution_diagram(nx_obj_dict)

     # Make distribution tests
    ___test_uniform_distribution(nx_obj_dict)
    ___chi_square_test(nx_obj_dict)

def ___chi_square_test(graphs):
    data = list(graphs.values())
    _, p = stats.chisquare(data)
    alpha = 0.05
    
    print("Chi-Square p-value.......................{}".format(p))
    if p <= alpha:
        print(COLOR_RED + "Chi-Square Test..........................failed" + COLOR_END)
    else:
        print(COLOR_GREEN + "Chi-Square Test..........................passed" + COLOR_END)   

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

def ___get_avr_btree_height(graphs, size, derived=True):
    # Average height of a btree is asymptotic to 2* sqrt(pi * n)
    avr = 2 * sqrt(2 * size)
    print("Avr. binary tree height..................{}".format(avr))

    # Check what average height our trees have
    heights = []
    for g in graphs:
        if not derived:
            init_half_edge = g.half_edge
        else:
            init_half_edge = g.base_class_object.half_edge
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
    print("Avr. height of sampled trees.............{}".format(avr))

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
def ___non_isomorphic_graphs_dict(nx_objects):
    # nx_objects =  [nx.relabel.convert_node_labels_to_integers(o, label_attribute='number') for o in objects]

    # Add labels as attributes
    for g in nx_objects:
        node_number = len(g.nodes())
        labels = random.sample(range(node_number), node_number)
        i = 0
        for n in g.nodes():
            g.nodes[n]['number'] = labels[i]
            i += 1


    # Filter out isomorphic graphs
    nm = iso.numerical_node_match('number',0)

    graphs = dict() 
    checked = []
    for g in nx_objects:
        if g not in checked:
            isomorphic = [x for x in nx_objects if iso.is_isomorphic(x, g, node_match=nm)]
            graphs[g] = len(isomorphic)
            checked = checked + isomorphic

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
    _, p = stats.kstest(test_data, u.cdf)
    print("KS-test p-value..........................{}".format(p))
    alpha = 0.05
    if p <= alpha:
        print(COLOR_RED + "Kolmogorov-Smirnov Test..................failed" + COLOR_END)
    else:
        print(COLOR_GREEN + "Kolmogorov-Smirnov Test..................passed" + COLOR_END)   

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
    _, p = stats.kstest(test_data, pois.cdf)
    print("KS-test p-value..........................{}".format(p))
    alpha = 0.05
    if p <= alpha:
        print(COLOR_RED + "Kolmogorov-Smirnov Test..................failed" + COLOR_END)
    else:
        print(COLOR_GREEN + "Kolmogorov-Smirnov Test..................passed" + COLOR_END)   

def ___draw_distribution_diagram(data):
    x_data = [x for x in range(len(data))]
    y_data = list(data.values())
    mean = 0
    for y in y_data:
        mean += y
    mean = mean / len(data)
    _ , ax = plt.subplots()
    # Draw bars, position them in the center of the tick mark on the x-axis
    ax.bar(x_data, y_data, color = '#539caf', align = 'center')
    ax.axhline(mean, color='green', linewidth=2)
    ax.set_ylabel("Number of isomorphic graphs")
    ax.set_xlabel("Graph type")
    ax.set_title("Distribution of Graphs")
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
        sizes = [1, 25, 1227, 84672, 7635120, 850626360, 112876089480, 17381709797760]
    elif object_class is "two_connected":
        # Number of 2-connected planar graphs on n labeled nodes
        sizes = [10, 237, 10707, 774924, 78702536, 10273189176, 1631331753120]
    elif object_class is "one_connected":
        # Number of connected labeled graphs with n nodes. 
        sizes = [1, 1, 4, 38, 728, 26704, 1866256, 251548592, 66296291072, 34496488594816]
    elif object_class is "planar_graph":
        # Number of planar graphs on n labeled nodes.
        sizes =[1, 2, 8, 64, 1023, 32071, 1823707, 163947848, 20402420291, 3209997749284]
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

def ___analyse_fusys_data(size, all=True, bin=False, three=False, two=False, one=False, planar=False):
    if bin or all:
        print("                Binary Trees               ")
        nx_objects = ___graphs_list_to_networkx("distribution_tests results/Fusy/fusy_graphs_btree_5.txt")
        data = ___parse_fusys_data("distribution_tests results/Fusy/fusy_stat_btree_5.txt", btree=True)
        ___test_combinatorial_class("binary_tree", data, nx_objects, size)
    if three or all:
        print("               Three Connected             ")
        nx_objects = ___graphs_list_to_networkx("distribution_tests results/Fusy/fusy_graphs_3conn_5.txt")
        data = ___parse_fusys_data("distribution_tests results/Fusy/fusy_stat_3conn_5.txt")
        ___test_combinatorial_class("three_connected", data, nx_objects, size)
    if two or all:
        print("               Two Connected               ")
        nx_objects = ___graphs_list_to_networkx("distribution_tests results/Fusy/fusy_graphs_2conn_5.txt")
        data = ___parse_fusys_data("distribution_tests results/Fusy/fusy_stat_2conn_5.txt")
        ___test_combinatorial_class("two_connected", data, nx_objects, size)
    if one or all:
        print("               One Connected               ")
        nx_objects = ___graphs_list_to_networkx("distribution_tests results/Fusy/fusy_graphs_1conn_5.txt")
        data = ___parse_fusys_data("distribution_tests results/Fusy/fusy_stat_1conn_5.txt")
        ___test_combinatorial_class("one_connected", data, nx_objects, size)
    if planar or all:
        print("               Planar Graphs               ")
        nx_objects = ___graphs_list_to_networkx("distribution_tests results/Fusy/fusy_graphs_planar_5.txt")
        data = ___parse_fusys_data("distribution_tests results/Fusy/fusy_stat_planar_5.txt")
        ___test_combinatorial_class("planar_graph", data, nx_objects, size)
    
def ___parse_fusys_data(file_name, btree=False):
    data = []
    with open(file_name) as file:
        for l in file:
            line_list = l.split(' ')
            data.append(tuple(line_list))
    print("No. sampled graphs.......................{}".format(len(data)))

    # Create data frame from statistics file
    if btree:
        labels = ["trials", "nodes", "time"]
    else:
        labels = ["trials", "nodes", "edges", "time"]

    data_frame = pd.DataFrame.from_records(data, columns = labels)
    return data_frame


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

# Convert a list of graphs into a list.
def ___parse_graphs(file_name):
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
def ___graphs_list_to_networkx(file_name):
    fusy_graphs = ___parse_graphs(file_name)
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

def ___ratio_edges_vertices(graphs):
    """Calculates the edges to nodes ratio for each graph and plot it."""
    ratio_list = []
    for g in graphs:
        node_number = len(g.nodes())
        edge_number = len(g.edges())
        ratio = edge_number / node_number
        ratio_list.append(ratio)

    x_data = [x for x in range(len(ratio_list))]
    y_data = ratio_list
    mean = 0
    for y in y_data:
        mean += y
    mean = mean / len(graphs)
    _, ax = plt.subplots()
    # Draw bars, position them in the center of the tick mark on the x-axis
    ax.plot(x_data, y_data, 'ro')
    ax.axhline(mean, color='green', linewidth=2)
    ax.set_ylabel("Edges/vertices ratio")
    ax.set_xlabel("Graph")
    ax.set_title("Edges/vertices Ratio")
    plt.show()

def ___vertex_degrees_distributions(graphs):
    degrees_list = []
    for g in graphs:
        neighbors = []
        nodes = g.nodes()
        for n in nodes:
            degree = g.degree(n)/1000
            neighbors.append(degree)
        degrees_list.append(neighbors)

    x_data = [x for x in range(len(degrees_list))]
    y_data = degrees_list
    _, ax = plt.subplots()

    for x, y in zip(x_data, y_data):
        ax.scatter([x] * len(y), y, s=10,marker='X',linewidths=0.1) 

    ax.set_ylabel("Nodes degrees")
    ax.set_xlabel("Graph")
    ax.set_title("Distribution of Vertex Degrees")
    plt.show()   

def ___analyse_nx_graphs(name, file_graphs, file_data, sample_num, samples_size):
    graph_list = ___graphs_list_to_networkx(file_graphs)
    if name is 'planar_graph':
        for g in graph_list:
            while len(g.nodes()) < samples_size:
                g.add_node(len(g.nodes())+1)
    data = ___file_to_data_frame(file_data)
    ___test_combinatorial_class(name, data, graph_list, samples_size)

def ___sample_and_analyse_nx_graphs(name, file_data ,sample_num, samples_size):
    graph_list = create_data(name, sample_num, samples_size)

    if name is 'planar_graph':
        nx_g = [bij_connected_comps(o) for o in graph_list]
    else:
        und_der = [o.underive_all() for o in graph_list]
        nx_g = [u.to_networkx_graph() for u in und_der] 

    data = ___file_to_data_frame(file_data)
    ___test_combinatorial_class(name, data, nx_g, samples_size)


# This class compares different kinds of graphs sampled by our code
# and the ones sampled by Fusy's code.
def main():
    argparser = argparse.ArgumentParser(description='Test stuff')
    argparser.add_argument('-d', dest='loglevel', action='store_const', const=logging.DEBUG, help='Print Debug info')
    argparser.add_argument('-a', '--all', action='store_true', help='Make statistical tests for all combinatorial classes')
    argparser.add_argument('-b', '--binary_tree', action='store_true', help='Make statistical tests for binary trees')
    argparser.add_argument('-three', '--three_connectd', action='store_true', help='Make statistical tests for three connected graphs')
    argparser.add_argument('-two', '--two_connected', action='store_true', help='Make statistical tests for two connected graphs')
    argparser.add_argument('-one', '--one_connected', action='store_true', help='Make statistical tests for one connected graphs')
    argparser.add_argument('-planar', '--planar_graph', action='store_true', help='Make statistical tests for planar graphs')
    argparser.add_argument('-plot', '--plot_distribution', action='store_true', help='Plot the distribution of the different graph types')
    argparser.add_argument('-fusy', '--analyse_fusy', action='store_true', help='Analyse data produced by Fusy`s implementation')
    argparser.add_argument('-analyse', '--analyse_nx', action='store_true', help='Only analyse already sampled nx graphs.')
    argparser.add_argument('-data', '--create_data', action='store_true', help='Sample graphs.')
    argparser.add_argument('samples', type=int, help="Sample x graphs.")
    argparser.add_argument('size', type=int, help="Sample object of a certain size.")

    args = argparser.parse_args()
    logging.basicConfig(level=args.loglevel)

    sample_num = args.samples
    samples_size = args.size

    if args.create_data and args.all:      
        #create_data('planar_graph', sample_num, samples_size)
        create_data('one_connected', sample_num, samples_size)
        create_data('two_connected', sample_num, samples_size)
        create_data('three_connected', sample_num, samples_size)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         
        create_data('binary_tree', sample_num, samples_size)
    elif args.analyse_nx and args.all:
        # print(COLOR_BLUE + "                 PLANAR GRAPH TEST" + COLOR_END)
        # ___analyse_nx_graphs('planar_graph', 'nx_planar_graph_graphs', 'nx_planar_graph_stats', sample_num, samples_size)

        print(COLOR_BLUE + "                  ONE-CONNECTED TEST" + COLOR_END)
        ___analyse_nx_graphs('one_connected', 'nx_one_connected_graphs', 'nx_one_connected_stats', sample_num, samples_size)

        print(COLOR_BLUE + "                  TWO-CONNECTED TEST" + COLOR_END)
        ___analyse_nx_graphs('two_connected', 'nx_two_connected_graphs', 'nx_two_connected_stats', sample_num, samples_size)

        print(COLOR_BLUE + "              THREE-CONNECTED TEST" + COLOR_END)
        ___analyse_nx_graphs('three_connected', 'nx_three_connected_graphs', 'nx_three_connected_stats', sample_num, samples_size)

        print(COLOR_BLUE + "                  BINARY TREE TEST" + COLOR_END)
        ___analyse_nx_graphs('binary_tree', 'nx_binary_tree_graphs', 'nx_binary_tree_stats', sample_num, samples_size) 

    elif args.analyse_fusy:
        print(COLOR_BLUE + "                ANALYSE FUSYS DATA" + COLOR_END)
        if args.one_connected:
            ___analyse_fusys_data(samples_size, all=False, one=True)
        elif args.two_connected:
            ___analyse_fusys_data(samples_size, all=False, two=True)
        elif args.three_connectd:
            ___analyse_fusys_data(samples_size, all=False, three=True)
        elif args.binary_tree:
            ___analyse_fusys_data(samples_size, all=False, bin=True)
        elif args.planar_graph:
            ___analyse_fusys_data(samples_size, all=False, planar=True)
        else:
            ___analyse_fusys_data(samples_size)
    else:
        if args.planar_graph:
            print(COLOR_BLUE + "                 PLANAR GRAPH TEST" + COLOR_END)
            if args.create_data:
                ___sample_and_analyse_nx_graphs('planar_graph', 'nx_planar_graph_stats', sample_num, samples_size)
            else:
                ___analyse_nx_graphs('planar_graph', 'nx_planar_graph_graphs', 'nx_planar_graph_stats', sample_num, samples_size)
        if args.one_connected:
            print(COLOR_BLUE + "                  ONE-CONNECTED TEST" + COLOR_END)
            if args.create_data:
                ___sample_and_analyse_nx_graphs('one_connected', 'nx_one_connected_stats', sample_num, samples_size)
            else:
                ___analyse_nx_graphs('one_connected', 'nx_one_connected_graphs', 'nx_one_connected_stats', sample_num, samples_size)
        if args.two_connected:
            print(COLOR_BLUE + "                  TWO-CONNECTED TEST" + COLOR_END)
            if args.create_data:
                ___sample_and_analyse_nx_graphs('two_connected', 'nx_two_connected_stats', sample_num, samples_size)
            else:
                ___analyse_nx_graphs('two_connected', 'nx_two_connected_graphs', 'nx_two_connected_stats', sample_num, samples_size)
        if args.three_connectd:
            print(COLOR_BLUE + "              THREE-CONNECTED TEST" + COLOR_END)
            if args.create_data:
                ___sample_and_analyse_nx_graphs('three_connected', 'nx_three_connected_stats', sample_num, samples_size)
            else:
                ___analyse_nx_graphs('three_connected', 'nx_three_connected_graphs', 'nx_three_connected_stats', sample_num, samples_size)
        if args.binary_tree:
            print(COLOR_BLUE + "                  BINARY TREE TEST" + COLOR_END)
            if args.create_data:
                ___sample_and_analyse_nx_graphs('binary_tree', 'nx_binary_tree_stats', sample_num, samples_size)
            else:
                ___analyse_nx_graphs('binary_tree', 'nx_binary_tree_graphs', 'nx_binary_tree_stats', sample_num, samples_size)   

if __name__ == '__main__':
    main()


