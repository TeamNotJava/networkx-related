import logging
from random import choice
import networkx as nx

from framework.generic_samplers import *
from framework.generic_classes import CombinatorialClass
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.evaluation_oracle import EvaluationOracle

from planar_graph_sampler.bijections.closure import Closure
from planar_graph_sampler.grammar.binary_tree_decomposition import binary_tree_grammar
from planar_graph_sampler.rejections.admissibility_check import check_admissibility
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100, planar_graph_evals_n1000


def closure(binary_tree):
    """To be used as bijection in the grammar.

    :param binary_tree: The binary tree of l-derived binary tree to be closed
    :return: The closure/l-derived closure of the tree/l-derived tree
    """
    dissection = Closure().closure(binary_tree)
    return dissection


def add_random_root_edge(decomp):
    """From ((L, U), dissection) or (U, dissection) to RootedIrreducibleDissection
    """
    dissection = decomp.second
    dissection.root_at_random_hexagonal_edge()
    return dissection


def irreducible_dissection_grammar():
    """
    Builds the dissection grammar. Must still be initialized with init().

    :return:
    """

    # Some shorthands to keep the grammar readable.
    L = LAtomSampler
    U = UAtomSampler
    K = AliasSampler('K')
    K_dx = AliasSampler('K_dx')
    I = AliasSampler('I')
    I_dx = AliasSampler('I_dx')
    J = AliasSampler('J')
    J_dx = AliasSampler('J_dx')
    Bij = BijectionSampler
    Rej = RejectionSampler

    grammar = DecompositionGrammar()
    # This grammar depends on the binary tree grammar so we add it.
    grammar.add_rules(binary_tree_grammar().get_rules())

    grammar.add_rules({

        'I': Bij(K, closure),

        'I_dx': Bij(K_dx, closure),

        'J': Bij(3*L()*U()*I, add_random_root_edge),

        'J_dx': Bij(3*U()*I + 3*L()*U()*I_dx, add_random_root_edge),

        'J_a': Rej(J, lambda d: d.is_admissible()),

        'J_a_dx': Rej(J_dx, lambda d: d.is_admissible()),

    })
    return grammar


if __name__ == "__main__":
    grammar = irreducible_dissection_grammar()
    grammar.init()

    BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'

    sampled_class = 'I'

    diss = grammar.sample(sampled_class, symbolic_x, symbolic_y)

    assert diss.half_edge.color is 'black'
    assert diss.half_edge.is_hexagonal

    print()
    print(diss.half_edge.node_nr)
    print(diss.half_edge.opposite.node_nr)
    print(diss.number_of_nodes())
    print(diss.number_of_edges())

    print(diss.number_of_half_edges())
    print(len(diss.get_half_edge().get_all_half_edges(include_opp=False, include_unpaired=False)))

    [print(he) for he in diss.get_hexagonal_edges()]

    import matplotlib.pyplot as plt
    diss.plot()
    plt.show()
