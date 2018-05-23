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
from .closure import Closure

class ThreeConnectedGraphSampler:
    """Sampler Class for 3-Connected Planar Graphs.
    Uses the Binary Tree Sampler for sampling the 3-Connected Planar Graph.
    """

    def set_probabilities(self, probabilities):
        """Sets the used probabilities
        """
        self.probabilities = probabilities

    def set_random(self, random_function):
        """Sets the used random function
        """
        self.random_function = random_function

    def __init__(self):
        self.binary_tree_function = BinaryTreeSampler().binary_tree
        self.binary_tree_sampler = BinaryTreeSampler().binary_tree_sampler
        self.black_pointed_binary_tree_sampler = BinaryTreeSampler().black_pointed_binary_tree_sampler
        self.dy_binary_tree_sampler = BinaryTreeSampler().dy_binary_tree_sampler

        self.closure_function = Closure().closure

        self.set_probabilities({
            'ch_K_in_dyK': [0.1023148450168439782698851645651737890839, 0.8976851549831560217301148354348262109160],
            'ch_dxK_in_dxyK': [0.01056720808167383324019751492093784146016, 0.9894327919183261667598024850790621585398],
            'ch_b_or_dxb': [0.04311363388351982963897237807044101069163, 0.9568863661164801703610276219295589893083],
            'ch_3b_or_dyb': [0.05196496216386519137788597254497784663637, 0.9480350378361348086221140274550221533636]
        })

    def three_connected_graph(self):
        """Sample a 3-Connected Planar Graph."""
        return self.___three_connected_graph()

    # Corresponds to 
    def ___three_connected_graph(self):
        return self.draw_k()

    def draw_k(self):
        while True:
            random = self.random_function()
            #TODO check this with max size again!! WHY 4??
            max_size = int(4 / random)
            binary_tree = self.binary_tree_function(max_size)
            if binary_tree is not None:
                half_edge = self.closure_function(binary_tree)
                if half_edge is not None:
                    return TreeConnectedGraph(half_edge)

    def draw_dxK(self):
        while True:
            binary_tree = self.binary_tree_sampler() # no need of N
            number_of_black_nodes = binary_tree.attr['num_black']
            number_of_white_nodes = binary_tree.attr['num_white']
            reject = (3.0 * (number_of_black_nodes + 1) / (2.0 * (number_of_black_nodes + number_of_white_nodes + 2)))
            if reject >= self.random_function():
                half_edge = self.closure_function(binary_tree)
                if half_edge is not None:
                    return TreeConnectedGraph(half_edge)

    def draw_dyK(self):
        if bern_choice(self.probabilities['ch_K_in_dyK'], self.random_function) is 0:
            return self.draw_k()
        else:
            while True:
                binary_tree = self.binary_tree_sampler()
                half_edge = self.closure_function(binary_tree)
                if half_edge is not None:
                    return TreeConnectedGraph(half_edge)

    def draw_dxyK(self):
        if bern_choice(self.probabilities['ch_dxK_in_dxyK'], self.random_function) is 0:
            return self.draw_dxK()
        else:
            while True:
                if bern_choice(self.probabilities['ch_b_or_dxb'], self.random_function) is 0:
                    binary_tree = self.binary_tree_sampler()
                else:
                    binary_tree = self.black_pointed_binary_tree_sampler()
                half_edge = self.closure_function(binary_tree)
                if half_edge is not None:
                    return TreeConnectedGraph(half_edge)

    def draw_dxxK(self):
        while True:
            black_rooted_binary_tree = self.black_pointed_binary_tree_sampler()
            number_of_black_nodes = black_rooted_binary_tree.attr['num_black']
            number_of_white_nodes = black_rooted_binary_tree.attr['num_white']
            reject = (3.0 * (number_of_black_nodes + 1) / (2.0 * (number_of_black_nodes + number_of_white_nodes + 2)))
            if reject >= self.random_function():
                half_edge = self.closure_function(black_rooted_binary_tree)
                if half_edge is not None:
                    return TreeConnectedGraph(half_edge)

    def draw_dyyK(self):
        while True:
            if bern_choice(self.probabilities['ch_3b_or_dyb'], self.random_function) is 0:
                binary_tree = self.binary_tree_sampler()
            else:
                binary_tree = self.dy_binary_tree_sampler()
            half_edge = self.closure_function(binary_tree)
            if half_edge is not None:
                return TreeConnectedGraph(half_edge)


class TreeConnectedGraph:
    ''' A Tree connected graph representation. '''

    # Root half edge.
    # It, together with its opposite one are not contained in the vertices list.
    root_half_edge = None

    #Both edges_list and vertices list contain objects from HalfEdge class.
    # List of vertices in the 3 connected graph
    vertices_list = list()

    # List of edges in the 3 connected graph
    edges_list = list()

    def __init__(self, root_half_edge):
        self.root_half_edge = root_half_edge
        self.__dfs_three_connected_graph_components_extraction(root_half_edge, root_half_edge, set())


    # Given the 3-map closure, this function extract the vertices and the edges from it.
    # The root half edge and its opposite one are not part from the vertices set.
    # The opposite property from the half edges in the edges_list gives the vertex in the 3 map for connection.
    def __dfs_three_connected_graph_components_extraction(self, first_half_edge, root_half_edge, visited_half_edges):
        # Check if the half edge has been already processed
        if first_half_edge.index in visited_half_edges:
            return

        # Mark the first half edge and the ones with which it shares a vertex to visited.
        visited_half_edges.update(first_half_edge.index)
        walker_half_edge = first_half_edge.next
        while walker_half_edge != first_half_edge:
            visited_half_edges.update(first_half_edge.index)
            walker_half_edge = walker_half_edge.next

        # Check if the first half edge is different from the root and root.opposite. If this is true,
        # than the first half edge is added to a vertices list.
        walker_half_edge = first_half_edge
        if walker_half_edge != root_half_edge and walker_half_edge.opposite != root_half_edge:
            self.vertices_list.append(walker_half_edge)

        # Insert half edges to the edges list.
        walker_half_edge = walker_half_edge.next
        while walker_half_edge != first_half_edge:
            # The condition that one half edge should fullfill for inserting.
            if walker_half_edge != root_half_edge and walker_half_edge.opposite.index not in visited_half_edges:
                self.edges_list.append(walker_half_edge)
            walker_half_edge = walker_half_edge.next

        # Call the function recursively for the opposite half edges.
        walker_half_edge = walker_half_edge.next
        while walker_half_edge != first_half_edge:
            self.__dfs_three_connected_graph_components_extraction(walker_half_edge.opposite, root_half_edge, visited_half_edges)
            walker_half_edge = walker_half_edge.next