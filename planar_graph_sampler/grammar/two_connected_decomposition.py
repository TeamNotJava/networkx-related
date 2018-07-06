from framework.generic_samplers import *
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler

from planar_graph_sampler.grammar.network_decomposition import network_grammar
from planar_graph_sampler.combinatorial_classes import UDerivedClass


def add_root_edge(decomp):
    # return decomp.second
    if isinstance(decomp, ZeroAtomClass):
        return UAtomClass()
    return decomp


def forget_direction_of_root_edge(decomp):
    return UDerivedClass(decomp, None)


def two_connected_graph_grammar():
    """

    :return:
    """

    Z = ZeroAtomSampler()
    L = LAtomSampler()
    D = AliasSampler('D')
    D_dx = AliasSampler('D_dx')
    F = AliasSampler('F')
    F_dx = AliasSampler('F_dx')
    G_2_dy = AliasSampler('G_2_dy')
    G_2_dy_dx = AliasSampler('G_2_dy_dx')
    G_2_arrow = AliasSampler('G_2_arrow')
    G_2_arrow_dx = AliasSampler('G_2_arrow_dx')
    Trans = TransformationSampler

    grammar = DecompositionGrammar()
    grammar.add_rules(network_grammar().get_rules())

    grammar.add_rules({

        # 2 connected planar graphs

        'G_2_arrow': Trans(Z + D, add_root_edge),

        'F': L * L * G_2_arrow,

        'G_2_dy': Trans(F, forget_direction_of_root_edge, 'G_2_dy'),

        'G_2_dx': LDerFromUDerSampler(G_2_dy, 2.0),  # see p. 26

        # l-derived 2 connected planar graphs

        'G_2_arrow_dx': Trans(D_dx, add_root_edge),

        'F_dx': L * L * G_2_arrow_dx + (L + L) * G_2_arrow,  # notice that 2 * L = L + L

        'G_2_dy_dx': Trans(F_dx, forget_direction_of_root_edge, 'G_2_dy_dx'),

        'G_2_dx_dx': LDerFromUDerSampler(G_2_dy_dx, 1.0),  # see 5.5

    })

    return grammar
