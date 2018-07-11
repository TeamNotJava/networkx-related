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

from itertools import repeat
from timeit import default_timer as timer
import copy

from framework.generic_samplers import *
from framework.decomposition_grammar import AliasSampler, DecompositionGrammar
from planar_graph_sampler.grammar.binary_tree_decomposition import binary_tree_grammar
from planar_graph_sampler.grammar.two_connected_decomposition import two_connected_graph_grammar
from planar_graph_sampler.evaluations_planar_graph import *
from planar_graph_sampler.grammar.two_connected_decomposition import two_connected_graph_grammar
from planar_graph_sampler.bijections.block_decomposition import BlockDecomposition


def ___sample_binary_tree(size):
    start_sampling = timer()
    number_trials = 0
    if size < 500:
        BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)     
    else:
        BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n1000)

    grammar = binary_tree_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    node_num = 0

    if size != 0: 
        while node_num != size:
            number_trials += 1
            tree = grammar.sample('R_b', symbolic_x, symbolic_y)
            node_num = tree.black_nodes_count + tree.white_nodes_count
    else:
        tree = grammar.sample('R_b', symbolic_x, symbolic_y)
        node_num = tree.black_nodes_count + tree.white_nodes_count

    end_sampling = timer()
    time_needed = end_sampling - start_sampling

    data = (node_num, tree.leaves_count, number_trials, time_needed)
    
    return data, tree

def ___get_btree_height(btree):
    pass
    
def ___sample_three_connected(size):
    raise NotImplementedError


def ___sample_two_connected(size):
    start_sampling = timer()
    number_trials = 0
    if size < 500:
        BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)     
    else:
        BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n1000)

    grammar = two_connected_graph_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'y'
    node_num = 0

    if size != 0: 
        while node_num != size:
            number_trials += 1
            two_connectd = grammar.sample('D', symbolic_x, symbolic_y)
            node_num = len(two_connectd.vertices_list)
    else:
        two_connectd = grammar.sample('D', symbolic_x, symbolic_y)
        node_num = len(two_connectd.vertices_list)

    edge_num = len(two_connectd.edges_list)

    end_sampling = timer()
    time_needed = end_sampling - start_sampling

    data_list = [node_num, edge_num, number_trials, time_needed]
    
    return data_list

def ___sample_one_connected(size):  
    raise NotImplementedError

def ___sample_planar_graphs(size):
    raise NotImplementedError

def ___write_to_file(file_name, data_list):
    file = open(file_name,'w')
    #for data in data_list:
    #    file.write(str(data))
    for data in data_list:
        for d in data:
            file.write(str(d))
            file.write(" ")
        file.write('\n')
    file.close()

def create_data(comb_class, sample_num, samples_size):
    data = []
    obj_list = []

    if comb_class is "binary_tree":
        for i in repeat(None,sample_num):
            d, t = ___sample_binary_tree(samples_size)
            data.append(d)
            obj_list.append(t)
        file_name = "binary_tree"

    elif comb_class is "three_connected":
        pass
    elif comb_class is "two_connected":
        pass
    elif comb_class is "one_connected":
        pass    
    elif comb_class is "planar_graph":
        pass
    else:
        raise Exception("No such combinatorial class!")

    ___write_to_file(file_name, data)

    return obj_list


    


