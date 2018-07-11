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
from math import fabs
import networkx as nx
import networkx.algorithms.isomorphism as iso
from test_data_creation import create_data
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge

# Define colors for output
COLOR_RED = '\033[91m'
COLOR_GREEN = '\033[92m'
COLOR_BLUE = '\033[94m'
COLOR_END = '\033[0m'


def stat_test_binary_trees(data, trees, size):
    print(COLOR_BLUE + "                   BINARY TREE TEST" + COLOR_END)
    # Calculate average number of trials to get the right size
    ___get_avr_num_trials(data)
    ___get_avr_time(data)
    ___calculate_number_of_possible_graphs(size, "binary_tree")
    dist = ___test_distribution(trees)    
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


def ___get_avr_btree_hight(data):
    # Average height of a btree is asymptotic to 2* sqrt(pi * n)
    raise NotImplementedError

def ___stat_test_three_connected_graphs(data, graphs):
    raise NotImplementedError

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
            return False
    
    return True

def ___draw_size_distribution_diagram(data):
    raise NotImplementedError

    

def ___calculate_number_of_possible_graphs(size, object_class):

    if object_class is "binary_tree":
        # Calculate the Catalan number for size
        catalan = 1.0
        for i in range(2, size+1):
            catalan = catalan * (size + i)/i
        print("Target No. non-isom. graphs..............{}".format(catalan))
    else:
        raise NotImplementedError



def ___test_for_special_graphs(data):
    raise NotImplementedError

def ___avr_num_trials_hitting_the_size(data):
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
        raise NotImplementedError

    data_frame = pd.DataFrame.from_records(data, columns = labels)
    return data_frame

def main():
    argparser = argparse.ArgumentParser(description='Test stuff')
    argparser.add_argument('-d', dest='loglevel', action='store_const', const=logging.DEBUG, help='Print Debug info')
    argparser.add_argument('-b', '--binary-tree', action='store_true', help='Make statistical tests for binary trees')
    argparser.add_argument('-three', '--three_connectd', action='store_true', help='Make statistical tests for three connected graphs')
    argparser.add_argument('-two', '--two_connected', action='store_true', help='Make statistical tests for two connected graphs')
    argparser.add_argument('-one', '--one_connected', action='store_true', help='Make statistical tests for one connected graphs')
    argparser.add_argument('samples', type=int, help="Sample x number of time.")
    argparser.add_argument('size', type=int, help="Sample object of a certain size.")

    args = argparser.parse_args()
    logging.basicConfig(level=args.loglevel)

    sample_num = args.samples
    samples_size = args.size

    if args.binary_tree:
        tree_list = create_data("binary_tree", sample_num, samples_size)
        data = ___file_to_data_frame("binary_tree")
        passed = stat_test_binary_trees(data, tree_list, samples_size)
        if passed:
            print(COLOR_GREEN + 'binary-tree test.....................passed' + COLOR_END)
        else:
            print(COLOR_RED + 'binary-tree test.....................failed' + COLOR_END)

    elif args.three_connectd:
        raise NotImplementedError
    elif args.two_connected:
        raise NotImplementedError
    elif args.one_connected:
        raise NotImplementedError
    else:
        raise Exception("Wrong combinatorial class.")


if __name__ == '__main__':
    main()


