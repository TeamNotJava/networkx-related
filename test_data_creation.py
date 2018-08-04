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


def ___sample_combinatorial_class(comb_class, symbolic_x, symbolic_y, size, exact=True):
    start_sampling = timer()
    number_trials = 0

    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)

    grammar = two_connected_graph_grammar()
    grammar.init()
    node_num = 0

    if exact: 
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
        sample = 'K'
        symbolic_x = 'x*G_1_dx(x,y)'
        symbolic_y = 'D(x*G_1_dx(x,y),y)'
    elif comb_class is "three_connected":
        sample = 'G_3_arrow'
        symbolic_x = 'x*G_1_dx(x,y)'
        symbolic_y = 'D(x*G_1_dx(x,y),y)'
    elif comb_class is "two_connected":
        sample = 'G_2_arrow'
        symbolic_x = 'x*G_1_dx(x,y)'
        symbolic_y = 'y'
    elif comb_class is "one_connected":
        sample = 'G_1_dx'
        symbolic_x = 'x'
        symbolic_y = 'y'
    elif comb_class is "planar_graph":
        sample = 'G'
        symbolic_x = 'x'
        symbolic_y = 'y'
    else:
        raise Exception("No such combinatorial class!")

    #if comb_class is not "binary_tree":
    for i in repeat(None, sample_num):
        d, g = ___sample_combinatorial_class(sample, symbolic_x, symbolic_y, samples_size)
        data.append(d)
        obj_list.append(g)

    ___write_to_file(comb_class, data)

    return obj_list