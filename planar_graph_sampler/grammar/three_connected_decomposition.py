from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.generic_samplers import *
from framework.evaluation_oracle import EvaluationOracle

from planar_graph_sampler.grammar.irreducible_dissection_decomposition import irreducible_dissection_grammar
from planar_graph_sampler.bijections.primal_map import primal_map
from planar_graph_sampler.bijections.whitney_3map_to_3graph import whitney
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100


def bij_primal(decomp):
    return primal_map(decomp)


def bij_primal_dx(decomp):
    return primal_map(decomp)


def bij_whitney(decomp):
    return whitney(decomp)


def bij_whitney_dx(decomp):
    return whitney(decomp)


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

        'M_3_arrow': Bij(J_a, bij_primal),

        'M_3_arrow_dx': Bij(J_a_dx, bij_primal_dx),

        'G_3_arrow': Trans(M_3_arrow, bij_whitney,

                           eval_transform=lambda evl, x, y: 0.5 * evl),  # see 4.1.9.

        'G_3_arrow_dx': Trans(M_3_arrow_dx, bij_whitney_dx,
                              eval_transform=lambda evl, x, y: 0.5 * evl),

        'G_3_arrow_dy': DyFromDx(G_3_arrow_dx, alpha_u_l=3)  # alpha_u_l = 3, see 5.3.3.

    })

    return grammar


if __name__ == "__main__":
    grammar = three_connected_graph_grammar()
    grammar.init()

    BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'

    sampled_class = 'G_3_arrow'

    g = grammar.sample(sampled_class, symbolic_x, symbolic_y)

    import matplotlib.pyplot as plt
    g.plot()
    plt.show()
