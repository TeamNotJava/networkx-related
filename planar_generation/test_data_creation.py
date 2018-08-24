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

from timeit import default_timer as timer
import copy

from framework.generic_samplers import BoltzmannSamplerBase
from framework.decomposition_grammar import AliasSampler, DecompositionGrammar
from planar_graph_sampler.grammar.binary_tree_decomposition import binary_tree_grammar
from planar_graph_sampler.grammar.three_connected_decomposition import three_connected_graph_grammar
from planar_graph_sampler.grammar.two_connected_decomposition import two_connected_graph_grammar
from planar_graph_sampler.grammar.one_connected_decomposition import one_connected_graph_grammar
from planar_graph_sampler.grammar.planar_graph_decomposition import planar_graph_grammar
from framework.evaluation_oracle import EvaluationOracle
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals
from planar_graph_sampler.grammar.planar_graph_decomposition import bij_connected_comps


def ___sample_combinatorial_class(name, comb_class, symbolic_x, symbolic_y, size, exact=True, derived=0):
    start_sampling = timer()
    number_trials = 0

    BoltzmannSamplerBase.oracle = EvaluationOracle.get_best_oracle_for_size(size, planar_graph_evals)   

    grammar = None

    if name is "binary_tree":
        grammar = binary_tree_grammar()
    elif name is "three_connected":
        grammar = three_connected_graph_grammar()
    elif name is "two_connected":
        grammar = two_connected_graph_grammar()
    elif name is "one_connected":
        grammar = one_connected_graph_grammar()
    elif name is "planar_graph":
        grammar = planar_graph_grammar()
    else:
        raise Exception("No such graph class")

    assert(grammar is not None)

    grammar.init()
    node_num = 0

    if exact: 
        while node_num != size:
            number_trials += 1
            graph = grammar.sample_iterative(comb_class, symbolic_x, symbolic_y) 
            
            if derived == 0 and name is not "planar_graph" and name is not "one_connected":     
                node_num = graph.number_of_nodes
            else:
                node_num = graph.l_size + derived
    else:
        graph = grammar.sample_iterative(comb_class, symbolic_x, symbolic_y)
        
        if derived == 0 and name is not "planar_graph" and name is not "one_connected":
            node_num = graph.number_of_nodes
        else:
            node_num = graph.l_size + derived

    if derived == 0 and name is not "planar_graph" and name is not "one_connected":
        edge_num = graph.number_of_edges
    else:
        edge_num = graph.u_size

    end_sampling = timer()
    time_needed = end_sampling - start_sampling
    data = (node_num, edge_num, number_trials, time_needed)

    ___save_graph_in_file(graph, name)
    
    return data, graph

def ___save_graph_in_file(graph, name):
    n = 'nx_' + name + '_graphs'
    file = open(n, 'a')
    file.write('\n')
    file.write('P')
    file.write('\n')

    if name is 'planar_graph':
        nx_graph =  bij_connected_comps(graph)   
    else:
        und_der = graph.underive_all()
        nx_graph = und_der.to_networkx_graph()

    for e in nx_graph.edges():
        file.write(str(e[0]))
        file.write(' ')
        file.write(str(e[1]))
        file.write('\n')
    file.close()
    
def ___write_to_file(name, data_list):
    file_name = 'nx_' + name + '_stats'
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
    der = 0

    if comb_class is "binary_tree":
        sample = 'K_dx'
        symbolic_x = 'x*G_1_dx(x,y)'
        symbolic_y = 'D(x*G_1_dx(x,y),y)'
        der = 1
    elif comb_class is "three_connected":
        sample = 'G_3_arrow_dx'
        symbolic_x = 'x*G_1_dx(x,y)'
        symbolic_y = 'D(x*G_1_dx(x,y),y)'
        der = 1
    elif comb_class is "two_connected":
        sample = 'G_2_dx_dx'
        symbolic_x = 'x*G_1_dx(x,y)'
        symbolic_y = 'y'
        der = 2
    elif comb_class is "one_connected":
        sample = 'G_1_dx_dx'
        symbolic_x = 'x'
        symbolic_y = 'y'
        der = 2
    elif comb_class is "planar_graph":
        sample = 'G_dx_dx'
        symbolic_x = 'x'
        symbolic_y = 'y'
        der = 2
    else:
        raise Exception("No such combinatorial class!")

    for _ in range(sample_num):
        d, g = ___sample_combinatorial_class(comb_class, sample, symbolic_x, symbolic_y, samples_size, derived=der)
        data.append(d)
        obj_list.append(g)

    ___write_to_file(comb_class, data)

    return obj_list
