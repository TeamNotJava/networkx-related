import random as rnd

from planar_graph_sampler.bijections.networks import substitute_edge_by_network
from planar_graph_sampler.combinatorial_classes.half_edge_graph import HalfEdgeGraph


class EdgeRootedThreeConnectedPlanarGraph(HalfEdgeGraph):
    """

    """

    def __init__(self, root_half_edge):
        super().__init__(root_half_edge)

    def is_consistent(self):
        super_ok = super().is_consistent()
        is_planar = self.is_planar()
        return super_ok and is_planar

    def get_u_size(self):
        # Root edge does not count.
        return self.number_of_edges() - 1

    def get_l_size(self):
        # The vertices adjacent to the root do not count.
        return self.number_of_nodes() - 2

    def replace_u_atoms(self, sampler, x, y):
        """
        Needed in the u-substitution that occurs in the network decomposition.

        :param sampler:
        :param x:
        :param y:
        :return:
        """
        # Get the edges for substitution in a separate set.
        edges_for_subs = self.half_edge.get_all_half_edges(include_opp=False, include_unpaired=False)
        # Don't substitute the root edge.
        assert self.half_edge in edges_for_subs and self.half_edge.opposite not in edges_for_subs
        edges_for_subs.remove(self.half_edge)

        # Substitute the edges with a newly sampled network one by one.
        for edge_for_substitution in edges_for_subs:
            network = sampler.sample(x, y)
            substitute_edge_by_network(edge_for_substitution, network)

        return self


class UDerivedEdgeRootedThreeConnectedPlanarGraph(EdgeRootedThreeConnectedPlanarGraph):
    """
    Is like a normal edge rooted graph but has one additional random distinguished u-atom.
    """

    def __init__(self, root_half_edge, vertices=None, edges=None):
        super().__init__(root_half_edge)
        # Pick random edge, but not the root edge itself.
        possible_edges = root_half_edge.get_all_half_edges(include_unpaired=False) - {root_half_edge,
                                                                                      root_half_edge.opposite}
        self.random_edge = rnd.choice(list(possible_edges))

    def get_u_size(self):
        # Root edge and random edge do not count.
        return self.number_of_edges() - 2

    def replace_u_atoms(self, sampler, x, y):
        """
        Needed in the u-substitution that occurs in the network decomposition.

        :param sampler:
        :param x:
        :param y:
        :return:
        """

        # TODO git rid of code dup

        # Get the edges for substitution in a separate set.
        edges_for_subs = self.half_edge.get_all_half_edges(include_opp=False, include_unpaired=False)

        # Don't substitute the root edge.
        assert self.half_edge in edges_for_subs and self.half_edge.opposite not in edges_for_subs
        edges_for_subs.remove(self.half_edge)

        # Don't substitute the random edge.
        try:
            edges_for_subs.remove(self.random_edge)
        except KeyError:
            edges_for_subs.remove(self.random_edge.opposite)

        # Substitute the edges with a newly sampled network one by one.
        for edge_for_substitution in edges_for_subs:
            network = sampler.sample(x, y)
            substitute_edge_by_network(edge_for_substitution, network)

        return self

    def replace_random_edge(self, network):
        """
        Plugs network into the random edge.

        :param network:
        :return:
        """
        substitute_edge_by_network(self.random_edge, network)
