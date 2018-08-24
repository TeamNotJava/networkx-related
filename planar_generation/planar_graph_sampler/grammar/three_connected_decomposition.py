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
from framework.generic_samplers import *
from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import BoltzmannSamplerBase

from planar_graph_sampler.grammar.grammar_utils import to_l_derived_class, divide_by_2
from planar_graph_sampler.grammar.irreducible_dissection_decomposition import irreducible_dissection_grammar
from planar_graph_sampler.bijections.primal_map import PrimalMap
from planar_graph_sampler.combinatorial_classes.three_connected_graph import EdgeRootedThreeConnectedPlanarGraph


def primal_map(dissection):
    """Invokes the primal map bijection."""
    half_edge = PrimalMap().primal_map_bijection(dissection.half_edge)
    return EdgeRootedThreeConnectedPlanarGraph(half_edge)


def three_connected_graph_grammar():
    """Builds the three-connected planar graph grammar.

    Returns
    -------
    DecompositionGrammar
        The grammar for sampling from G_3_arrow_dx and G_3_arrow_dy
    """

    # Some shorthands to keep the grammar readable.
    J_a = AliasSampler('J_a')
    J_a_dx = AliasSampler('J_a_dx')
    M_3_arrow = AliasSampler('M_3_arrow')
    M_3_arrow_dx = AliasSampler('M_3_arrow_dx')
    G_3_arrow_dx = AliasSampler('G_3_arrow_dx')
    Bij = BijectionSampler
    Trans = TransformationSampler
    DyFromDx = UDerFromLDerSampler

    grammar = DecompositionGrammar()
    # Depends on irreducible dissection so we add those rules.
    grammar.rules = irreducible_dissection_grammar().rules

    grammar.rules = {

        'M_3_arrow': Bij(J_a, primal_map),

        'M_3_arrow_dx': Bij(J_a_dx, primal_map),

        'G_3_arrow': Trans(M_3_arrow, eval_transform=divide_by_2),  # See 4.1.9.

        'G_3_arrow_dx': Trans(M_3_arrow_dx, to_l_derived_class, eval_transform=divide_by_2),

        'G_3_arrow_dy': DyFromDx(G_3_arrow_dx, alpha_u_l=3)  # See 5.3.3.

    }

    return grammar


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100, planar_graph_evals_n1000

    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)

    grammar = three_connected_graph_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'G_3_arrow_dy'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    # random.seed(0)

    while True:
        try:
            g = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
            if g.l_size > 0:
                print(g)
                g = g.underive_all()
                assert g.is_consistent
                g.plot(node_size=25, use_planar_drawer=True)
                plt.show()
        except RecursionError:
            print("Recursion error")
