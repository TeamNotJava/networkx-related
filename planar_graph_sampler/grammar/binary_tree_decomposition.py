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
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.generic_samplers import *
from framework.generic_samplers import BoltzmannSamplerBase
from framework.utils import bern

from planar_graph_sampler.grammar.grammar_utils import underive, Counter
from planar_graph_sampler.combinatorial_classes import BinaryTree
from planar_graph_sampler.combinatorial_classes.binary_tree import Leaf


class WhiteRootedBinaryTreeBuilder(DefaultBuilder):
    """
    Builds white-rooted binary trees (rules 'R_w', 'R_w_head', 'R_w_as', 'R_b_head_help').
    """

    def __init__(self):
        self._counter = Counter()

    def u_atom(self):
        # A u-atom is a leaf.
        return Leaf()

    def product(self, lhs, rhs):
        # Builds white-rooted tree from decomposition of the form (leaf|black)(leaf|black)
        res = BinaryTree('white')
        res.set_root_node_nr(next(self._counter))
        res.add_left_child(lhs)
        res.add_right_child(rhs)
        return res


class BlackRootedBinaryTreeBuilder(DefaultBuilder):
    """
    Builds black-rooted binary trees (rules 'R_b', 'R_b_head', 'R_b_as').
    """

    def __init__(self):
        self._counter = Counter()

    def l_atom(self):
        # An l-atom is a black rooted tree without children
        res = BinaryTree('black')
        res.set_root_node_nr(next(self._counter))
        return res

    def u_atom(self):
        # A u-atom is a leaf.
        return Leaf()

    def product(self, lhs, rhs):
        # Builds black rooted tree from decompositions of the form
        # (1) black(leaf|white) or (2) (leaf|white)black.
        if not lhs.is_leaf and lhs.is_black_rooted:
            # Form (1)
            lhs.add_right_child(rhs)
            res = lhs
        else:
            # Form (2)
            rhs.add_left_child(lhs)
            res = rhs
        return res


def rej_to_K(u_derived_tree):
    return bern(2 / (u_derived_tree.u_size + 1))


def to_K_dy(tree):
    tree.leaves_count += 1
    return UDerivedClass(tree)


def binary_tree_grammar():
    """
    Builds the bicolored binary tree grammar. Must still be initialized with init().

    Returns
    -------
    DecompositionGrammar
        The grammar for sampling K and K_dx.
    """

    # Some shorthands to keep the grammar readable.
    L = LAtomSampler
    U = UAtomSampler
    K_dy = AliasSampler('K_dy')
    R_b_as = AliasSampler('R_b_as')
    R_w_as = AliasSampler('R_w_as')
    R_b_head = AliasSampler('R_b_head')
    R_b_head_help = AliasSampler('R_b_head_help')
    R_w_head = AliasSampler('R_w_head')
    R_b = AliasSampler('R_b')
    R_w = AliasSampler('R_w')
    Rej = RejectionSampler
    Bij = BijectionSampler
    DxFromDy = LDerFromUDerSampler

    grammar = DecompositionGrammar()
    # Add the decomposition rules.
    grammar.rules = {

        'K': Bij(Rej(K_dy, rej_to_K), underive),  # See 4.1.6.

        'K_dx': DxFromDy(K_dy, alpha_l_u=2 / 3),  # See 5.3.1

        'K_dy': Bij(R_b_as + R_w_as, to_K_dy),

        'R_b_as': R_w * L() * U() + U() * L() * R_w + R_w * L() * R_w,

        'R_w_as': R_b_head * U() + U() * R_b_head + R_b ** 2,

        'R_b_head': R_w_head * L() * R_b_head_help + R_b_head_help * L() * R_w_head + R_w_head * L() * R_w_head,

        'R_b_head_help': U() * U(),

        'R_w_head': U() + R_b * U() + U() * R_b + R_b ** 2,

        'R_b': (U() + R_w) * L() * (U() + R_w),

        'R_w': (U() + R_b) * (U() + R_b),

    }
    # Set builder information.
    grammar.set_builder(['R_w', 'R_w_head', 'R_w_as', 'R_b_head_help'], WhiteRootedBinaryTreeBuilder())
    grammar.set_builder(['R_b', 'R_b_head', 'R_b_as'], BlackRootedBinaryTreeBuilder())

    # We do not init the grammar here.
    return grammar


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100, planar_graph_evals_n1000

    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    BoltzmannSamplerBase.debug_mode = False

    grammar = binary_tree_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'K_dx'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    # random.seed(0)

    while True:
        try:
            tree = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
            if tree.l_size > 0:
                print(tree)
                tree = tree.underive_all()
                assert tree.is_consistent
                tree.plot(draw_leaves=False, node_size=50)
                plt.show()
        except RecursionError:
            print("Recursion error")
