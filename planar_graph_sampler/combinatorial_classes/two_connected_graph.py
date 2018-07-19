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

import random as rnd

from planar_graph_sampler.combinatorial_classes.half_edge_graph import HalfEdgeGraph


class TwoConnectedPlanarGraph(HalfEdgeGraph):

    def __init__(self, half_edge):
        super().__init__(half_edge)

    def is_consistent(self):
        super_ok = super().is_consistent()
        two_connected = self.is_connected(2)
        planar = self.is_planar()
        return all([super_ok, True, planar])


class EdgeRootedTwoConnectedPlanarGraph(TwoConnectedPlanarGraph):

    def __init__(self, root_half_edge):
        super().__init__(root_half_edge)

    def get_u_size(self):
        return super().get_u_size() - 1

    def get_l_size(self):
        return super().get_l_size() - 2


class UDerivedTwoConnectedPlanarGraph(TwoConnectedPlanarGraph):

    def __init__(self, half_edge):
        super().__init__(half_edge)

    def get_u_size(self):
        return super().get_u_size() - 1


class ULDerivedTwoConnectedPlanarGraph(TwoConnectedPlanarGraph):

    def __init__(self, half_edge):
        super().__init__(half_edge)

    def get_u_size(self):
        return super().get_u_size() - 1

    def get_l_size(self):
        return super().get_l_size() - 1


class LDerivedTwoConnectedPlanarGraph(TwoConnectedPlanarGraph):

    def __init__(self, half_edge):
        super().__init__(half_edge)

    def get_l_size(self):
        return super().get_l_size() - 1

    def replace_l_atoms(self, sampler, x, y):
        nodes = self.half_edge.get_node_list()
        # Select a random node and save a half-edge incident to it.
        random_node = rnd.choice(list(nodes.keys()))
        self.half_edge = nodes[random_node][0]
        # Remove the random node.
        nodes.pop(random_node)
        # Sample a graph and merge it with all remaining nodes.
        for node in nodes:
            # Sampler is for Z_L * G_1_dx
            plug_in = sampler.sample(x, y).second.get_half_edge()
            # Get any half-edge incident to the current node.
            he = nodes[node][0]
            he.insert_all(plug_in)


class BiLDerivedTwoConnectedPlanarGraph(TwoConnectedPlanarGraph):
    def __init__(self, half_edge):
        super().__init__(half_edge)
        self.random_node_2 = None

    def get_l_size(self):
        return super().get_l_size() - 2

    def replace_l_atoms(self, sampler, x, y):
        nodes = self.half_edge.get_node_list()
        # Select two random nodes and save a half-edge incident to them.
        random_node_1 = rnd.choice(list(nodes.keys()))
        self.half_edge = nodes[random_node_1][0]
        # Remove the random node.
        nodes.pop(random_node_1)
        random_node_2 = rnd.choice(list(nodes.keys()))
        self.random_node_2 = nodes[random_node_2][0]
        # Remove the random node.
        nodes.pop(random_node_2)
        assert random_node_1 is not random_node_2
        # Sample a graph and merge it with all remaining nodes.
        for node in nodes:
            # Sampler is for Z_L * G_1_dx
            plug_in = sampler.sample(x, y).second.get_half_edge()
            # Get any half-edge incident to the current node.
            he = nodes[node][0]
            he.insert_all(plug_in)
