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

from framework.generic_samplers import *
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import BoltzmannSamplerBase
from planar_graph_sampler.bijections.closure import Closure
from planar_graph_sampler.combinatorial_classes import BinaryTree
from planar_graph_sampler.combinatorial_classes.dissection import IrreducibleDissection
from planar_graph_sampler.grammar.binary_tree_decomposition import binary_tree_grammar, EarlyRejectionControl


def closure(binary_tree):
    """To be used as bijection in the grammar."""
    binary_tree = binary_tree.underive_all()
    return Closure().closure(binary_tree)
    # if isinstance(binary_tree, LDerivedClass):
    #     # derived
    #     binary_tree = binary_tree.base_class_object
    #     if isinstance(binary_tree, LDerivedClass):
    #         # bi-derived
    #         binary_tree = binary_tree.base_class_object
    #         dissection = Closure().closure(binary_tree)
    #         return LDerivedClass(LDerivedClass(dissection))
    #     dissection = Closure().closure(binary_tree)
    #     return LDerivedClass(dissection)
    # else:
    #     # not derived
    #     return Closure().closure(binary_tree)



def add_random_root_edge(decomp):
    """From ((L, U), dissection) or (U, dissection) to IrreducibleDissection."""
    if isinstance(decomp, ProdClass):
        dissection = decomp.second
    else:
        dissection = decomp
    dissection = dissection.underive_all()
    # TODO find out if this random rooting is actually necessary
    dissection.root_at_random_hexagonal_edge()
    return dissection


def is_admissible(dissection):
    """Admissibility check for usage in the grammar."""
    return dissection.is_admissible

def irreducible_dissection_grammar():
    """Builds the dissection grammar. Must still be initialized with init().

    Returns
    -------
    DecompositionGrammar
        The grammar for sampling from J_a and J_a_dx.
    """

    # Some shorthands to keep the grammar readable.
    L = LAtomSampler
    U = UAtomSampler
    K = AliasSampler('K')
    K_dx = AliasSampler('K_dx')
    K_dx_dx = AliasSampler('K_dx_dx')
    I = AliasSampler('I')
    I_dx = AliasSampler('I_dx')
    I_dx_dx = AliasSampler('I_dx_dx')
    J = AliasSampler('J')
    J_dx = AliasSampler('J_dx')
    J_dx_dx = AliasSampler('J_dx_dx')
    Bij = BijectionSampler
    Rej = RejectionSampler

    grammar = DecompositionGrammar()
    # This grammar depends on the binary tree grammar so we add it.
    grammar.rules = binary_tree_grammar().rules
    EarlyRejectionControl.grammar = grammar

    grammar.rules = {

        # Non-derived dissections (standard, rooted, admissible).

        'I': Bij(K, closure),

        # We drop the 3*L*U factor here.
        # This bijection does not preserve l-size/u-size.
        'J': Bij(I, add_random_root_edge),

        'J_a': Rej(J, is_admissible),

        # Derived dissections.

        # The result is not a derived class, the bijection does not preserve l-size.
        'I_dx': Bij(K_dx, closure),

        # We drop the factor 3*U.
        # This bijection does not preserve l-size/u-size.
        'J_dx': Bij(I + L() * I_dx, add_random_root_edge),

        'J_a_dx': Rej(J_dx, is_admissible),

        # Bi-derived dissections.

        # Does not preserve l-size, result is not a derived class.
        'I_dx_dx': Bij(K_dx_dx, closure),

        # We dropped a factor.
        'J_dx_dx': Bij(2 * I_dx + L() * I_dx_dx, add_random_root_edge),

        'J_a_dx_dx': Rej(J_dx_dx, is_admissible)

    }
    return grammar


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from planar_graph_sampler.evaluations_planar_graph import *
    from timeit import default_timer as timer


    oracle = EvaluationOracle(my_evals_100)
    BoltzmannSamplerBase.oracle = oracle
    BoltzmannSamplerBase.debug_mode = False

    grammar = irreducible_dissection_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'J_a'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    try:
        print("expected avg. size: {}\n".format(oracle.get_expected_l_size(sampled_class, symbolic_x, symbolic_y)))
    except BoltzmannFrameworkError:
        pass

    # random.seed(0)
    # boltzmann_framework_random_gen.seed(3)

    # l_sizes = []
    # i = 0
    # samples = 10000
    # start = timer()
    # while i < samples:
    #     obj = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
    #     l_sizes.append(obj.l_size)
    #     i += 1
    # end = timer()
    # print()
    # print("avg. size: {}".format(sum(l_sizes) / len(l_sizes)))
    # print("time: {}".format(end - start))


    while True:
        tree = grammar.sample_iterative('K', symbolic_x, symbolic_y)
        if tree.l_size == 1:
            print(tree)
            print(tree.half_edge.node_nr)
            tree = tree.underive_all()
            assert tree.is_consistent
            tree.plot(with_labels=True, use_planar_drawer=False, node_size=50, draw_leaves=False)
            plt.show()

            diss = closure(tree)
            print(diss)
            print(diss.half_edge.node_nr)
            diss.root_at_random_hexagonal_edge()
            print(diss.is_admissible)
            diss.plot(with_labels=True, use_planar_drawer=False, node_size=50)

            plt.show()

    # num_samples = 100
    # samples = []
    # l_size = 20
    # i = 0
    # while i < num_samples:
    #     diss = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
    #     if diss.l_size == l_size:
    #         i += 1
    #         samples.append(diss)
    #
    # admissible = len([diss for diss in samples if diss.is_admissible])
    # print(admissible / num_samples)
