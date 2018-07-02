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

from .generic_classes import CombinatorialClass
from ..utils import nth 
import random as rn
from ..bijections.block_decomposition import BlockDecomposition



class EdgeRootedTwoConnectedPlanarGraph(CombinatorialClass):

    def __init__(self, vertices_list, edges_list, root_half_edge):
        self.vertices_list = vertices_list
        self.edges_list = edges_list
        self.root_half_edge = root_half_edge
    
    def get_u_size(self):
        return len(self.edges_list)

    def get_l_size(self):
        return len(self.vertices_list)

    def u_atoms(self):
        raise NotImplementedError

    def l_atoms(self):
        raise NotImplementedError

    def random_u_atom(self):
        raise NotImplementedError

    def random_l_atom(self):
        raise NotImplementedError

    # we don't need this.
    def replace_u_atoms(self, sampler, x, y):
        raise NotImplementedError

    # we need this as we replace every unmarked node (l-atom) with a l-der one-connected graph
    def replace_l_atoms(self, sampler, x, y):
        nodes_for_subs = self.vertices_list
        # Switch to diconary representation of the nodes
        nodes_for_subs = self.vertices_list[0].get_nodes_dictonary()

        node_by_one_connected_subs = BlockDecomposition()

        for node in nodes_for_subs:
            node_half_edges = nodes_for_subs[node]
            # Sample only for unmakred nodes
            if not node_half_edges[0].marked_vertex:
                # Sample a L-derived one-connected graph at the unmarked node
                l_der_one_connected = sampler.sample(x,y)
                node_by_one_connected_subs.replace_node_with_l_der_one_connected(node_half_edges, l_der_one_connected)
        # Dummy
        return self

    # this is an ugly method to avoid using isinstance or similar
    def is_l_atom(self):
        raise NotImplementedError

    # this is an ugly method to avoid using isinstance or similar
    def is_u_atom(self):
        raise NotImplementedError

    def __str__(self):
        repr = 'Root Edge : %s \n' % self.root_half_edge.__repr__()
        repr += 'Vertices : %s' % self.vertices_list.__repr__()
        repr += 'Edges : %s' % self.edges_list.__repr__()
        return repr
