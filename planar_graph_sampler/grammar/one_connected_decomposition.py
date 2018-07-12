from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import *
from framework.decomposition_grammar import AliasSampler, DecompositionGrammar
from planar_graph_sampler.combinatorial_classes.one_connected_graph import OneConnectedPlanarGraph
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100, planar_graph_evals_n1000

from planar_graph_sampler.grammar.two_connected_decomposition import two_connected_graph_grammar


class Merger(DefaultBuilder):
    def set(self, graphs):
        if len(graphs) is 0:
            return OneConnectedPlanarGraph()
        res = graphs.pop()
        for g in graphs:
            res.get_half_edge().insert_all(g.get_half_edge())
        return res


def one_connected_graph_grammar():
    """

    :return:
    """

    # Some shortcuts to make the grammar more readable.
    L = LAtomSampler()
    G_2_dx = AliasSampler('G_2_dx')
    G_2_dx_dx = AliasSampler('G_2_dx_dx')
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
    grammar.set_builder(['G_1_dx'], Merger())

    return grammar


if __name__ == '__main__':
    grammar = one_connected_graph_grammar()
    grammar.init()

    BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n1000)
    BoltzmannSampler.debug_mode = False

    symbolic_x = 'x'
    symbolic_y = 'y'

    sampled_class = 'G_1_dx'

    while True:
        try:
            g = grammar.sample(sampled_class, symbolic_x, symbolic_y)
        except RecursionError:
            pass
        if g.get_l_size() > 5:
            print(g)
            assert g.is_consistent()

            import matplotlib.pyplot as plt

            g.plot(with_labels=False)
            plt.show()
