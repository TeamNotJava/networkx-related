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
from planar_graph_sampler.grammar.three_connected_decomposition import three_connected_graph_grammar
from planar_graph_sampler.evaluations_planar_graph import *
from planar_graph_sampler.grammar.two_connected_decomposition import two_connected_graph_grammar


def ___sample_binary_tree(size):
    start_sampling = timer()
    number_trials = 0
    # if size <= 100:
    #     BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)     
    # else:
    #     BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n1000)
    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n1000)

    grammar = binary_tree_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    node_num = 0

    if size != 0: 
        while node_num != size:
            number_trials += 1
            try:
                tree = grammar.sample('K', symbolic_x, symbolic_y)
                node_num = tree.black_nodes_count + tree.white_nodes_count
            except Exception:
                number_trials += 1     
    else:
        tree = grammar.sample('K', symbolic_x, symbolic_y)
        node_num = tree.black_nodes_count + tree.white_nodes_count

    end_sampling = timer()
    time_needed = end_sampling - start_sampling

    data = (node_num, tree.leaves_count, number_trials, time_needed)
    
    return data, tree

def ___sample_three_connected(size):
    # Sample three connected edge rooted graphs
    start_sampling = timer()
    number_trials = 0
    if size <= 100:
        BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    else:
        BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n1000)

    grammar = three_connected_graph_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    node_num = 0

    if size != 0:
        while node_num != size:
            number_trials += 1
            try:
                three_connected = grammar.sample('M_3_arrow', symbolic_x, symbolic_y)
                node_num = three_connected.l_size
            except Exception:
                number_trials += 1
    else:
        three_connected = grammar.sample('M_3_arrow', symbolic_x, symbolic_y)
        node_num = three_connected.l_size
    
    end_sampling = timer()
    time_needed = end_sampling - start_sampling

    data = (node_num, number_trials, time_needed)
    return data, three_connected
    

def ___sample_two_connected(size):
    start_sampling = timer()
    number_trials = 0
    if size <= 100:
        BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    else:
        BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n1000)

    grammar = two_connected_graph_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'y'
    node_num = 0

    if size != 0: 
        while node_num != size:
            number_trials += 1
            try:
                two_connectd = grammar.sample('G_2_arrow', symbolic_x, symbolic_y)
                node_num = two_connectd.number_of_nodes
            except Exception:
                number_trials += 1
    else:
        two_connectd = grammar.sample('G_2_arrow', symbolic_x, symbolic_y)
        node_num = two_connectd.number_of_nodes

    edge_num = two_connectd.number_of_edges

    end_sampling = timer()
    time_needed = end_sampling - start_sampling

    data = (node_num, edge_num, number_trials, time_needed)
    
    return data, two_connectd

def ___sample_one_connected(size):  
    raise NotImplementedError

def ___sample_planar_graphs(size):
    raise NotImplementedError

def ___sample_combinatorial_class(comb_class, symbolic_x, symbolic_y, size):
    start_sampling = timer()
    number_trials = 0
    if size == 100:
        BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    else:
        BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n1000)

    grammar = two_connected_graph_grammar()
    grammar.init()
    node_num = 0

    if size != 0: 
        while node_num != size:
            number_trials += 1
            graph = grammar.sample(comb_class, symbolic_x, symbolic_y)
            node_num = graph.number_of_nodes
    else:
        graph = grammar.sample(comb_class, symbolic_x, symbolic_y)
        node_num = graph.number_of_nodes

    edge_num = graph.number_of_edges

    end_sampling = timer()
    time_needed = end_sampling - start_sampling

    data = (node_num, edge_num, number_trials, time_needed)
    
    return data, graph


def ___write_to_file(file_name, data_list):
    file = open(file_name,'w')
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
        for i in repeat(None, sample_num):
            d, g = ___sample_binary_tree(samples_size)
            data.append(d)
            obj_list.append(g)
    elif comb_class is "three_connected":
        sample = 'M_3_arrow'
        symbolic_x = 'x*G_1_dx(x,y)'
        symbolic_y = 'D(x*G_1_dx(x,y),y)'
    elif comb_class is "two_connected":
        sample = 'M_2_arrow'
        symbolic_x = 'x*G_1_dx(x,y)'
        symbolic_y = 'y'
    elif comb_class is "one_connected":
        sample = 'G_1'
        symbolic_x = 'x'
        symbolic_y = 'y'
    elif comb_class is "planar_graph":
        sample = 'G'
        symbolic_x = 'x'
        symbolic_y = 'y'
    else:
        raise Exception("No such combinatorial class!")

    if comb_class is not "binary_tree":
        for i in repeat(None, sample_num):
            d, g = ___sample_combinatorial_class(sample, symbolic_x, symbolic_y, samples_size)
            data.append(d)
            obj_list.append(g)

    ___write_to_file(comb_class, data)

    return obj_list



