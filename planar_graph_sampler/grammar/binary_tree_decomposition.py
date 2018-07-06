from framework.evaluation_oracle import EvaluationOracle
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.generic_samplers import *
from framework.utils import bern

from planar_graph_sampler.bijections.binary_tree_builders import WhiteRootedBinaryTreeBuilder, \
    BlackRootedBinaryTreeBuilder
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100


def binary_tree_grammar():
    """
    Builds the bicolored binary tree grammar. Must still be initialized with init().

    :return: The grammar for sampling K and K_dx.
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
    DxFromDy = LDerFromUDerSampler

    grammar = DecompositionGrammar()
    # Add the decomposition rules.
    grammar.add_rules({

        'K': Rej(K_dy, lambda gamma: bern(2 / (gamma.get_u_size() + 1))),  # See section 4.1.6. for this rejection.

        'K_dx': DxFromDy(K_dy, alpha_l_u=2 / 3),

        'K_dy': R_b_as + R_w_as,

        'R_b_as': R_w * L() * U() + U() * L() * R_w + R_w * L() * R_w,

        'R_w_as': R_b_head * U() + U() * R_b_head + R_b ** 2,

        'R_b_head': R_w_head * L() * R_b_head_help + R_b_head_help * L() * R_w_head + R_w_head * L() * R_w_head,

        'R_b_head_help': U() * U(),

        'R_w_head': U() + R_b * U() + U() * R_b + R_b ** 2,

        'R_b': (U() + R_w) * L() * (U() + R_w),

        'R_w': (U() + R_b) * (U() + R_b),

    })
    # Set builder information.
    grammar.set_builder(['R_w', 'R_w_head', 'R_w_as', 'R_b_head_help'], WhiteRootedBinaryTreeBuilder())
    grammar.set_builder(['R_b', 'R_b_head', 'R_b_as'], BlackRootedBinaryTreeBuilder())

    # Note that we do not init the grammar here.
    return grammar


if __name__ == '__main__':
    BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)
    grammar = binary_tree_grammar()
    grammar.init()

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'

    print("Needed oracle entries:")
    [print(query) for query in sorted(grammar.collect_oracle_queries('K_dy', symbolic_x, symbolic_y))]

    tree = grammar.sample('K_dy', symbolic_x, symbolic_y)

    print("Black nodes: {}".format(tree.get_l_size()))
    print("Total leaves: {}".format(tree.get_u_size()))
    print("Root Node {}".format(tree.get_root()))

    import matplotlib.pyplot as plt

    tree.plot()
    plt.show()
