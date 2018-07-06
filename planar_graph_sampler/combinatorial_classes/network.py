import random as rn

from framework.generic_classes import CombinatorialClass
from framework.utils import nth


class NetworkClass(CombinatorialClass):
    """

    """

    def __init__(self, vertices_list, edges_list, root_half_edge):
        # It contains all the vertices excluding the poles. They can be easily approached by the root_half_edge.
        self.vertices_list = vertices_list
        # It contains all the edges in the network.
        self.edges_list = edges_list
        # The first part of the edge between the poles.
        self.root_half_edge = root_half_edge

    # returns true if this is the link graph (u atom)
    def is_link_graph(self):
        return len(self.vertices_list) == 0

    def get_u_size(self):
        # number of edges + 1 because of the root edge
        return len(self.edges_list)

    def get_l_size(self):
        # The poles are not part from the vertices list.
        return len(self.vertices_list)

    def u_atoms(self):
        raise NotImplementedError

    def l_atoms(self):
        raise NotImplementedError

    def random_u_atom(self):
        rand_index = rn.randrange(self.get_u_size())
        return nth(self.u_atoms(), rand_index)

    def random_l_atom(self):
        rand_index = rn.randrange(self.get_l_size())
        return nth(self.l_atoms(), rand_index)

    # not needed as we never have u substitution in networks
    def replace_u_atoms(self, sampler, x, y):
        raise NotImplementedError

    # not needed as we never have l substitution in networks
    def replace_l_atoms(self, sampler, x, y):
        raise NotImplementedError

    # this is an ugly method to avoid using isinstance or similar
    def is_l_atom(self):
        return False

    # this is an ugly method to avoid using isinstance or similar
    def is_u_atom(self):
        # correct?
        return self.is_link_graph()

    def __str__(self):
        raise NotImplementedError
