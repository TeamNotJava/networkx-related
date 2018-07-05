from framework.bijections.binary_tree_builders import WhiteRootedBinaryTreeBuilder, BlackRootedBinaryTreeBuilder
from framework.evaluation_oracle import EvaluationOracle
from framework.evaluations_planar_graph import planar_graph_evals_n100
from framework.decomposition_grammar import AliasSampler
from framework.decomposition_grammar import DecompositionGrammar
from framework.samplers.generic_samplers import *
from framework.utils import bern


def binary_tree_grammar():
    """
    Builds the bicolored binary tree grammar. Must still be initialized with init().

    :return: The grammar for sampling K and K_dx.
    """

    # Some shorthand to keep the grammar readable.
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
    Bij = BijectionSampler
    Rej = RejectionSampler
    DxFromDy = LDerFromUDerSampler
    w_debug = AliasSampler('w_debug')
    b_debug = AliasSampler('b_debug')

    grammar = DecompositionGrammar()
    # Add the decomposition rules.
    grammar.add_rules({

        'K': Rej(K_dy, lambda gamma: bern(2 / (gamma.get_u_size() + 1))), # See section 4.1.6. for this rejection.

        'K_dx': DxFromDy(K_dy, alpha_l_u=2 / 3),

        'K_dy': R_b_as + R_w_as,

        'R_b_as': R_w*L()*U() + U()*L()*R_w + R_w*L()*R_w,

        'R_w_as': R_b_head*U() + U()*R_b_head + R_b**2,

        'R_b_head': R_w_head*L()*R_b_head_help + R_b_head_help*L()*R_w_head + R_w_head*L()*R_w_head,

        'R_b_head_help': U()*U(),

        'R_w_head': U() + R_b*U() + U()*R_b + R_b**2,

        'R_b': (U() + R_w)*L()*(U() + R_w),

        'R_w': (U() + R_b)*(U() + R_b),

        'w_debug': U()*U(),

        'b_debug': w_debug*L()*w_debug,

    })
    # Set builder information.
    grammar.set_builder(['R_w', 'R_w_head', 'R_w_as', 'R_b_head_help', 'w_debug'], WhiteRootedBinaryTreeBuilder())
    grammar.set_builder(['R_b', 'R_b_head', 'R_b_as', 'b_debug'], BlackRootedBinaryTreeBuilder())

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

    tree = grammar.sample('K', symbolic_x, symbolic_y)

    print("Black nodes: {}".format(tree.get_l_size()))
    print("Total leaves: {}".format(tree.get_u_size()))

    try:
        import matplotlib.pyplot as plt
        tree.plot()
        plt.show()
    except:
        pass
