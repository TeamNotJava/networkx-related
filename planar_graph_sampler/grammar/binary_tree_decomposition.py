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


class EarlyRejectionControl:
    """
    Needed to implement the early rejection for class K.
    Holds some global variables to control the process.
    """

    rejection_activated = False  # Indicates if the early rejection is activated.
    L = 0  # Number of leaves generated so far.
    grammar = None  # A reference to the grammar for the sampler interrupt.

    @staticmethod
    def activate_rejection():
        EarlyRejectionControl.rejection_activated = True

    @staticmethod
    def deactivate_rejection():
        EarlyRejectionControl.rejection_activated = False

    @staticmethod
    def reset():
        EarlyRejectionControl.L = 0


class BinaryTreeBuilder(DefaultBuilder):
    """Common base class for black- and white-rooted binary tree builders."""

    def __init__(self):
        self._counter = Counter()  # Counter for node numbers.

    def u_atom(self):
        # A u-atom is a leaf.
        if EarlyRejectionControl.rejection_activated:
            EarlyRejectionControl.L += 1
            L = EarlyRejectionControl.L
            if L > 1 and not bern(L / (L + 1)):
                EarlyRejectionControl.grammar.restart_sampler()
        return Leaf()


class WhiteRootedBinaryTreeBuilder(BinaryTreeBuilder):
    """Builds white-rooted binary trees (rules 'R_w', 'R_w_head', 'R_w_as', 'R_b_head_help')."""

    def product(self, lhs, rhs):
        # Builds white-rooted tree from decomposition of the form (leaf|black)(leaf|black)
        res = BinaryTree('white')
        res.set_root_node_nr(next(self._counter))
        res.add_left_child(lhs)
        res.add_right_child(rhs)
        return res


class BlackRootedBinaryTreeBuilder(BinaryTreeBuilder):
    """Builds black-rooted binary trees (rules 'R_b', 'R_b_head', 'R_b_as')."""

    def l_atom(self):
        # An l-atom is a black rooted tree without children.
        res = BinaryTree('black')
        res.set_root_node_nr(next(self._counter))
        return res

    def u_atom(self):
        # A u-atom is a leaf.
        return Leaf()

    def product(self, lhs, rhs):
        # Builds black rooted tree from decompositions of the form
        # (1) black(leaf|white) or (2) (leaf|white)black or (3) (leaf|white)(leaf|white)
        if not lhs.is_leaf and lhs.is_black_rooted:
            # Form (1)
            lhs.add_right_child(rhs)
            res = lhs
        elif not rhs.is_leaf and rhs.is_black_rooted:
            # Form (2)
            rhs.add_left_child(lhs)
            res = rhs
        else:
            # Form (3)
            res = BinaryTree('black')
            res.set_root_node_nr(next(self._counter))
            res.add_left_child(lhs)
            res.add_right_child(rhs)
        return res


def rej_to_K(u_derived_tree):
    return bern(2 / (u_derived_tree.u_size + 1))


def to_K_dy(tree):
    tree.leaves_count += 1
    return UDerivedClass(tree)

def get_base_class(obj):
    return obj.base_class_object


def to_K_dy_dx(tree):
    # TODO In fact K_dx_dy, notation a bit messed up here
    tree.leaves_count += 1
    tree = LDerivedClass(tree)
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
    K_dy_dx = AliasSampler('K_dy_dx')
    R_b_dx = AliasSampler('R_b_dx')
    R_w_dx = AliasSampler('R_w_dx')
    R_b_as_dx = AliasSampler('R_b_as_dx')
    R_w_as_dx = AliasSampler('R_w_as_dx')
    R_b_head_dx = AliasSampler('R_b_head_dx')
    R_w_head_dx = AliasSampler('R_w_head_dx')
    Bij = BijectionSampler
    Trans = TransformationSampler
    Hook = HookSampler
    DxFromDy = LDerFromUDerSampler

    grammar = DecompositionGrammar()

    # Add the decomposition rules.
    grammar.rules = {

        # Underived and derived binary trees.

        'K':
            Hook(
                Trans(
                    K_dy,
                    underive
                ),
                before=EarlyRejectionControl.activate_rejection,
                after=EarlyRejectionControl.deactivate_rejection
            ),  # See 4.1.6.

        'K_dx':
            DxFromDy(
                K_dy,
                alpha_l_u=2 / 3  # See 5.3.1.
            ),

        'K_dy':
            RestartableSampler(
                Hook(
                    Bij(
                        R_b_as + R_w_as,
                        to_K_dy
                    ),
                    EarlyRejectionControl.reset  # Reset leaf-counter before sampling from this rule.
                ),
            ),

        'R_b_as':
            R_w * L() * U()
            + U() * L() * R_w
            + R_w * L() * R_w,

        'R_w_as':
            R_b_head * U()
            + U() * R_b_head
            + R_b ** 2,

        'R_b_head':
            R_w_head * L() * R_b_head_help
            + R_b_head_help * L() * R_w_head
            + R_w_head * L() * R_w_head,

        'R_b_head_help':
            U() * U(),

        'R_w_head':
            U()
            + R_b * U()
            + U() * R_b
            + R_b ** 2,

        'R_b':
            (U() + R_w) * L() * (U() + R_w),

        'R_w':
            (U() + R_b) ** 2,

        # Bi-derived binary trees.

        'K_dx_dx':
            DxFromDy(
                K_dy_dx,
                alpha_l_u=2 / 3  # See 5.3.1, 2/3 is also valid for K_dx.
            ),

        'K_dy_dx':
            Bij(
                R_b_as_dx + R_w_as_dx,
                to_K_dy_dx
            ),

        'R_b_as_dx':
            U() * L() * R_w_dx
            + R_w_dx * L() * U()
            + R_w * L() * R_w_dx
            + R_w_dx * L() * R_w
            + U() * R_w
            + R_w * U()
            + R_w ** 2,

        'R_w_as_dx':
            R_b_head_dx * U()
            + U() * R_b_head_dx
            + R_b * R_b_dx
            + R_b_dx * R_b,

        'R_b_head_dx':
            R_b_head_help * L() * R_w_head_dx
            + R_w_head_dx * L() * R_b_head_help
            + R_w_head * L() * R_w_head_dx
            + R_w_head_dx * L() * R_w_head
            + R_w_head * R_b_head_help
            + R_b_head_help * R_w_head
            + R_w_head ** 2,

        'R_w_head_dx':
            R_b_dx * (R_b + U())
            + (R_b + U()) * R_b_dx,  # is the same as R_w_dx!

        'R_b_dx':
            (U() + R_w) ** 2
            + R_w_dx * L() * (U() + R_w)
            + (U() + R_w) * L() * R_w_dx,

        'R_w_dx':
            R_b_dx * (U() + R_b)
            + (U() + R_b) * R_b_dx,

    }

    # Set builders.
    grammar.set_builder(['R_w', 'R_w_head', 'R_w_as', 'R_b_head_help',
                         'R_w_dx', 'R_w_head_dx', 'R_w_as_dx'], WhiteRootedBinaryTreeBuilder())
    grammar.set_builder(['R_b', 'R_b_head', 'R_b_as',
                         'R_b_dx', 'R_b_head_dx', 'R_b_as_dx'], BlackRootedBinaryTreeBuilder())

    # Set the grammar in the early rejection control variables.
    EarlyRejectionControl.grammar = grammar

    # We do not init the grammar here.
    return grammar


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from planar_graph_sampler.evaluations_planar_graph import *
    from timeit import default_timer as timer

    oracle = EvaluationOracle(my_evals_100)
    BoltzmannSamplerBase.oracle = oracle
    BoltzmannSamplerBase.debug_mode = False

    grammar = binary_tree_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'K'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    try:
        print("expected: {}\n".format(oracle.get_expected_l_size(sampled_class, symbolic_x, symbolic_y)))
    except BoltzmannFrameworkError:
        pass

    # random.seed(0)
    # boltzmann_framework_random_gen.seed(0)

    l_sizes = []
    i = 0
    samples = 1000
    start = timer()
    while i < samples:
        tree = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
        if tree.l_size < 0:
            print(tree.l_size)
            tree = tree.underive_all()
            tree.plot()
            plt.show()
        l_sizes.append(tree.l_size)
        i += 1
    end = timer()
    print()
    print()
    print("avg. size: {}".format(sum(l_sizes) / len(l_sizes)))
    print("time: {}".format(end - start))
