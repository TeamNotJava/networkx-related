from __future__ import division
import networkx as nx

from framework.generic_classes import DerivedClass
from framework.generic_samplers import BoltzmannSamplerBase
from framework.evaluation_oracle import EvaluationOracle

from planar_graph_sampler.evaluations_planar_graph import \
    planar_graph_evals_n100, planar_graph_evals_n1000, reference_evals
from planar_graph_sampler.grammar.one_connected_decomposition import one_connected_graph_grammar
from planar_graph_sampler.grammar.one_connected_decomposition import two_connected_graph_grammar


def test_distribution(grammar, sampled_class, x, y, graphs_automs, num_samples=100):
    # for g_aut in graphs_automs:
    #     import matplotlib.pyplot as plt
    #     nx.draw(g_aut[0], with_labels=True)
    #     plt.show()

    def find_isomorphic_graph(g):
        for index, gr_aut in enumerate(graphs_automs):
            if nx.is_isomorphic(g, gr_aut[0]):
                return index
        assert False

    possible_graphs_count = sum([gr_aut[1] for gr_aut in graphs_automs])
    expected_distribution = [gr_aut[1] / possible_graphs_count for gr_aut in graphs_automs]

    count = 0
    result = [0 for _ in range(len(graphs_automs))]
    while count < num_samples:
        try:
            g = grammar.sample(sampled_class, x, y)
            if isinstance(g, DerivedClass):
                g = g.base_class_object
            if isinstance(g, DerivedClass):
                g = g.base_class_object
            if g.number_of_nodes == 4:
                g = g.to_networkx_graph()
                result[find_isomorphic_graph(g)] += 1
                count += 1
        except RecursionError:
            print("RecursionError")

    assert sum(result) == num_samples

    print("{} ({} samples):\n".format(sampled_class, num_samples))
    print("Observed absolute frequencies:\n{}\n".format(result))
    result = [x / num_samples for x in result]
    print("Observed relative frequencies:\n{}\n".format(result))
    print("Expected distribution:\n{}\n".format(expected_distribution))


def test_distribution_connected(num_samples=100):
    """Test if connected planar graphs with exactly 4 nodes have the right distribution."""
    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    grammar = one_connected_graph_grammar()
    grammar.init()

    # All one-connected planar graphs with 4 nodes and the number of their automorphisms.
    # See p.15, Fig. 5.
    cycle_with_chord = nx.cycle_graph(4)
    cycle_with_chord.add_edge(0, 2)
    graphs_automs = [
        (nx.path_graph(4), 12),
        (nx.star_graph(3), 4),
        (nx.lollipop_graph(3, 1), 12),
        (nx.cycle_graph(4), 3),
        (cycle_with_chord, 6),
        (nx.complete_graph(4), 1)
    ]

    test_distribution(grammar, 'G_1_dx_dx', 'x', 'y', graphs_automs, num_samples=num_samples)


def test_distribution_two_connected(num_samples=100):
    """Test if 2-connected planar graphs with exactly 4 nodes have the right distribution."""
    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    grammar = two_connected_graph_grammar()
    grammar.init()

    # All two-connected planar graphs with 4 nodes and the number of their automorphisms.
    # See p.15, Fig. 5.
    cycle_with_chord = nx.cycle_graph(4)
    cycle_with_chord.add_edge(0, 2)
    graphs_automs = [
        (nx.cycle_graph(4), 3),
        (cycle_with_chord, 6),
        (nx.complete_graph(4), 1)
    ]

    test_distribution(grammar, 'G_2_dx_dx', 'x*G_1_dx(x,y)', 'y', graphs_automs, num_samples=num_samples)


if __name__ == "__main__":
    test_distribution_connected(500)
    #test_distribution_two_connected()
