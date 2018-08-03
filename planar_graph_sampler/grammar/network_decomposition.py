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

from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import *
from framework.generic_samplers import BoltzmannSamplerBase
from planar_graph_sampler.grammar.grammar_utils import Counter

from planar_graph_sampler.bijections.networks import merge_networks_in_parallel, merge_networks_in_series, \
    substitute_edge_by_network
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge
from planar_graph_sampler.combinatorial_classes.network import Network
from planar_graph_sampler.grammar.three_connected_decomposition import three_connected_graph_grammar


class NetworkBuilder(DefaultBuilder):
    """Builds u-atoms of networks."""

    def __init__(self):
        self._counter = Counter()

    def u_atom(self):
        """Constructs the trivial link network consisting of the poles and an edge between them."""
        # Create the zero-pole of the network.
        root_half_edge = HalfEdge(self_consistent=True)
        root_half_edge.node_nr = next(self._counter)
        # Creates the inf-pole.
        root_half_edge_opposite = HalfEdge(self_consistent=True)
        root_half_edge_opposite.node_nr = next(self._counter)
        # Link the poles.
        root_half_edge.opposite = root_half_edge_opposite
        root_half_edge_opposite.opposite = root_half_edge
        res = Network(root_half_edge, is_linked=True, l_size=0, u_size=1)
        return res


class SNetworkBuilder(NetworkBuilder):
    """Builds S-networks."""

    def product(self, lhs, rhs):
        """Merges the given networks in series."""
        if isinstance(lhs, Network) and isinstance(rhs, Network):
            return merge_networks_in_series(lhs, rhs)
        if isinstance(lhs, Network):
            # rhs is an l-atom.
            assert isinstance(rhs, LAtomClass)
            return lhs
        # Other case is symmetric.
        return self.product(rhs, lhs)


class PNetworkBuilder(NetworkBuilder):
    """Builds P-networks."""

    def set(self, networks):
        """Merges a set of networks in parallel."""
        if len(networks) == 0:
            # An empty set is like a zero atom (it has size 0).
            # We use the generic zero atom here as a zero-atom-network cannot be defined.
            return ZeroAtomClass()
        # TODO Without reversing the list of networks, weird things happen, find out why.
        networks.reverse()
        res = networks.pop()
        for nw in networks:
            res = merge_networks_in_parallel(res, nw)
        return res

    def product(self, n1, n2):
        """Merges the set {n1, n2} of networks in parallel."""
        # n2 might be the zero-atom resulting from an empty set of networks.
        if isinstance(n2, ZeroAtomClass):
            return n1
        assert isinstance(n1, Network) and isinstance(n2, Network)
        return self.set([n1, n2])


def g_3_arrow_to_network(decomp):
    """To be used as a bijection in the rules H and H_dx."""
    if isinstance(decomp, ProdClass):
        network = decomp.first
        u_der_graph = decomp.second
        substitute_edge_by_network(u_der_graph.marked_atom, network)
        return Network(u_der_graph.base_class_object.half_edge, is_linked=False)
    else:
        graph = decomp
        if isinstance(decomp, LDerivedClass):
            graph = decomp.base_class_object
        link_edge = graph.half_edge
        # Create and return the network.
        return Network(link_edge, is_linked=False)


def network_grammar():
    """Constructs the grammar for networks.

    Returns
    -------
    DecompositionGrammar
        The grammar for sampling from D and D_dx.
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
    grammar.rules = three_connected_graph_grammar().rules

    grammar.rules = {

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

    }

    # Set up builders.
    grammar.set_builder(['D', 'S', 'P', 'H', 'D_dx', 'S_dx', 'P_dx', 'H_dx'], NetworkBuilder())
    grammar.set_builder(['P', 'P_dx'], PNetworkBuilder())
    grammar.set_builder(['S', 'S_dx'], SNetworkBuilder())

    return grammar


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100, planar_graph_evals_n1000

    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n1000)
    BoltzmannSamplerBase.debug_mode = True

    grammar = network_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'y'
    sampled_class = 'D_dx'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    # random.seed(0)

    while True:
        try:
            g = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
            if g.l_size > 0:
                print(g)
                assert g.is_consistent
                g.plot(with_labels=False, use_planar_drawer=False, node_size=25)
                plt.show()
        except RecursionError:
            print("RecursionError")
