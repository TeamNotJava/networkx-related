from framework.generic_samplers import *
from framework.decomposition_grammar import AliasSampler, DecompositionGrammar

from planar_graph_sampler.grammar.two_connected_decomposition import two_connected_graph_grammar


def one_connected_graph_grammar():
    """

    :return:
    """

    # Some shortcuts to make the grammar more readable.
    L = LAtomSampler()
    G_2_dx = AliasSampler('G_2_dx')
    G_2_dx_dx = AliasSampler('G_2_dx_dx')
    G_1 = AliasSampler('G_1')
    G_1_dx = AliasSampler('G_1_dx')
    G_1_dx_dx = AliasSampler('G_1_dx_dx')

    grammar = DecompositionGrammar()
    grammar.add_rules(two_connected_graph_grammar().get_rules())
    grammar.add_rules({

        # 1 connected planar graphs

        'G_1_dx': SetSampler(0, LSubsSampler(G_2_dx, L * G_1_dx)),

        'G_1_dx_dx': (G_1_dx + L * G_1_dx_dx) * (LSubsSampler(G_2_dx_dx, L * G_1_dx)) * G_1_dx,

        'G_1': RejectionSampler(G_1_dx, lambda g: bern(1 / (g.get_l_size() + 1)), 'G_1'),  # lemma 15

    })

    return grammar
