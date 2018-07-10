import networkx as nx

from framework.generic_classes import CombinatorialClass


class HalfEdgeGraph(CombinatorialClass):
    """
    Base class for all different flavours of graphs that show up in the decomposition:
    Bicolored binary trees, bicolored dissections, 3-connected maps, networks, 2-connected maps, 1-connected maps.

    Combinatorically, this simply represents the class of undirected graphs with labelled vertices and unlabelled edges,
    i.e. the l-size is the number of vertices and the u-size is the number of edges.
    """

    def __init__(self, half_edge):
        """

        :param half_edge:
        """
        self.half_edge = half_edge

    def get_half_edge(self):
        """
        :return:
        """
        return self.half_edge

    def number_of_nodes(self):
        """

        :return:
        """
        return self.half_edge.get_number_of_nodes()

    def number_of_edges(self):
        """

        :return:
        """
        return self.half_edge.get_number_of_edges()

    def number_of_half_edges(self):
        """

        :return:
        """
        return len(self.half_edge.list_half_edges())

    def u_atoms(self):
        pass

    def l_atoms(self):
        pass

    # CombinatorialClass interface.

    def get_u_size(self):
        return self.number_of_edges()

    def get_l_size(self):
        return self.number_of_nodes()

    def replace_u_atoms(self, sampler, x, y):
        """
        Maybe it's not so stupid to actually implement this here ... (same for l_subs)
        :param sampler:
        :param x:
        :param y:
        :return:
        """
        pass

    def replace_l_atoms(self, sampler, x, y):
        pass

    # Networkx based functionality.

    def is_tree(self):
        return nx.is_tree(self.to_networkx_graph())

    def is_planar(self):
        return nx.check_planarity(self.to_networkx_graph())

    def is_connected(self, k=1):
        """
        Checks if the graph is k-connected.

        :param k: default 1
        :return: True iff the graph is k-connected.
        """
        pass

    def to_networkx_graph(self):
        return self.half_edge.to_networkx_graph()

    def plot(self):
        return self.half_edge.plot()
