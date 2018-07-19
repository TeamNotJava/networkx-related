from framework.generic_samplers import *
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler

from planar_graph_sampler.grammar.network_decomposition import network_grammar
from planar_graph_sampler.combinatorial_classes import UDerivedClass
from framework.evaluation_oracle import EvaluationOracle
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100


def add_root_edge(decomp):
    if isinstance(decomp, ZeroAtomClass):
        return UAtomClass()
    # Check if the poles in decomp are adjecent.
    # if not add an edge between the poles and root the whole graph on this new edge.
    # This edge is directed from 0 to inf
    # TODO Are our roots currently directed? If not why, if yes how?
    return decomp


def forget_direction_of_root_edge(decomp):
    # just forget about the direction of the root edge (maybe the edge between 0 and inf added in add_root_edge)
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


if __name__ == "__main__":
    grammar = two_connected_graph_grammar()
    grammar.init()

    BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'y'

    sampled_class = 'G_2_dy'

    g = grammar.sample(sampled_class, symbolic_x, symbolic_y)

    import matplotlib.pyplot as plt
    g.get_base_class_object.root_half_edge.plot()
    plt.show()
