from framework.generic_samplers import *
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler

from planar_graph_sampler.grammar.network_decomposition import network_grammar
from planar_graph_sampler.combinatorial_classes import UDerivedClass


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
    G_2_dx_dy = AliasSampler('G_2_dx_dy')
    G_2_arrow = AliasSampler('G_2_arrow')
    G_2_arrow_dx = AliasSampler('G_2_arrow_dx')
    Trans = TransformationSampler
    DxFromDy = LDerFromUDerSampler

    grammar = DecompositionGrammar()
    grammar.add_rules(network_grammar().get_rules())

    grammar.add_rules({

        # two connected

        'G_2_arrow': Trans(Z + D, id,
                           eval_transform=lambda evl, x, y: evl / (1 + BoltzmannSampler.oracle.get(y))),  # see 5.5

        'F': L**2 * G_2_arrow,

        'G_2_dy': Trans(F, id,
                        eval_transform=lambda evl, x, y: 0.5 * evl),

        'G_2_dx': DxFromDy(G_2_dy, alpha_l_u=2.0),  # see p. 26

        # l-derived two connected

        'G_2_arrow_dx': Trans(D_dx, id,
                              eval_transform=lambda evl, x, y: evl / (1 + BoltzmannSampler.oracle.get(y))),

        'F_dx': L**2 * G_2_arrow_dx + 2 * L * G_2_arrow,

        'G_2_dy_dx': Trans(F_dx, id,
                           eval_transform=lambda evl, x, y: 0.5 * evl),

        'G_2_dx_dy': G_2_dy_dx,

        'G_2_dx_dx': DxFromDy(G_2_dx_dy, alpha_l_u=1.0)  # see 5.5

    })

    return grammar
