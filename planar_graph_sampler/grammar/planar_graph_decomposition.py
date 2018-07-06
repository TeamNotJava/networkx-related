from framework.generic_samplers import *
from framework.decomposition_grammar import AliasSampler, DecompositionGrammar

from planar_graph_sampler.grammar.one_connected_decomposition import one_connected_graph_grammar


def planar_graph_grammar():
    """

    :return:
    """

    # Some shortcuts to make the grammar more readable.
    G_1 = AliasSampler('G_1')
    G_1_dx = AliasSampler('G_1_dx')
    G_1_dx_dx = AliasSampler('G_1_dx_dx')

    G = AliasSampler('G')
    G_dx = AliasSampler('G_dx')

    grammar = DecompositionGrammar()
    grammar.add_rules(one_connected_graph_grammar().get_rules())
    grammar.add_rules({

        # planar graphs

        'G': SetSampler(0, G_1),

        'G_dx': G_1_dx * G,

        'G_dx_dx': G_1_dx_dx * G + G_1_dx * G_dx,

    })

    return grammar
