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
import math

from framework.class_builder import CombinatorialClassBuilder, DummyBuilder
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.generic_samplers import *
from framework.generic_samplers import BoltzmannSamplerBase
from framework.utils import bern

from planar_graph_sampler.grammar.grammar_utils import divide_by_2, underive, to_l_derived_class, to_u_derived_class


def to_K_dy(dummy):
    dummy._u_size += 1
    return UDerivedClass(dummy)


# def underive(dummy):
#     dummy._l_size += 1
#     return dummy
#
#
# def to_u_derived_class(dummy):
#     dummy._u_size -= 1
#     return dummy
#
#
# def to_l_derived_class(dummy):
#     dummy._l_size -= 1
#     return dummy


def dummy_sampling_grammar():
    """Returns the adapted grammar for sampling dummies.

    This is useful for making experiments about the sizes of the objects output by the sampler.
    The grammar still needs to be initialized and set to dummy sampling mode.
    """
    # Some general shortcuts to make the grammar more readable.
    L = LAtomSampler()
    U = UAtomSampler()
    Z = ZeroAtomSampler()
    Set = SetSampler
    USubs = USubsSampler
    LSubs = LSubsSampler
    Bij = BijectionSampler
    Rej = RejectionSampler
    Trans = TransformationSampler
    DxFromDy = LDerFromUDerSampler
    DyFromDx = UDerFromLDerSampler
    Hook = HookSampler

    grammar = DecompositionGrammar()

    # Binary trees.

    class NodeCounter(object):
        L = 0

        @staticmethod
        def reset():
            NodeCounter.L = 0

    class ModifiedDummyBuilder(DummyBuilder):

        activate_rejection_K = False

        @staticmethod
        def activate_rejection():
            ModifiedDummyBuilder.activate_rejection_K = True

        @staticmethod
        def deactivate_rejection():
            ModifiedDummyBuilder.activate_rejection_K = False

        def __init__(self, grammar):
            self._grammar = grammar

        def u_atom(self):
            if ModifiedDummyBuilder.activate_rejection_K:
                NodeCounter.L += 1
                L = NodeCounter.L
                if L > 1 and not bern(L / (L + 1)):
                    self._grammar.restart_sampler()
            return DummyClass(u_size=1)

    K_dy = AliasSampler('K_dy')
    R_b = AliasSampler('R_b')
    R_w = AliasSampler('R_w')
    R_b_as = AliasSampler('R_b_as')
    R_w_as = AliasSampler('R_w_as')
    R_b_head = AliasSampler('R_b_head')
    R_w_head = AliasSampler('R_w_head')

    K_dy_dx = AliasSampler('K_dy_dx')
    R_b_dx = AliasSampler('R_b_dx')
    R_w_dx = AliasSampler('R_w_dx')
    R_b_as_dx = AliasSampler('R_b_as_dx')
    R_w_as_dx = AliasSampler('R_w_as_dx')
    R_b_head_dx = AliasSampler('R_b_head_dx')
    R_w_head_dx = AliasSampler('R_w_head_dx')

    def rej_to_K(u_derived_tree):
        # return bern(2 / (u_derived_tree.u_size + 1))
        return True

    def rej_is_assymetric(dummy):
        return dummy._u_size != 2 and (dummy._u_size != 5 or dummy._l_size != 1)
        # return True

    def rej_K_dy_to_K_dx(dummy):
        return bern(1.5 * dummy._l_size / (dummy._u_size + 1))

    def bij_to_l_derived(dummy):
        dummy._l_size -= 1
        return dummy

    def bij_underive_dy(dummy):
        dummy._u_size += 1
        return dummy

    binary_tree_rules = {

        # Underived and derived binary trees.

        'K':
            Hook(
                Trans(
                    K_dy,
                    bij_underive_dy
                ),
                before=ModifiedDummyBuilder.activate_rejection,
                after=ModifiedDummyBuilder.deactivate_rejection
            ),

        # This sampler seems to be about half as fast as the one for K_dy (due to the rejection)
        # So it looks like this invokes K_dy twice on average
        'K_dx':
            Bij(
                Rej(
                    K_dy,
                    rej_K_dy_to_K_dx
                ),
                bij_to_l_derived
            ),

        # I measured that the more complicated grammar is about 10 - 15% faster than this rejection !
        # (For values of size 10000)
        'K_dy':
            RestartableSampler(
                Hook(
                    R_b_as + R_w_as,
                    NodeCounter.reset
                ),
            ),

        'R_b_as':
            2 * R_w * L * U + R_w ** 2 * L,

        'R_w_as':
            2 * R_b_head * U + R_b ** 2,

        'R_b_head':
            2 * R_w_head * L * U ** 2 + R_w_head ** 2 * L,

        'R_w_head':
            U + 2 * R_b * U + R_b ** 2,

        'R_b':
            L * (U + R_w) ** 2,

        'R_w':
            (U + R_b) ** 2,

        # Bi-derived binary trees.

        'K_dx_dx':
            Bij(
                Rej(
                    K_dy_dx,
                    rej_K_dy_to_K_dx
                ),
                bij_to_l_derived
            ),

        'K_dy_dx':
            R_b_as_dx + R_w_as_dx,

        'R_b_as_dx':
            2 * U * (R_w_dx * L + R_w) + 2 * R_w * R_w_dx * L + R_w ** 2,

        'R_w_as_dx':
            2 * R_b_head_dx * U + 2 * R_b * R_b_dx,

        'R_b_head_dx':
            2 * U ** 2 * (R_w_head_dx * L + R_w_head) + 2 * R_w_head * R_w_head_dx * L + R_w_head ** 2,

        'R_w_head_dx':
            2 * R_b_dx * U + 2 * R_b * R_b_dx,

        'R_b_dx':
            (U + R_w) ** 2 + 2 * R_w_dx * L * (U + R_w),

        'R_w_dx':
            2 * (U + R_b) * R_b_dx

    }

    grammar.rules = binary_tree_rules

    # Irreducible dissection.

    K = AliasSampler('K')
    K_dx = AliasSampler('K_dx')
    K_dx_dx = AliasSampler('K_dx_dx')
    I = AliasSampler('I')
    I_dx = AliasSampler('I_dx')
    I_dx_dx = AliasSampler('I_dx_dx')
    J = AliasSampler('J')
    J_dx = AliasSampler('J_dx')
    J_a = AliasSampler('J_a')
    J_a_dx = AliasSampler('J_a_dx')
    J_dx_dx = AliasSampler('J_dx_dx')
    J_a_dx_dx = AliasSampler('J_a_dx_dx')

    irreducible_dissection_rules = {

        # Non-derived dissections (standard, rooted, admissible).

        'I': K,

        'J': 3 * L * U * I,

        # Using only dummies we cannot make the admissibility check as it depends on internal structure. Based on
        # experiments however, we conjecture that the admissibility of an object in J is "almost" independent of its
        # size. Ignoring the check, we get an average size which is ~4% too small (for values N=100)
        # We also measured that the success probability seems to be around 20% only. So this rejection is quite costly.
        'J_a': Trans(J),

        # Derived dissections.

        'I_dx': K_dx,

        'J_dx':
            3 * U * (I + L * I_dx),

        'J_a_dx': J_dx,

        # Bi-derived dissections.

        'I_dx_dx': K_dx_dx,

        'J_dx_dx': 3 * U * I_dx + 3 * U * I_dx + 3 * L * U * I_dx_dx,

        'J_a_dx_dx': J_dx_dx,

    }

    grammar.rules = irreducible_dissection_rules

    # 3-connected planar graphs.

    G_3_arrow = AliasSampler('G_3_arrow')
    G_3_arrow_dy = AliasSampler('G_3_arrow_dy')
    G_3_arrow_dx = AliasSampler('G_3_arrow_dx')
    G_3_arrow_dx_dx = AliasSampler('G_3_arrow_dx_dx')
    G_3_arrow_dx_dy = AliasSampler('G_3_arrow_dx_dy')
    G_3_arrow_dy_dy = AliasSampler('G_3_arrow_dy_dy')

    M_3_arrow = AliasSampler('M_3_arrow')
    M_3_arrow_dx = AliasSampler('M_3_arrow_dx')
    M_3_arrow_dx_dx = AliasSampler('M_3_arrow_dx_dx')

    def rej_G_3_arrow_dx_to_dy(dummy):
        return bern(1 / 3 * dummy._u_size / (dummy._l_size + 1))  # todo check this

    three_connected_rules = {

        # Non-derived 3-connected rooted planar maps/graphs.

        'M_3_arrow': J_a,  # primal map

        'G_3_arrow': Trans(M_3_arrow, eval_transform=divide_by_2),  # See 4.1.9.

        # Derived 3-connected rooted planar maps/graphs.

        'M_3_arrow_dx': J_a_dx,

        'G_3_arrow_dx': Trans(M_3_arrow_dx, eval_transform=divide_by_2),

        'G_3_arrow_dy': Rej(G_3_arrow_dx, rej_G_3_arrow_dx_to_dy),  # See 5.3.3.

        # Bi-derived 3-connected rooted planar maps/graphs.

        'M_3_arrow_dx_dx': J_a_dx_dx,

        'G_3_arrow_dx_dx': Trans(M_3_arrow_dx_dx, eval_transform=divide_by_2),

        'G_3_arrow_dx_dy': Rej(G_3_arrow_dx_dx, rej_G_3_arrow_dx_to_dy),

        'G_3_arrow_dy_dy': Rej(G_3_arrow_dx_dy, rej_G_3_arrow_dx_to_dy),

    }

    grammar.rules = three_connected_rules

    # Networks.

    D = AliasSampler('D')
    S = AliasSampler('S')
    P = AliasSampler('P')
    H = AliasSampler('H')
    D_dx = AliasSampler('D_dx')
    S_dx = AliasSampler('S_dx')
    P_dx = AliasSampler('P_dx')
    H_dx = AliasSampler('H_dx')
    D_dx_dx = AliasSampler('D_dx_dx')
    S_dx_dx = AliasSampler('S_dx_dx')
    P_dx_dx = AliasSampler('P_dx_dx')
    H_dx_dx = AliasSampler('H_dx_dx')

    network_rules = {

        # networks

        'D': U + S + P + H,

        'S': (U + P + H) * L * D,

        'P': U * Set(1, S + H) + Set(2, S + H),

        'H': USubs(G_3_arrow, D),

        # l-derived networks

        'D_dx': S_dx + P_dx + H_dx,

        'S_dx': (P_dx + H_dx) * L * D + (U + P + H) * (D + L * D_dx),

        'P_dx': U * (S_dx + H_dx) * Set(0, S + H) + (S_dx + H_dx) * Set(1, S + H),

        'H_dx': USubs(G_3_arrow_dx, D) + D_dx * USubs(G_3_arrow_dy, D),

        # bi-l-derived networks

        'D_dx_dx':
            S_dx_dx + P_dx_dx + H_dx_dx,

        'S_dx_dx':
            (P_dx_dx + H_dx_dx) * L * D
            + 2 * (P_dx + H_dx) * (D + L * D_dx)
            + (U + P + H) * (2 * D_dx + L * D_dx_dx),

        'P_dx_dx':
            U * ((S_dx_dx + H_dx_dx) * Set(0, S + H)
            + U * (S_dx + H_dx) ** 2 * Set(0, S + H))
            + (S_dx_dx + H_dx_dx) * Set(1, S + H)
            + (S_dx + H_dx) ** 2 * Set(0, S + H),

        'H_dx_dx':
            USubs(G_3_arrow_dx_dx, D) + D_dx * USubs(G_3_arrow_dx_dy, D)
            + D_dx_dx * USubs(G_3_arrow_dy, D)
            + D_dx * USubs(G_3_arrow_dx_dy, D) + D_dx**2 * USubs(G_3_arrow_dy_dy, D)

    }

    grammar.rules = network_rules

    # Set default dummy builder in all rules.
    grammar.dummy_sampling_mode()
    # In binary tree rules set modified builder for the early rejection.
    grammar.set_builder(
        ['R_b', 'R_b_head', 'R_b_as', 'R_w', 'R_w_head', 'R_w_as', 'R_b_dx', 'R_b_head_dx', 'R_b_as_dx', 'R_w_dx',
         'R_w_head_dx', 'R_w_as_dx'],
        ModifiedDummyBuilder(grammar)
    )

    return grammar


if __name__ == "__main__":
    from framework.evaluation_oracle import EvaluationOracle
    from planar_graph_sampler.evaluations_planar_graph import *
    from framework.utils import boltzmann_framework_random_gen
    from timeit import default_timer as timer

    # oracle = EvaluationOracle(planar_graph_evals[10000])
    oracle = EvaluationOracle(my_evals_100)
    BoltzmannSamplerBase.oracle = oracle
    BoltzmannSamplerBase.debug_mode = False

    grammar = dummy_sampling_grammar()
    grammar.init()
    # grammar.dummy_sampling_mode()
    # symbolic_x = 'x'
    symbolic_y = 'y'
    symbolic_x = 'x*G_1_dx(x,y)'
    # symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'D_dx_dx'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    try:
        print("expected: {}\n".format(oracle.get_expected_l_size(sampled_class, symbolic_x, symbolic_y)))
    except BoltzmannFrameworkError:
        pass

    # random.seed(0)
    # boltzmann_framework_random_gen.seed(0)

    l_sizes = []
    i = 0
    samples = 100
    start = timer()
    while i < samples:
        dummy = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
        l_sizes.append(dummy.l_size)
        i += 1
    end = timer()
    print()
    print()
    print("avg. size: {}".format(sum(l_sizes) / len(l_sizes)))
    print("time: {}".format(end - start))

    # while True:
    #     dummy = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
    #     if dummy.l_size > 100:
    #         print(dummy.u_size / dummy.l_size )
