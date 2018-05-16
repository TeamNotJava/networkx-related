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

from .utils import bern_choice
from .binary_tree import BinaryTreeSampler
from planarity_generation.closure import Closure

class ThreeConnectedGraphSampler:
    """Sampler Class for 3-Connected Planar Graphs.
    Uses the Binary Tree Sampler for sampling the 3-Connected Planar Graph.
    """

    binary_tree_sampler = None

    def set_probabilities(self, probabilities):
        """Sets the used probabilities
        """
        self.probabilities = probabilities

    def set_random(self, random_function):
        """Sets the used random function
        """
        self.random_function = random_function

    def __init__(self):
        self.binary_tree_sampler = BinaryTreeSampler()
        self.set_probabilities({
            'ch_K_in_dyK': [0.1023148450168439782698851645651737890839, 0.8976851549831560217301148354348262109160],
            'ch_dxK_in_dxyK': [0.01056720808167383324019751492093784146016, 0.9894327919183261667598024850790621585398],
            'ch_b_or_dxb': [0.04311363388351982963897237807044101069163, 0.9568863661164801703610276219295589893083],
            'ch_3b_or_dyb': [0.05196496216386519137788597254497784663637, 0.9480350378361348086221140274550221533636]
        })

    def three_connected_graph(self, n, epsilon=None):
        """Sample a 3-Connected Planar Graph with size n.
        If epsilon is not None the size can be between n(1-epsilon) and n(1+epsilon)
        """
        return self.___three_connected_graph()

    # Corresponds to 
    def ___three_connected_graph(self):
        pass


    def draw_k(self):
        while True:
            random = self.random_function()
            max_size = int(4 / random)
            #TODO: We still don't have the check if the binary tree exceeds the maximum number of nodes
            #TODO  in BinaryTreeSampler, so it will return the first generated tree
            binary_tree = self.binary_tree_sampler.binary_tree() # we should include the max size here!!
            if binary_tree is not None:
                half_edge = Closure().closure(binary_tree)
                if half_edge is not None:
                    return TreeConnectedGraph(half_edge)


    def draw_dxK(self):
        while True:
            binary_tree = self.binary_tree_sampler.binary_tree() # no need of N
            number_of_black_nodes = 0 # Todo: they are not provided in the interface
            number_of_white_nodes = 0 # Todo: they are not provided in the interface
            reject = (3.0 * (number_of_black_nodes + 1) / (2.0 * (number_of_black_nodes + number_of_white_nodes + 2)))
            if reject >= self.random_function():
                half_edge = Closure().closure(binary_tree)
                if half_edge is not None:
                    return TreeConnectedGraph(half_edge)


    def draw_dyK(self):
        if bern_choice(self.probabilities['ch_K_in_dyK'], self.random_function) is 0:
            return self.draw_k()
        else:
            while True:
                binary_tree = self.binary_tree_sampler.binary_tree() # no need of N
                half_edge = Closure().closure(binary_tree)
                if half_edge is not None:
                    return TreeConnectedGraph(half_edge)


    def draw_dxyK(self):
        if bern_choice(self.probabilities['ch_dxK_in_dxyK'], self.random_function) is 0:
            return self.draw_dxK()
        else:
            while True:
                if bern_choice(self.probabilities['ch_b_or_dxb'], self.random_function) is 0:
                    binary_tree = self.binary_tree_sampler.binary_tree() #  n is not necessary
                else:
                    binary_tree = self.binary_tree_sampler.black_pointed_binary_tree()
                half_edge = Closure().closure(binary_tree)
                if half_edge is not None:
                    return TreeConnectedGraph(half_edge)


    def draw_dxxK(self):
        while True:
            black_rooted_binary_tree = self.binary_tree_sampler.black_pointed_binary_tree()
            number_of_black_nodes = 0  # Todo: they are not provided in the interface
            number_of_white_nodes = 0  # Todo: they are not provided in the interface
            reject = (3.0 * (number_of_black_nodes + 1) / (2.0 * (number_of_black_nodes + number_of_white_nodes + 2)))
            if reject >= self.random_function():
                half_edge = Closure().closure(black_rooted_binary_tree)
                if half_edge is not None:
                    return TreeConnectedGraph(half_edge)


    def draw_dyyK(self):
        while True:
            if bern_choice(self.probabilities['ch_3b_or_dyb'], self.random_function) is 0:
                binary_tree = self.binary_tree_sampler.binary_tree() # n is not necessary
            else:
                binary_tree = self.binary_tree_sampler.white_pointed_binary_tree()
            half_edge = Closure().closure(binary_tree)
            if half_edge is not None:
                return TreeConnectedGraph(half_edge)



class TreeConnectedGraph:
    ''' A Tree connected graph representation. '''

    # Root half edge
    root_half_edge = None

    #Both edges_list and vertices list contain objects from HalfEdge class.
    # List of vertices
    vertices_list = list()

    # List of edges
    edges_list = list()

    def __init__(self, root_half_edge):
        self.make_copy(root_half_edge)
        self.root_half_edge = root_half_edge

    def make_copy(self, root_half_edge):
        pass