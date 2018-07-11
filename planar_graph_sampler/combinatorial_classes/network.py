import random as rn

from framework.utils import nth
from planar_graph_sampler.combinatorial_classes.half_edge_graph import HalfEdgeGraph


class Network(HalfEdgeGraph):
    """

    """

    def __init__(self, half_edge, is_linked, l_size=None, u_size=None):
        # It contains all the vertices excluding the poles. They can be easily approached by the root_half_edge.
        #self.vertices_list = vertices_list
        # It contains all the edges in the network.
        #self.edges_list = edges_list
        # The first part of the edge between the poles.
        assert half_edge.opposite is not None
        super().__init__(half_edge)
        self.is_linked = is_linked
        if l_size is None:
            l_size = self.number_of_nodes() - 2
        self.l_size = l_size
        if u_size is None:
            u_size = self.number_of_edges() - (not is_linked)
        self.u_size = u_size

    def is_consistent(self):
        super_ok = super().is_consistent()
        is_two_connected = self.is_connected(2)
        return all([super_ok, is_two_connected])

    # returns true if this is the link graph (u atom)
    def is_link_graph(self):
        return self.number_of_nodes() == 2


    def get_zero_pole(self):
        """
        Returns the half-edge between zero-pole and inf-pole.
        :return:
        """
        return self.half_edge

    def get_inf_pole(self):
        """
        Returns the half-edge between inf-pole and zero-pole.
        :return:
        """
        return self.half_edge.opposite

    def get_u_size(self):
        # number of edges + 1 because of the root edge
        #return len(self.edges_list)
        #res = self.number_of_edges()
        #if not self.is_linked:
        #    res -= 1
        #return res
        return self.u_size

    def get_l_size(self):
        # The poles are not part from the vertices list.
        #return len(self.vertices_list)
        # The poles don't count.
        #return self.number_of_nodes() - 2
        return self.l_size

    def random_u_atom(self):
        rand_index = rn.randrange(self.get_u_size())
        return nth(self.u_atoms(), rand_index)

    def random_l_atom(self):
        rand_index = rn.randrange(self.get_l_size())
        return nth(self.l_atoms(), rand_index)
