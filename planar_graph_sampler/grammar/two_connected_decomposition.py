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

from __future__ import division

from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import *
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.generic_samplers import BoltzmannSamplerBase

from planar_graph_sampler.grammar.grammar_utils import Counter, divide_by_2, to_u_derived_class
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge
from planar_graph_sampler.combinatorial_classes.two_connected_graph import EdgeRootedTwoConnectedPlanarGraph, \
    TwoConnectedPlanarGraph
from planar_graph_sampler.grammar.network_decomposition import network_grammar


class ZeroAtomGraphBuilder(DefaultBuilder):
    """Builds zero atoms of the class G_2_arrow (= link graphs)."""

    def __init__(self):
        self._counter = Counter()

    def zero_atom(self):
        root_half_edge = HalfEdge(self_consistent=True)
        root_half_edge.node_nr = next(self._counter)
        root_half_edge_opposite = HalfEdge(self_consistent=True)
        root_half_edge_opposite.node_nr = next(self._counter)
        root_half_edge.opposite = root_half_edge_opposite
        root_half_edge_opposite.opposite = root_half_edge
        return EdgeRootedTwoConnectedPlanarGraph(root_half_edge)


def to_G_2(decomp):
    return TwoConnectedPlanarGraph(decomp.second.half_edge)


def to_G_2_dx(decomp):
    g = decomp.second
    assert isinstance(g, EdgeRootedTwoConnectedPlanarGraph) or isinstance(g, LDerivedClass)
    if isinstance(g, LDerivedClass):
        g = g.base_class_object
    return LDerivedClass(TwoConnectedPlanarGraph(g.half_edge))


def to_G_2_arrow(network):
    return EdgeRootedTwoConnectedPlanarGraph(network.half_edge)


def to_G_2_arrow_dx(network):
    return LDerivedClass(EdgeRootedTwoConnectedPlanarGraph(network.half_edge))


def divide_by_1_plus_y(evl, x, y):
    """Needed as an eval-transform for rules G_2_arrow and G_2_arrow_dx."""
    return evl / (1 + BoltzmannSamplerBase.oracle.get(y))


def two_connected_graph_grammar():
    """Constructs the grammar for two connected planar graphs.

    Returns
    -------
    DecompositionGrammar
        The grammar for sampling from G_2_dx and G_2_dx_dx.
    """

    Z = ZeroAtomSampler
    L = LAtomSampler
    D = AliasSampler('D')
    D_dx = AliasSampler('D_dx')
    F = AliasSampler('F')
    F_dx = AliasSampler('F_dx')
    G_2_dy = AliasSampler('G_2_dy')
    G_2_dx_dy = AliasSampler('G_2_dx_dy')
    G_2_arrow = AliasSampler('G_2_arrow')
    G_2_arrow_dx = AliasSampler('G_2_arrow_dx')
    Trans = TransformationSampler
    Bij = BijectionSampler
    DxFromDy = LDerFromUDerSampler

    grammar = DecompositionGrammar()
    grammar.rules = network_grammar().rules

    grammar.rules = {

        # two connected

        'G_2_arrow': Trans(Z() + D, to_G_2_arrow, eval_transform=divide_by_1_plus_y),  # see 5.5

        'F': Bij(L() ** 2 * G_2_arrow, to_G_2),

        'G_2_dy': Trans(F, to_u_derived_class, eval_transform=divide_by_2),

        'G_2_dx': DxFromDy(G_2_dy, alpha_l_u=2.0),  # see p. 26

        # l-derived two connected

        'G_2_arrow_dx': Trans(D_dx, to_G_2_arrow_dx, eval_transform=divide_by_1_plus_y),

        'F_dx': Bij(L() ** 2 * G_2_arrow_dx + 2 * L() * G_2_arrow, to_G_2_dx),

        'G_2_dx_dy': Trans(F_dx, to_u_derived_class, eval_transform=divide_by_2),

        'G_2_dx_dx': DxFromDy(G_2_dx_dy, alpha_l_u=1.0),  # see 5.5

    }
    grammar.set_builder(['G_2_arrow'], ZeroAtomGraphBuilder())
    return grammar


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100

    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    BoltzmannSamplerBase.debug_mode = True

    grammar = two_connected_graph_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'y'
    sampled_class = 'G_2_dx_dx'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    while True:
        try:
            g = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
            if g.l_size > 0:
                g = g.underive_all()
                assert g.is_consistent
                print(g)
                g.plot(with_labels=False, node_size=25, use_planar_drawer=False)
                plt.show()
        except RecursionError:
            print("Recursion error")
