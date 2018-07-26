from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.generic_samplers import *
from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import BoltzmannSamplerBase

from planar_graph_sampler.grammar.irreducible_dissection_decomposition import irreducible_dissection_grammar
from planar_graph_sampler.bijections.primal_map import primal_map
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100
from planar_graph_sampler.combinatorial_classes.three_connected_graph import UDerivedEdgeRootedThreeConnectedPlanarGraph


def to_G_3_arrow_dx(g):
    return UDerivedEdgeRootedThreeConnectedPlanarGraph(g.get_half_edge())


def three_connected_graph_grammar():
    """
    Builds the three-connected planar graph grammar.

    :return:
    """

    # Some shorthands to keep the grammar readable.
    J_a = AliasSampler('J_a')
    J_a_dx = AliasSampler('J_a_dx')
    M_3_arrow = AliasSampler('M_3_arrow')
    M_3_arrow_dx = AliasSampler('M_3_arrow_dx')
    G_3_arrow_dx = AliasSampler('G_3_arrow_dx')
    Bij = BijectionSampler
    Trans = TransformationSampler
    DyFromDx = UDerFromLDerSampler

    grammar = DecompositionGrammar()
    # Depends on irreducible dissection so we add those rules.
    grammar.add_rules(irreducible_dissection_grammar().get_rules())

    grammar.add_rules({

        'M_3_arrow': Bij(J_a, primal_map),

        'M_3_arrow_dx': Bij(J_a_dx, primal_map),

        'G_3_arrow': Trans(M_3_arrow, eval_transform=lambda evl, x, y: 0.5 * evl),  # see 4.1.9.

        'G_3_arrow_dx': Trans(M_3_arrow_dx, eval_transform=lambda evl, x, y: 0.5 * evl),

        'G_3_arrow_dy': Bij(DyFromDx(G_3_arrow_dx, alpha_u_l=3), to_G_3_arrow_dx)  # _alpha_u_l = 3, see 5.3.3.

    })

    return grammar


if __name__ == "__main__":
    grammar = three_connected_graph_grammar()
    grammar.init()

    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'

    sampled_class = 'G_3_arrow_dx'

    g = grammar.sample(sampled_class, symbolic_x, symbolic_y)
    print(g)
    assert g.is_consistent()

    import matplotlib.pyplot as plt
    g.plot()
    plt.show()
