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

from planar_graph_sampler.grammar.binary_tree_decomposition import EarlyRejectionControl
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
        root_half_edge = HalfEdge()
        root_half_edge.next = root_half_edge
        root_half_edge.prior = root_half_edge
        root_half_edge.node_nr = next(self._counter)
        # Creates the inf-pole.
        root_half_edge_opposite = HalfEdge()
        root_half_edge_opposite.next = root_half_edge_opposite
        root_half_edge_opposite.prior = root_half_edge_opposite
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
        # Form is either (lhs,rhs) = (network, network) (1) or (lhs,rhs) = (network, l-atom) (2)
        if isinstance(lhs, Network) and isinstance(rhs, Network):
            # Form (1)
            res = merge_networks_in_series(lhs, rhs)
        else:
            # Form (2)
            assert isinstance(rhs, LAtomClass), rhs
            # The l-atom can be discarded.
            res = lhs
        assert not res.is_linked
        return res


class PNetworkBuilder(NetworkBuilder):
    """Builds P-networks."""

    def set(self, networks):
        """Merges a set of networks in parallel."""
        if len(networks) == 0:
            # An empty set is like a zero atom (it has size 0).
            # We use the generic zero atom here as a zero-atom-network cannot be defined.
            return ZeroAtomClass()
        # TODO Without reversing the list of networks, weird things happen, find out why.
        # networks.reverse()
        res = networks.pop()
        for nw in networks:
            res = merge_networks_in_parallel(res, nw)
        return res

    def product(self, n1, n2):
        """Merges the set {n1, n2} of networks in parallel."""
        # n2 might be the zero-atom resulting from an empty set of networks.
        assert not isinstance(n1, ZeroAtomClass)
        if isinstance(n2, ZeroAtomClass):
            return n1
        assert isinstance(n1, Network) and isinstance(n2, Network), n2
        return self.set([n1, n2])


def g_3_arrow_to_network(decomp):
    """To be used as a bijection in the rules H, H_dx and H_dx_dx."""
    # decomp = graph (1) | (network,graph_dy) (2) | ((network, network),graph_dy_dy) (3)
    if not isinstance(decomp, ProdClass):
        # Form (1)
        g = decomp.underive_all()
        link_edge = g.half_edge
        res = Network(link_edge, is_linked=False)
    elif isinstance(decomp.first, Network):
        # Form (2)
        network = decomp.first
        marked_atom = decomp.second.marked_atom
        g = decomp.second.underive_all()
        substitute_edge_by_network(marked_atom, network)
        res = Network(g.half_edge, is_linked=False)
    else:
        # Form (3)
        network1 = decomp.first.first
        network2 = decomp.first.second
        marked_atom1 = decomp.second.marked_atom
        marked_atom2 = decomp.second.base_class_object.marked_atom
        g = decomp.second.underive_all()
        substitute_edge_by_network(marked_atom1, network1)
        substitute_edge_by_network(marked_atom2, network2)
        res = Network(g.half_edge, is_linked=False)
    res.type = 'H'
    return res


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
    D_dx_dx = AliasSampler('D_dx_dx')
    S_dx_dx = AliasSampler('S_dx_dx')
    P_dx_dx = AliasSampler('P_dx_dx')
    H_dx_dx = AliasSampler('H_dx_dx')
    G_3_arrow_dx_dx = AliasSampler('G_3_arrow_dx_dx')
    G_3_arrow_dx_dy = AliasSampler('G_3_arrow_dx_dy')
    G_3_arrow_dy_dy = AliasSampler('G_3_arrow_dy_dy')
    Bij = BijectionSampler
    Set = SetSampler
    USubs = USubsSampler

    grammar = DecompositionGrammar()
    grammar.rules = three_connected_graph_grammar().rules

    grammar.rules = {

        # networks

        'D': U() + S + P + H,

        'S': (U() + P + H) * D * L(),

        'P': U() * Set(1, S + H) + Set(2, S + H),

        'H': Bij(USubs(G_3_arrow, D), g_3_arrow_to_network),

        # l-derived networks

        'D_dx': S_dx + P_dx + H_dx,

        'S_dx':
            (P_dx + H_dx) * D * L()
            + (U() + P + H) * D_dx * L()
            + (U() + P + H) * D,

        'P_dx':
            U() * (S_dx + H_dx) * Set(0, S + H)
            + (S_dx + H_dx) * Set(1, S + H),

        'H_dx':
            Bij(
                USubs(G_3_arrow_dx, D) + D_dx * USubs(G_3_arrow_dy, D),
                g_3_arrow_to_network
            ),

        # bi-l-derived networks

        'D_dx_dx':
            S_dx_dx + P_dx_dx + H_dx_dx,

        'S_dx_dx':
            (P_dx_dx + H_dx_dx) * D * L()
            + 2 * (P_dx + H_dx) * D_dx * L()
            + (U() + P + H) * D_dx_dx * L()
            + 2 * (P_dx + H_dx) * D
            + 2 * (U() + P + H) * D_dx,

        'P_dx_dx':
            U() * (S_dx_dx + H_dx_dx) * Set(0, S + H)
            + U() * (S_dx + H_dx) ** 2 * Set(0, S + H)
            + (S_dx_dx + H_dx_dx) * Set(1, S + H)
            + (S_dx + H_dx) ** 2 * Set(0, S + H),

        'H_dx_dx':
            Bij(
                USubs(G_3_arrow_dx_dx, D)
                + 2 * D_dx * USubs(G_3_arrow_dx_dy, D)
                + D_dx_dx * USubs(G_3_arrow_dy, D)
                + D_dx ** 2 * USubs(G_3_arrow_dy_dy, D),
                g_3_arrow_to_network
            ),

    }
    # Set up builders.
    grammar.set_builder(['D', 'S', 'P', 'H',
                         'D_dx', 'S_dx', 'P_dx', 'H_dx',
                         'D_dx_dx', 'S_dx_dx', 'P_dx_dx', 'H_dx_dx'], NetworkBuilder())
    grammar.set_builder(['P', 'P_dx', 'P_dx_dx'], PNetworkBuilder())
    grammar.set_builder(['S', 'S_dx', 'S_dx_dx'], SNetworkBuilder())
    EarlyRejectionControl.grammar = grammar

    return grammar


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from planar_graph_sampler.evaluations_planar_graph import *
    from timeit import default_timer as timer

    oracle = EvaluationOracle(my_evals_100)
    BoltzmannSamplerBase.oracle = oracle
    BoltzmannSamplerBase.debug_mode = False

    start = timer()
    grammar = network_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'y'
    sampled_class = 'D'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)
    end = timer()
    print("Time init: {}".format(end - start))

    try:
        print("expected avg. size: {}\n".format(oracle.get_expected_l_size(sampled_class, symbolic_x, symbolic_y)))
    except BoltzmannFrameworkError:
        pass

    # random.seed(0)
    # boltzmann_framework_random_gen.seed(13)

    l_sizes = []
    i = 0
    samples = 100000
    start = timer()
    while i < samples:
        obj = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
        l_size = obj.l_size
        # print(l_size)
        l_sizes.append(l_size)
        # if obj.l_size == 4:
        #    i += 1
        i += 1
    end = timer()
    print()
    print("avg. size: {}".format(sum(l_sizes) / len(l_sizes)))
    print("time: {}".format(end - start))

    # while True:
    #     g = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
    #     if g.l_size == 2:
    #         g = g.underive_all()
    #         print(g)
    #         print(g.number_of_edges)
    #         print("is linked: {}".format(g.is_linked))
    #         assert g.is_consistent
    #         g.plot(with_labels=False, use_planar_drawer=False, node_size=25)
    #         plt.show()
