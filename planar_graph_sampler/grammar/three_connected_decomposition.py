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
from planar_graph_sampler.grammar.binary_tree_decomposition import EarlyRejectionControl

from planar_graph_sampler.grammar.grammar_utils import to_l_derived_class, divide_by_2
from planar_graph_sampler.grammar.irreducible_dissection_decomposition import irreducible_dissection_grammar
from planar_graph_sampler.bijections.primal_map import PrimalMap
from planar_graph_sampler.combinatorial_classes.three_connected_graph import EdgeRootedThreeConnectedPlanarGraph


def primal_map(dissection):
    """Invokes the primal map bijection."""
    l_size = dissection.l_size
    half_edge = PrimalMap().primal_map_bijection(dissection.half_edge)
    res = EdgeRootedThreeConnectedPlanarGraph(half_edge)
    # print("{}, {}".format(l_size, res.l_size))
    # assert l_size == res.l_size
    return res


def to_bi_l_derived_class(obj):
    return to_l_derived_class(to_l_derived_class(obj))


def mark_u_atom(g_dy):
    g_dy.marked_atom = g_dy.underive_all().random_u_atom()
    return g_dy


def mark_2_u_atoms(g_dy_dy):
    he1, he2 = g_dy_dy.underive_all().two_random_u_atoms()
    assert he1 is not None and he2 is not None
    g_dy_dy.marked_atom = he1
    g_dy_dy.base_class_object.marked_atom = he2
    return g_dy_dy


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
    J_a_dx_dx = AliasSampler('J_a_dx_dx')
    G_3_arrow = AliasSampler('G_3_arrow')
    G_3_arrow_dy = AliasSampler('G_3_arrow_dy')
    G_3_arrow_dx = AliasSampler('G_3_arrow_dx')
    G_3_arrow_dx_dx = AliasSampler('G_3_arrow_dx_dx')
    G_3_arrow_dx_dy = AliasSampler('G_3_arrow_dx_dy')
    G_3_arrow_dy_dy = AliasSampler('G_3_arrow_dy_dy')
    M_3_arrow = AliasSampler('M_3_arrow')
    M_3_arrow_dx = AliasSampler('M_3_arrow_dx')
    M_3_arrow_dx_dx = AliasSampler('M_3_arrow_dx_dx')
    Bij = BijectionSampler
    Trans = TransformationSampler
    DyFromDx = UDerFromLDerSampler

    grammar = DecompositionGrammar()
    # Depends on irreducible dissection so we add those rules.
    grammar.rules = irreducible_dissection_grammar().rules
    EarlyRejectionControl.grammar = grammar

    grammar.rules = {

        # Non-derived 3-connected rooted planar maps/graphs.

        'M_3_arrow': Bij(J_a, primal_map),

        'G_3_arrow': Trans(M_3_arrow, eval_transform=divide_by_2),  # See 4.1.9.

<<<<<<< Updated upstream
        'G_3_arrow_dx': Trans(M_3_arrow_dx, to_l_derived_class, eval_transform=divide_by_2),
=======
<<<<<<< Updated upstream
        'G_3_arrow_dx': Trans(M_3_arrow_dx, to_l_derived_class, eval_transform=lambda evl, x, y: 0.5 * evl),
=======
        # Derived 3-connected rooted planar maps/graphs.

        'M_3_arrow_dx': Bij(J_a_dx, primal_map),

        'G_3_arrow_dx': Trans(M_3_arrow_dx, to_l_derived_class, eval_transform=divide_by_2),
>>>>>>> Stashed changes

        'G_3_arrow_dy':
            Bij(
                DyFromDx(G_3_arrow_dx, alpha_u_l=3),  # See 5.3.3.
                mark_u_atom
            ),
>>>>>>> Stashed changes

        # Bi-derived 3-connected rooted planar maps/graphs.

        'M_3_arrow_dx_dx': Bij(J_a_dx_dx, primal_map),

        'G_3_arrow_dx_dx': Trans(M_3_arrow_dx_dx, to_bi_l_derived_class, eval_transform=divide_by_2),

        'G_3_arrow_dx_dy':
            Bij(
                DyFromDx(G_3_arrow_dx_dx, alpha_u_l=3),
                mark_u_atom
            ),

        'G_3_arrow_dy_dy':
            Bij(
                DyFromDx(
                    Bij(
                        G_3_arrow_dx_dy,
                        lambda gamma: gamma.invert_derivation_order()
                    ),
                    alpha_u_l=3
                ),
                mark_2_u_atoms
            ),

    }

    return grammar


if __name__ == "__main__":
<<<<<<< Updated upstream
    import matplotlib.pyplot as plt
    from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100, planar_graph_evals_n1000
=======
<<<<<<< Updated upstream
    grammar = three_connected_graph_grammar()
    grammar.init()
=======
    import matplotlib.pyplot as plt
    from planar_graph_sampler.evaluations_planar_graph import *
    from timeit import default_timer as timer
>>>>>>> Stashed changes
>>>>>>> Stashed changes

    oracle = EvaluationOracle(my_evals_100)
    BoltzmannSamplerBase.oracle = oracle

    grammar = three_connected_graph_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
<<<<<<< Updated upstream
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
=======
<<<<<<< Updated upstream

    sampled_class = 'G_3_arrow_dy'

    g = grammar.sample(sampled_class, symbolic_x, symbolic_y)
    g = g.base_class_object
    print(g)
    assert g.is_consistent

    import matplotlib.pyplot as plt

    g.plot(node_size=50)
    plt.show()
=======
    sampled_class = 'G_3_arrow_dy_dy'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    # random.seed(0)
    # boltzmann_framework_random_gen.seed(0)

    try:
        print("expected avg. size: {}\n".format(oracle.get_expected_l_size(sampled_class, symbolic_x, symbolic_y)))
    except BoltzmannFrameworkError:
        pass

    l_sizes = []
    i = 0
    samples = 1
    start = timer()
    while i < samples:
        obj = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
        assert obj.marked_atom is not None
        l_sizes.append(obj.l_size)
        i += 1
    end = timer()
    print()
    print("avg. size: {}".format(sum(l_sizes) / len(l_sizes)))
    print("time: {}".format(end - start))

    # while True:
    #     g = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
    #     if g.l_size > 100:
    #         print(g)
    #         print(g.u_size / g.l_size)
    #         # g = g.underive_all()
    #         # assert g.is_consistent
    #         # g.plot(node_size=25, use_planar_drawer=True)
    #         # plt.show()
>>>>>>> Stashed changes
>>>>>>> Stashed changes
