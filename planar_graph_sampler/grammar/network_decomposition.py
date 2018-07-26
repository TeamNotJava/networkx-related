from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import *
from framework.generic_samplers import BoltzmannSamplerBase
from framework.utils import Counter

from planar_graph_sampler.bijections.networks import merge_networks_in_parallel, merge_networks_in_series
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge
from planar_graph_sampler.combinatorial_classes.network import Network
from planar_graph_sampler.combinatorial_classes.three_connected_graph import EdgeRootedThreeConnectedPlanarGraph
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n1000
from planar_graph_sampler.grammar.three_connected_decomposition import three_connected_graph_grammar

counter = Counter()


class NetworkBuilder(DefaultBuilder):
    """Builds u-atoms of networks."""

    def u_atom(self):
        """

        :return: The trivial link network consisting of the poles and an edge between them.
        """
        # Create the zero-pole of the network.
        root_half_edge = HalfEdge(self_consistent=True)
        root_half_edge.node_nr = next(counter)

        # Creates the inf-pole.
        root_half_edge_opposite = HalfEdge(self_consistent=True)
        root_half_edge_opposite.node_nr = next(counter)

        # Link the poles.
        root_half_edge.opposite = root_half_edge_opposite
        root_half_edge_opposite.opposite = root_half_edge

        res = Network(root_half_edge, is_linked=True, l_size=0, u_size=1)
        return res


class SNetworkBuilder(NetworkBuilder):
    """Builds S-networks."""

    def product(self, lhs, rhs):
        """
        Merges the given networks in series.

        :param lhs:
        :param rhs:
        :return:
        """
        if isinstance(lhs, Network) and isinstance(rhs, Network):
            return merge_networks_in_series(lhs, rhs)
        if isinstance(lhs, Network):
            # _rhs is an l-atom.
            assert isinstance(rhs, LAtomClass)
            return lhs
        # Other case is symmetric.
        return self.product(rhs, lhs)


class PNetworkBuilder(NetworkBuilder):
    """Builds P-networks."""

    def set(self, networks):
        """
        Merges a set of networks in parallel.

        :param networks: Networks to be merged.
        :return: The network resulting from the parallel merge operation or None if no networks were given.
        """
        if len(networks) == 0:
            return None
        res = networks[0]
        for i in range(1, len(networks)):
            res = merge_networks_in_parallel(res, networks[i])
        return res

    def product(self, n1, n2):
        """
        Merges the set {n1, n2} of networks.

        :param n1:
        :param n2:
        :return:
        """
        if n2 is None:
            return n1
        assert isinstance(n1, Network) and isinstance(n2, Network)
        return self.set([n1, n2])


def g_3_arrow_to_network(decomp):
    if isinstance(decomp, ProdClass):
        network = decomp._first
        graph = decomp._second
        graph.replace_random_edge(network)
        return Network(graph.get_half_edge(), is_linked=False)
    else:
        graph = decomp
        assert isinstance(graph, EdgeRootedThreeConnectedPlanarGraph)
        link_edge = graph.get_half_edge()
        # Create and return the network.
        return Network(link_edge, is_linked=False)


def network_grammar():
    """
    Constructs the grammar for networks.

    :return:
    """

    L = LAtomSampler
    U = UAtomSampler
    G_3_arrow = AliasSampler('G_3_arrow')
    G_3_arrow_dx = AliasSampler('G_3_arrow_dx')
    G_3_arrow_dy = AliasSampler('G_3_arrow_dy')
    D = AliasSampler('D')
    D_dx = AliasSampler('D_dx')
    S = AliasSampler('S')
    S_dx = AliasSampler('S_dx')
    P = AliasSampler('P')
    P_dx = AliasSampler('P_dx')
    H = AliasSampler('H')
    H_dx = AliasSampler('H_dx')
    Bij = BijectionSampler
    Set = SetSampler
    USubs = USubsSampler

    grammar = DecompositionGrammar()
    grammar.add_rules(three_connected_graph_grammar().get_rules())

    grammar.add_rules({

        # networks

        'D': U() + S + P + H,

        'S': (U() + P + H) * L() * D,

        'P': U() * Set(1, S + H) + Set(2, S + H),

        'H': Bij(USubs(G_3_arrow, D), g_3_arrow_to_network),

        # l-derived networks

        'D_dx': S_dx + P_dx + H_dx,

        'S_dx': (P_dx + H_dx) * L() * D + (U() + P + H) * (D + L() * D_dx),

        'P_dx': U() * (S_dx + H_dx) * Set(0, S + H) + (S_dx + H_dx) * Set(1, S + H),

        'H_dx': Bij(USubs(G_3_arrow_dx, D) + D_dx * USubs(G_3_arrow_dy, D), g_3_arrow_to_network),

    })

    grammar.set_builder(['D', 'S', 'P', 'H', 'D_dx', 'S_dx', 'P_dx', 'H_dx'], NetworkBuilder())
    grammar.set_builder(['P', 'P_dx'], PNetworkBuilder())
    grammar.set_builder(['S', 'S_dx'], SNetworkBuilder())

    return grammar


if __name__ == '__main__':
    grammar = network_grammar()
    grammar.init()

    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n1000)
    BoltzmannSamplerBase.debug_mode = False

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'y'

    sampled_class = 'D'



    # while True:
    #     try:
    #         g = grammar.sample(sampled_class, symbolic_x, symbolic_y)
    #         if g.l_size() == 2:
    #             print(g)
    #             assert g.is_consistent()
    #
    #             import matplotlib.pyplot as plt
    #
    #             g.plot(with_labels=False)
    #             plt.show()
    #     except RecursionError:
    #         pass

    c = [0, 0, 0, 0, 0, 0, 0, 0]
    samples = 1000
    i = 0
    while i < samples:
        try:
            g = grammar.sample(sampled_class, symbolic_x, symbolic_y)
            if g.l_size() == 2:
                assert g.is_consistent()
                c[g.u_size()] += 1
                i += 1
        except RecursionError:
            pass

    print(c)
