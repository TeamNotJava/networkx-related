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

from framework.generic_classes import CombinatorialClass


class VertexRootedTwoConnectedPlanarGraph(CombinatorialClass):

    def __init__(self, vertices_list, edges_list, root_vertex):
        self.vertices_list = vertices_list
        self.edges_list = edges_list
        # A list of half-edges belonging to the root-vertex
        self.root_vertex = root_vertex
    
    def get_u_size(self):
        return len(self.edges_list)

    def get_l_size(self):
        return len(self.vertices_list) - 1

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

    # we don't need this 
    def replace_l_atoms(self, sampler, x, y):
        raise NotImplementedError

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


class UnrootedTwoConnectedPlanarGraph(CombinatorialClass):

    def __init__(self, vertices_list, edges_list, root_vertex):
        self.vertices_list = vertices_list
        self.edges_list = edges_list
        # A list of half-edges belonging to the root-vertex
        self.root_vertex = root_vertex
    
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

    # we don't need this 
    def replace_l_atoms(self, sampler, x, y):
        raise NotImplementedError

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
