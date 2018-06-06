from .generic_classes import CombinatorialClass
from ..utils import nth
import networkx as nx
from networkx.algorithms.components import is_connected, is_biconnected
import random as rn


class NetworkClass(CombinatorialClass):
    def __init__(self, graph, zero_pole, inf_pole):
        # graph must be connected a connected undirected networkx graph
        self.graph = graph
        # adding an edge between zero_pole and inf_pole must make the graph 2-connected
        self.zero_pole = zero_pole
        self.inf_pole = inf_pole

    # returns true if this is the link graph (u atom)
    def is_link_graph(self):
        return self.graph.number_of_nodes() == 2 and self.graph.number_of_edges() == 2 and self.graph.has_edge(
            self.zero_pole, self.inf_pole)

    # maybe handy for debugging
    def is_consistent(self):
        if not self.zero_pole in self.graph or not self.inf_pole in self.graph:
            return False
        if not is_connected(self.graph):
            return False
        if not self.is_link_graph():
            graph_copy = self.graph.copy()
            graph_copy.add_edge(self.zero_pole, self.inf_pole)
            if not is_biconnected(graph_copy):
                return False
        return True

    # relabels the nodes appending the given suffix
    def relabel(self, suffix):
        def mapping(label):
            return str(label) + str(suffix)

        nx.relabel_nodes(self.graph, mapping, copy=False)
        # also update this
        self.zero_pole = mapping(self.zero_pole)
        self.inf_pole = mapping(self.inf_pole)

    def get_u_size(self):
        # number of edges?
        return self.graph.number_of_edges()

    def get_l_size(self):
        # number of vertices not counting the poles?
        return self.graph.number_of_nodes() - 2

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
