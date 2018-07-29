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

from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import *
from framework.decomposition_grammar import AliasSampler, DecompositionGrammar
from framework.generic_samplers import BoltzmannSamplerBase

from planar_graph_sampler.combinatorial_classes.one_connected_graph import OneConnectedPlanarGraph
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100, planar_graph_evals_n1000
from planar_graph_sampler.grammar.grammar_utils import underive
from planar_graph_sampler.grammar.two_connected_decomposition import two_connected_graph_grammar


class Merger(DefaultBuilder):
    """Merges a set of l-derived graphs at their marked vertices."""

    def set(self, graphs):
        if len(graphs) is 0:
            return LDerivedClass(OneConnectedPlanarGraph())
        res = graphs.pop().base_class_object
        for g in graphs:
            res.half_edge.insert_all(g.base_class_object.half_edge)
        return LDerivedClass(res)


def merge(prod):
    """Merges derived one-connected graphs."""
    # lhs is a bi-derived connected and rhs a derived connected.
    lhs = prod.first
    rhs = prod.second
    g1 = lhs.base_class_object.base_class_object
    g2 = rhs.base_class_object
    if not g2.half_edge.is_trivial:
        g1.half_edge.insert_all(g2.half_edge)
    return lhs


def subs_marked_vertex(decomp):
    """Substitutes marked vertex."""
    plug_in = decomp.first
    if isinstance(decomp.first, ProdClass):
        plug_in = decomp.first.second.base_class_object
    assert isinstance(plug_in, LDerivedClass) and isinstance(plug_in.base_class_object, OneConnectedPlanarGraph)
    plug_in = plug_in.base_class_object
    g = decomp.second.base_class_object.base_class_object
    g.half_edge.insert_all(plug_in.half_edge)
    return LDerivedClass(LDerivedClass(OneConnectedPlanarGraph(g.half_edge)))


def rej_to_G_1(g):
    return bern(1 / (g.l_size + 1))


def one_connected_graph_grammar():
    """Constructs the grammar for connected planar graphs.

    Returns
    -------
    DecompositionGrammar
        The grammar for sampling from G_1_dx and G_1_dx_dx.
    """

    # Some shortcuts to make the grammar more readable.
    L = LAtomSampler
    G_2_dx = AliasSampler('G_2_dx')
    G_2_dx_dx = AliasSampler('G_2_dx_dx')
    G_1_dx = AliasSampler('G_1_dx')
    G_1_dx_dx = AliasSampler('G_1_dx_dx')
    G_1_dx_dx_helper = AliasSampler('G_1_dx_dx_helper')
    Set = SetSampler
    LSubs = LSubsSampler
    Bij = BijectionSampler
    Rej = RejectionSampler

    grammar = DecompositionGrammar()
    grammar.rules = two_connected_graph_grammar().rules
    grammar.rules = {

        # 1 connected planar graphs

        'G_1_dx': Set(0, LSubs(G_2_dx, L() * G_1_dx)),

        'G_1_dx_dx_helper': Bij((G_1_dx + L() * G_1_dx_dx) * LSubs(G_2_dx_dx, L() * G_1_dx), subs_marked_vertex),

        'G_1_dx_dx': Bij(G_1_dx_dx_helper * G_1_dx, merge),

        'G_1': Bij(Rej(G_1_dx, rej_to_G_1), underive)  # See lemma 15.

    }
    grammar.set_builder(['G_1_dx'], Merger())

    return grammar


if __name__ == '__main__':
    grammar = one_connected_graph_grammar()
    grammar.init()

    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    BoltzmannSamplerBase.debug_mode = False

    symbolic_x = 'x'
    symbolic_y = 'y'

    sampled_class = 'G_1_dx_dx'

    try:
        print(BoltzmannSamplerBase.oracle.get_expected_l_size(sampled_class, symbolic_x, symbolic_y))
    except BoltzmannFrameworkError:
        pass

    while True:

        try:
            g = grammar.sample(sampled_class, symbolic_x, symbolic_y)
            if g.l_size > 50:
                if isinstance(g, DerivedClass):
                    g = g.base_class_object
                if isinstance(g, DerivedClass):
                    g = g.base_class_object
                print(g)
                assert g.is_consistent

                import matplotlib.pyplot as plt

                g.plot(with_labels=False, node_size=25, use_planar_drawer=True)
                plt.show()
        except RecursionError:
            pass
