from __future__ import division

from framework.class_builder import CombinatorialClassBuilder
from framework.evaluation_oracle import EvaluationOracle
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.generic_samplers import *
from framework.generic_samplers import BoltzmannSamplerBase
from framework.utils import bern

from planar_graph_sampler.grammar.grammar_utils import underive, to_u_derived_class, Counter
from planar_graph_sampler.combinatorial_classes import BinaryTree
from planar_graph_sampler.combinatorial_classes.binary_tree import Leaf
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100, planar_graph_evals_n1000


class WhiteRootedBinaryTreeBuilder(CombinatorialClassBuilder):
    """
    Builds white-rooted binary trees (rules 'R_w', 'R_w_head', 'R_w_as').
    The builder is in the same file as the grammar it belongs to because it is quite closely connected.
    """

    def __init__(self):
        self._counter = Counter()

    def u_atom(self):
        """A u-atom is a leaf."""
        return Leaf()

    def product(self, lhs, rhs):
        res = BinaryTree('white')
        res.set_root_node_nr(next(self._counter))
        res.add_left_child(lhs)
        res.add_right_child(rhs)
        return res


class BlackRootedBinaryTreeBuilder(CombinatorialClassBuilder):
    """
    Builds black-rooted binary trees (rules 'R_b', 'R_b_head', 'R_b_head_help', 'R_b_as').
    The builder is in the same file as the grammar it belongs to because it is quite closely connected.
    """

    def __init__(self):
        self._counter = Counter()

    def l_atom(self):
        """An l-atom is a black rooted tree without children."""
        res = BinaryTree('black')
        res.set_root_node_nr(next(self._counter))
        return res

    def u_atom(self):
        """A u-atom is a leaf."""
        return Leaf()

    def product(self, lhs, rhs):
        """"""
        res = None
        if lhs.is_leaf:
            # rhs is not a leaf.
            assert rhs.is_black_rooted
            rhs.add_left_child(lhs)
            res = rhs
        elif rhs.is_leaf:
            # lhs is not a leaf.
            res = self.product(rhs, lhs).flip()
        elif lhs.is_white_rooted and rhs.is_black_rooted:
            # Both are not leaves.
            rhs.add_left_child(lhs)
            res = rhs
        elif rhs.is_white_rooted and lhs.is_black_rooted:
            res = self.product(rhs, lhs).flip()
        # Notice that these are the only possible cases.
        # This is because of the way in which the grammar is written down.
        assert res is not None
        assert res.root_color is 'black'
        return res


def rej_to_K(u_derived_tree):
    return bern(2 / (u_derived_tree.u_size + 1))


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

        # See section 4.1.6. for this rejection.
        'K': Bij(Rej(K_dy, rej_to_K), underive),

        'K_dx': DxFromDy(K_dy, alpha_l_u=2 / 3),

        'K_dy': Bij(R_b_as + R_w_as, to_u_derived_class),

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
    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n1000)
    BoltzmannSamplerBase.debug_mode = True

    grammar = binary_tree_grammar()
    grammar.init()
    # grammar.dummy_sampling_mode()

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'K'

    print("Expected size of K: {}".format(BoltzmannSamplerBase.oracle.get_expected_l_size('K', symbolic_x, symbolic_y)))

    while True:
        try:
            tree = grammar.sample(sampled_class, symbolic_x, symbolic_y)
        except RecursionError:
            pass
        if tree.l_size > 0:
            print(tree)
            assert tree.is_consistent

            import matplotlib.pyplot as plt

            tree.plot(draw_leaves=True, node_size=50)
            plt.show()

    c = [0, 0, 0, 0, 0, 0, 0]
    samples = 100000
    i = 0
    while i < samples:
        try:
            tree = grammar.sample(sampled_class, symbolic_x, symbolic_y)
        except RecursionError:
            pass
        if tree.l_size() == l_size:
            assert tree.is_consistent()
            c[tree.u_size()] += 1
            i += 1
    print(c)
    a = BoltzmannSampler.oracle.get_probability(sampled_class, symbolic_x, symbolic_y, l_size, 3)
    b = BoltzmannSampler.oracle.get_probability(sampled_class, symbolic_x, symbolic_y, l_size, 4)
    print(a / (a + b))
    print(b / (a + b))
