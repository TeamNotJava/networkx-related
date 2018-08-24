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
from framework.generic_samplers import BoltzmannSamplerBase
from framework.utils import bern

from planar_graph_sampler.grammar.grammar_utils import underive, to_u_derived_class, divide_by_2, to_l_derived_class


def to_K_dy(dummy):
    dummy._u_size += 1
    return UDerivedClass(dummy)

def dummy_sampling_grammar():
    """Returns the adapted grammar for sampling dummies.

    This is useful for making experiments about the sizes of the objects output by the sampler.
    The grammar still needs to be initialized and set to dummy sampling mode.
    """
    # Some general shortcuts to make the grammar more readable.
    Z = ZeroAtomSampler
    L = LAtomSampler
    U = UAtomSampler
    Set = SetSampler
    LSubs = LSubsSampler
    USubs = USubsSampler
    Bij = BijectionSampler
    Rej = RejectionSampler
    Trans = TransformationSampler
    DxFromDy = LDerFromUDerSampler
    DyFromDx = UDerFromLDerSampler

    # Binary trees.

    K_dy = AliasSampler('K_dy')
    R_b_as = AliasSampler('R_b_as')
    R_w_as = AliasSampler('R_w_as')
    R_b_head = AliasSampler('R_b_head')
    R_b_head_help = AliasSampler('R_b_head_help')
    R_w_head = AliasSampler('R_w_head')
    R_b = AliasSampler('R_b')
    R_w = AliasSampler('R_w')

    def rej_to_K(u_derived_tree):
        return bern(2 / (u_derived_tree.u_size + 1))

    binary_tree_rules = {

        'K': Bij(Rej(K_dy, rej_to_K), underive),  # See 4.1.6.

        'K_dx': DxFromDy(K_dy, alpha_l_u=2 / 3),

        'K_dy': Bij(R_b_as + R_w_as, to_K_dy),

        'R_b_as': R_w * L() * U() + U() * L() * R_w + R_w * L() * R_w,

        'R_w_as': R_b_head * U() + U() * R_b_head + R_b ** 2,

        'R_b_head': R_w_head * L() * R_b_head_help + R_b_head_help * L() * R_w_head + R_w_head * L() * R_w_head,

        'R_b_head_help': U() * U(),

        'R_w_head': U() + R_b * U() + U() * R_b + R_b ** 2,

        'R_b': (U() + R_w) * L() * (U() + R_w),

        'R_w': (U() + R_b) * (U() + R_b),

    }

    # Irreducible dissection.

    K = AliasSampler('K')
    K_dx = AliasSampler('K_dx')
    I = AliasSampler('I')
    I_dx = AliasSampler('I_dx')
    J = AliasSampler('J')
    J_dx = AliasSampler('J_dx')
    J_a = AliasSampler('J_a')
    J_a_dx = AliasSampler('J_a_dx')

    def admissible_approx(dissection):
        # a dissection with 5 or less inner faces (tree with <=5 leaves) can't be admissible
        # because there is an internal path with 3 edges from any outer black node to its opposite white node
        return dissection.u_size > 5

    irreducible_dissection_rules = {

        'I': K,

        'I_dx': K_dx,

        'J': 3 * L() * U() * I,

        'J_dx': 3 * U() * I + 3 * L() * U() * I_dx,

        'J_a': Rej(J, admissible_approx),

        'J_a_dx': Rej(J_dx, admissible_approx),

    }

    # 3-connected planar graphs.

    G_3_arrow = AliasSampler('G_3_arrow')
    G_3_arrow_dy = AliasSampler('G_3_arrow_dy')
    G_3_arrow_dx = AliasSampler('G_3_arrow_dx')
    M_3_arrow = AliasSampler('M_3_arrow')
    M_3_arrow_dx = AliasSampler('M_3_arrow_dx')

    three_connected_rules = {

        'M_3_arrow': J_a,

        'M_3_arrow_dx': J_a_dx,

        'G_3_arrow': Trans(M_3_arrow, eval_transform=divide_by_2),  # See 4.1.9.

        'G_3_arrow_dx': Trans(M_3_arrow_dx, to_l_derived_class, eval_transform=divide_by_2),

        'G_3_arrow_dy': DyFromDx(G_3_arrow_dx, alpha_u_l=3)  # See 5.3.3.

    }

    # Networks.

    D = AliasSampler('D')
    S = AliasSampler('S')
    P = AliasSampler('P')
    H = AliasSampler('H')
    D_dx = AliasSampler('D_dx')
    S_dx = AliasSampler('S_dx')
    P_dx = AliasSampler('P_dx')
    H_dx = AliasSampler('H_dx')

    network_rules = {

        # networks

        'D': U() + S + P + H,

        'S': (U() + P + H) * L() * D,

        'P': U() * Set(1, S + H) + Set(2, S + H),

        'H': USubs(G_3_arrow, D),

        # l-derived networks

        'D_dx': S_dx + P_dx + H_dx,

        'S_dx': (P_dx + H_dx) * L() * D + (U() + P + H) * (D + L() * D_dx),

        'P_dx': U() * (S_dx + H_dx) * Set(0, S + H) + (S_dx + H_dx) * Set(1, S + H),

        'H_dx': USubs(G_3_arrow_dx, D) + D_dx * USubs(G_3_arrow_dy, D),

    }

    # 2-connected planar graphs.

    G_2_arrow = AliasSampler('G_2_arrow')
    G_2_arrow_dy = AliasSampler('G_2_arrow_dy')
    G_2_arrow_dx = AliasSampler('G_2_arrow_dx')

    G_2_dx = AliasSampler('G_2_dx')
    G_2_dx_dx = AliasSampler('G_2_dx_dx')
    G_2_dy = AliasSampler('G_2_dy')
    G_2_dy_dx = AliasSampler('G_2_dy_dx')
    G_2_dx_dy = AliasSampler('G_2_dx_dy')
    F = AliasSampler('F')
    F_dx = AliasSampler('F_dx')

    def divide_by_1_plus_y(evl, x, y):
        """Needed as an eval-transform for rules G_2_arrow and G_2_arrow_dx."""
        return evl / (1 + BoltzmannSamplerBase.oracle.get(y))

    def to_G_2_dx(decomp):
        g = decomp.second
        if isinstance(g, LDerivedClass):
            g = g.base_class_object
        return LDerivedClass(g)

    two_connected_rules = {

        # two connected

        'G_2_arrow': Trans(Z() + D, eval_transform=divide_by_1_plus_y),  # see 5.5

        'F': L() ** 2 * G_2_arrow,

        'G_2_dy': Trans(F, to_u_derived_class, eval_transform=divide_by_2),

        'G_2_dx': DxFromDy(G_2_dy, alpha_l_u=2.0),  # see p. 26

        # l-derived two connected

        'G_2_arrow_dx': Trans(D_dx, to_l_derived_class, eval_transform=divide_by_1_plus_y),

        'F_dx': Bij(L() ** 2 * G_2_arrow_dx + 2 * L() * G_2_arrow, to_G_2_dx),

        'G_2_dx_dy': Trans(F_dx, to_u_derived_class, eval_transform=divide_by_2),

        'G_2_dx_dx': DxFromDy(G_2_dx_dy, alpha_l_u=1.0),  # see 5.5

    }

    # Connected planar graphs.

    G_1 = AliasSampler('G_1')
    G_1_dx = AliasSampler('G_1_dx')
    G_1_dx_dx = AliasSampler('G_1_dx_dx')

    def rej_to_G_1(g):
        return bern(1 / (g.l_size + 1))

    connected_rules = {

        'G_1_dx': Set(0, LSubs(G_2_dx, L() * G_1_dx)),

        # 'G_1_dx_dx_helper': Bij((G_1_dx + L() * G_1_dx_dx) * LSubs(G_2_dx_dx, L() * G_1_dx), subs_marked_vertex),

        'G_1_dx_dx': (G_1_dx + L() * G_1_dx_dx) * LSubs(G_2_dx_dx, L() * G_1_dx) * G_1_dx,

        'G_1': Bij(Rej(G_1_dx, rej_to_G_1), underive)  # See lemma 15.

    }

    # Planar graphs.

    G = AliasSampler('G')
    G_dx = AliasSampler('G_dx')

    planar_graphs_rules = {

        'G': SetSampler(0, G_1),

        'G_dx': G_1_dx * G,

        'G_dx_dx': G_1_dx_dx * G + G_1_dx * G_dx,

    }

    grammar = DecompositionGrammar()
    grammar.rules = binary_tree_rules
    grammar.rules = irreducible_dissection_rules
    grammar.rules = three_connected_rules
    grammar.rules = network_rules
    grammar.rules = two_connected_rules
    grammar.rules = connected_rules
    grammar.rules = planar_graphs_rules
    return grammar
