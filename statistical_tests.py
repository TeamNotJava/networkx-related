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
from math import fabs, sqrt
import copy
import networkx as nx
import networkx.algorithms.isomorphism as iso
from test_data_creation import create_data
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge

# Define colors for output
COLOR_RED = '\033[91m'
COLOR_GREEN = '\033[92m'
COLOR_BLUE = '\033[94m'
COLOR_END = '\033[0m'


def ___stat_test_binary_trees(data, trees, size):
    print(COLOR_BLUE + "                  BINARY TREE TEST" + COLOR_END)
    # Calculate average number of trials to get the right size
    ___get_avr_num_trials(data)
    ___get_avr_time(data)
    #___calculate_number_of_possible_graphs(size, "binary_tree")
    dist, graphs = ___test_distribution(trees) 
    #___get_avr_btree_hight(graphs, size)   
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


def ___get_avr_btree_hight(data, size):
    # Average height of a btree is asymptotic to 2* sqrt(pi * n)
    avr = 2 * sqrt(2 * size)
    print("Avr. binary tree height..................{}".format(avr))

    # Check what average height our trees have
    graphs = list(data.keys())
    hights = []
    for g in graphs:
        init_half_edge = g
        if init_half_edge.opposite is not None:
            half_edge_list = init_half_edge.list_half_edges()
            for h in half_edge_list:
                if h.opposite is None:
                    init_half_edge = h
                    break
        g_hight = ___get_tree_hight(init_half_edge, 0)
        hights.append(g_hight)
    
    avr = 0
    for h in hights:
        avr += h
    avr = avr / len(hights)
    print("Avr. sampled tree height.................{}".format(avr))


def ___get_tree_hight(init_half_edge, hight):
    left = 0
    right = 0
    if init_half_edge.next.opposite is not None:
        left = ___get_tree_hight(init_half_edge.next, hight+1)
    
    if init_half_edge.prior.opposite is not None:
        right = ___get_tree_hight(init_half_edge.prior, hight+1)

    if left > right:
        hight += left
    else:
        hight += right
    return hight
    

def ___stat_test_three_connected_graphs(data, graphs, size):
    print(COLOR_BLUE + "              THREE CONNECTED TEST" + COLOR_END)
    # Calculate average number of trials to get the right size
    ___get_avr_num_trials(data)
    ___get_avr_time(data)
    #___calculate_number_of_possible_graphs(size, "binary_tree")
    dist, graphs = ___test_distribution(graphs) 
    #___get_avr_btree_hight(graphs, size)   
    return dist
    

def ___stat_test_two_connected_graphs(data, graphs):
    raise NotImplementedError

def ___stat_test_one_connected_graphs(data, graphs):
    raise NotImplementedError

def ___stat_test_planar_graphs(data, graphs):
    raise NotImplementedError

def ___test_distribution(objects):
    # Convert to netwokrx graphs
    nx_objects = [ o.to_networkx_graph() for o in objects]

    graphs = dict()
    # Count isomorphic graphs
    for g1 in nx_objects:
        graphs[g1] = 1
        for g2 in nx_objects:
            if g2 != g1 and nx.is_isomorphic(g1, g2):
                nx_objects.remove(g2)
                graphs[g1] += 1
        nx_objects.remove(g1)
    
    # If the sampler samples the object uniformly then the size
    # distribution must be uniform
    total_num = 0
    graphs_num = 0
    for g in graphs:
        graphs_num += 1
        total_num += graphs[g]

    target = float(total_num / graphs_num)
    
    print("Avr. No. graphs per size.................{}".format(target))
    print("No. non-isom. graphs.....................{}".format(graphs_num))

    # Check if there are graphs which occure significantla less/more often 
    # than the target
    wrong = 0
    for g in graphs:
        diff = fabs(graphs[g] - target)
        tolerance = target * 0.9 # x% variance is allowed
        if diff > tolerance or diff < tolerance:
            wrong += 1
        if wrong > (graphs_num/2):
            # More then halv of the graphs exceed the tolerance
            return False, graphs
    return True, graphs

def ___draw_size_distribution_diagram(data):
    raise NotImplementedError


def ___calculate_number_of_possible_graphs(size, object_class):
    number = 0
    if object_class is "binary_tree":
        raise NotImplementedError
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
        raise NotImplementedError

def ___test_for_special_graphs(data):
    raise NotImplementedError

def ___find_the_right_const_for_evals(data):
    raise NotImplementedError

def ___parse_data(file_name):
    data = []
    with open(file_name) as file:
        for l in file:
            line_list = l.split(' ')
            line_list.remove('\n')
            data.append(tuple(line_list))
    return data

def ___file_to_data_frame(file_name):
    data = ___parse_data(file_name)
    labels = []
    if file_name is "binary_tree":
        labels = ["nodes", "leaves", "trials", "time"]
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
        passed = ___stat_test_binary_trees(data, tree_list, samples_size)
    elif args.three_connectd:
        print(COLOR_BLUE + "              THREE-CONNECTED TEST" + COLOR_END)
        comb_class = "three-connected"
        graph_list = create_data("three_connected", sample_num, samples_size)
        data = ___file_to_data_frame("three_connected")
        passed = ___stat_test_three_connected_graphs(data, graph_list, samples_size)
    elif args.two_connected:
        print(COLOR_BLUE + "                  TWO-CONNECTED TEST" + COLOR_END)
        comb_class = "two-connected"
        graph_list = create_data("two_connected", sample_num, samples_size)
        data = ___file_to_data_frame("two_connected")
        passed = ___stat_test_three_connected_graphs(data, graph_list, samples_size)
    elif args.one_connected:
        print(COLOR_BLUE + "                  ONE-CONNECTED TEST" + COLOR_END)
        comb_class = "one-connected"
        graph_list = create_data("one_connected", sample_num, samples_size)
        data = ___file_to_data_frame("one_connected")
        passed = ___stat_test_three_connected_graphs(data, graph_list, samples_size)
    elif args.planar:
        print(COLOR_BLUE + "                 PLANAR GRAPH TEST" + COLOR_END)
        comb_class = "planar graph"
        graph_list = create_data("planar_graph", sample_num, samples_size)
        data = ___file_to_data_frame("planar_graph")
        passed = ___stat_test_three_connected_graphs(data, graph_list, samples_size)
    else:
        raise Exception("Wrong combinatorial class.")

    if passed:
        print(COLOR_GREEN + '{} test.........................PASSED'.format(comb_class) + COLOR_END)
    else:
        print(COLOR_RED + '{} test...........................FAILED'.format(comb_class) + COLOR_END) 


if __name__ == '__main__':
    main()


