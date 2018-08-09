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

from planar_graph_sampler.grammar.planar_graph_decomposition import  planar_graph_grammar, bij_connected_comps
from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import BoltzmannSamplerBase
from framework.generic_classes import SetClass
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals
import networkx as nx

class PlanarGraphGenerator:

    def generate_planar_graph(self, node_number, variance):
        """This function generates a random planar graph using Boltzmann
        samplers with fixed number of nodes with the possibility to
        define a margin in which the number of nodes of the sampled
        planar graph can vary.

        Parameters
        ----------
        node_number: int
            the desired number of nodes the graph should have
        variance: float
            the variance for the number of nodes in percent

        Returns
        -------
        graph: NetworkX
            a random networkx planar graph

        Notes
        -----
        This algorithm makes use of the fact that every planar graph can
        be decomposed into a set of connected planar graphs which in
        turn can be obtained by using several bijection and rejection
        steps starting with bicolored binary trees. For every step one
        creates a Boltzmann sampler that produces a certain random
        object with uniform probability. Combining all the samplers,
        one obtain a Boltzmann sampler for planar graphs [1].

        References
        ----------
        .. [1] Eric Fusy:
            Uniform random sampling of planar graphs in linear time
        """
        # If the user specifies a variance of 100, then there are no
        #  lower/upper bounds
        if variance != 100:
            lower_bound = node_number - (node_number * variance/100)
            upper_bound = node_number + (node_number * variance/100)

        BoltzmannSamplerBase.oracle = EvaluationOracle.get_best_oracle_for_size(node_number, planar_graph_evals)     


        grammar = planar_graph_grammar()
        grammar.init()
        grammar.precompute_evals('G_dx_dx', 'x', 'y')
        curr_node_number = 0
        
        planar_graph = grammar.sample_iterative('G_dx_dx', 'x', 'y')
        
        if variance != 100:
            curr_node_number = planar_graph.l_size
            while(curr_node_number < lower_bound or curr_node_number > upper_bound):
                planar_graph = grammar.sample_iterative('G_dx_dx', 'x', 'y')
                curr_node_number = planar_graph.l_size

        # Transform to networkx graph
        gnx = bij_connected_comps(planar_graph)
        return gnx

    def generate_planar_graph_fixed_nodes_edges(self, node_num, edge_num, node_var, edge_var):
        """This function samples random planar graphs using Boltzmann
        samplers with fixed number of nodes and edges with the
        possibility of choosing a variance for number of nodes and edges.
        """
        if node_var != 100:
            lower_nodes = node_num - (node_num * node_var)
            upper_nodes = node_num + (node_num * node_var)
        if edge_var != 100:
            lower_edges = edge_num - (edge_num * edge_var)
            upper_edges = edge_num + (edge_num * edge_var)

        BoltzmannSamplerBase.oracle = EvaluationOracle.get_best_oracle_for_size(node_number, planar_graph_evals)  

        grammar = planar_graph_grammar()
        grammar.init()
        grammar.precompute_evals('G_dx_dx', 'x', 'y')
        curr_node_number = 0
        curr_edge_number = 0

        if node_var != 100 and edge_var != 100:
            while(curr_node_number < lower_nodes or curr_node_number > upper_nodes
                    or curr_edge_number < lower_edges or curr_edge_number > upper_edges):
                planar_graph = grammar.sample_iterative('G_dx_dx', 'x', 'y')
                curr_node_number = planar_graph.l_size
                curr_edge_number = planar_graph.u_size
        elif node_num != 100 and edge_var == 100:
            while(curr_node_number < lower_nodes or curr_node_number > upper_nodes):
                planar_graph = grammar.sample_iterative('G_dx_dx', 'x', 'y')
                curr_node_number = planar_graph.l_size
        elif node_num == 100 and edge_var != 100:
            while(curr_node_number < lower_nodes or curr_node_number > upper_nodes):
                planar_graph = grammar.sample_iterative('G_dx_dx', 'x', 'y')
                curr_node_number = planar_graph.l_size
        else:
            planar_graph = grammar.sample_iterative('G_dx_dx', 'x', 'y')

        # Transform to networkx graph
        gnx = bij_connected_comps(planar_graph)
        return gnx

    def generate_planar_graph_with_min_number_nodes(self, node_number):
        """This function samples random planar graphs using Boltzmann samplers
        with at least the given number of desired nodes.
        """

        BoltzmannSamplerBase.oracle = EvaluationOracle.get_best_oracle_for_size(node_number, planar_graph_evals)  

        grammar = planar_graph_grammar()
        grammar.init()
        grammar.precompute_evals('G_dx_dx', 'x', 'y')
        curr_node_number = 0

        while(curr_node_number < node_number):
            planar_graph = grammar.sample_iterative('G_dx_dx', 'x', 'y')
            curr_node_number = planar_graph.l_size

        # Transform to networkx graph
        gnx = bij_connected_comps(planar_graph)
        return gnx
