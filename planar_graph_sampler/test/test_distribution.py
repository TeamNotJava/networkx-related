from __future__ import division
import networkx as nx

from framework.generic_classes import DerivedClass
from framework.generic_samplers import BoltzmannSamplerBase
from framework.evaluation_oracle import EvaluationOracle

from planar_graph_sampler.evaluations_planar_graph import \
    planar_graph_evals_n100, planar_graph_evals_n1000, reference_evals
from planar_graph_sampler.grammar.binary_tree_decomposition import binary_tree_grammar
from planar_graph_sampler.grammar.one_connected_decomposition import one_connected_graph_grammar
from planar_graph_sampler.grammar.one_connected_decomposition import two_connected_graph_grammar
from planar_graph_sampler.grammar.three_connected_decomposition import three_connected_graph_grammar


def test_boltzmann_prob(grammar, sampled_class, x, y, l_size, num_graphs, num_samples=100, silent=False):
    oracle = BoltzmannSamplerBase.oracle
    assert oracle is not None
    assert oracle[y] == 1.0

    total_prob = num_graphs * oracle.get_probability(sampled_class, x, y, l_size, 1.0)
    count = 0
    fails = 0
    successes = 0
    while count < num_samples:
        try:
            g = grammar.sample(sampled_class, x, y)
            if g.l_size == l_size:
                # Count the observation.
                successes += 1
            else:
                fails += 1
        except RecursionError:
            fails += 1
            if not silent:
                print("RecursionError")
        count += 1

    observed_prob = successes / num_samples
    error = observed_prob / total_prob - 1

    if not silent:
        print("{} ({} samples):\n".format(sampled_class, num_samples))
        print("Probability for hitting object with l-size {}: {}".format(l_size, total_prob))
        print("Observed probability: {} (Error: {})\n".format(observed_prob, error))

    return error


def test_distribution_for_l_size(grammar, sampled_class, x, y, l_size, graphs_labs_u_size, num_samples=100,
                                 silent=False):
    # for g_aut in graphs_labs_u_size:
    #     import matplotlib.pyplot as plt
    #     nx.draw(g_aut[0], with_labels=True)
    #     plt.show()

    def find_isomorphic_graph(g):
        for i, g_l_u in enumerate(graphs_labs_u_size):
            if nx.is_isomorphic(g, g_l_u[0]):
                return i
        import matplotlib.pyplot as plt
        nx.draw(g, with_labels=True)
        plt.show()
        assert False

    for g1, _, _ in graphs_labs_u_size:
        for g2, _, _ in graphs_labs_u_size:
            if g1 != g2:
                assert not nx.is_isomorphic(g1, g2)

    oracle = BoltzmannSamplerBase.oracle
    assert oracle is not None
    expected_distribution = [
        g_l_u[1] * oracle.get_probability(sampled_class, x, y, l_size, g_l_u[2]) for g_l_u in graphs_labs_u_size
    ]
    total_prob = sum(expected_distribution)

    norm_factor = sum(expected_distribution)
    expected_distribution = [x / norm_factor for x in expected_distribution]

    count = 0
    fails = 0
    absolute_frequencies = [0 for _ in range(len(graphs_labs_u_size))]
    while count < num_samples:
        try:
            g = grammar.sample_iterative(sampled_class, x, y)
            if g.l_size == l_size:
                # Remove all wrapping derived classes if any.
                g_base = g.underive_all()
                assert g_base.is_consistent
                # Convert to networkx graph to use the isomorphism test.
                gnx = g_base.to_networkx_graph(include_unpaired=False)
                index = find_isomorphic_graph(gnx)
                # Assert that we provided the correct u-size.
                assert graphs_labs_u_size[index][2] == g.u_size
                # Count the observation.
                absolute_frequencies[index] += 1
                count += 1
            else:
                fails += 1
        except RecursionError:
            if not silent:
                print("RecursionError")

    observed_prob = num_samples / (num_samples + fails)
    prob_error = observed_prob / total_prob - 1

    relative_frequencies = [x / num_samples for x in absolute_frequencies]
    errors = [obs / exp - 1 for obs, exp in zip(relative_frequencies, expected_distribution)]

    if not silent:
        print("{} ({} samples):\n".format(sampled_class, num_samples))
        print("Probability for hitting object with l-size {}: {}".format(l_size, total_prob))
        print("Observed probability: {} (Error: {})\n".format(observed_prob, prob_error))

        # print("Observed absolute frequencies:\n{}\n".format(absolute_frequencies))
        print("Observed relative frequencies:{}\n".format(relative_frequencies))
        print("Expected distribution:{}\n".format(expected_distribution))
        print("Errors:{}\n\n".format(errors))

    return prob_error, errors


def test_distribution_R_w_l_1(num_samples=100):
    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    grammar = binary_tree_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'R_w'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    # In this case the labs column does not correspond to actual labelings
    # but to distinction because of the root.
    graphs_labs_u_size = [
        (nx.path_graph(2), 2, 3),
        (nx.path_graph(3), 4, 4),
        (nx.star_graph(3), 2, 5),
    ]

    test_distribution_for_l_size(
        grammar,
        sampled_class,
        symbolic_x, symbolic_y,
        1,  # l-size
        graphs_labs_u_size,
        num_samples
    )


def test_distribution_R_b_l_1(num_samples=100):
    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    grammar = binary_tree_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'R_b'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    # In this case the labs column does not correspond to actual labelings
    # but to distinction because of the root.
    graphs_labs_u_size = [
        (nx.path_graph(1), 1, 2),
        (nx.path_graph(2), 2, 3),
        (nx.path_graph(3), 1, 4),
    ]

    test_distribution_for_l_size(
        grammar,
        sampled_class,
        symbolic_x, symbolic_y,
        1,  # l-size
        graphs_labs_u_size,
        num_samples
    )


def test_distribution_K_dy_l_1(num_samples=100):
    BoltzmannSamplerBase.oracle = EvaluationOracle(reference_evals)
    grammar = binary_tree_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'K_dy'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    # In this case the labs column does not correspond to actual labelings
    # but to distinction because of the root.
    graphs_labs_u_size = [
        (nx.path_graph(2), 4, 3),
        (nx.path_graph(3), 5, 4),
    ]

    test_distribution_for_l_size(
        grammar,
        sampled_class,
        symbolic_x, symbolic_y,
        1,  # l-size
        graphs_labs_u_size,
        num_samples
    )


def test_distribution_K_l_1(num_samples=100):
    """Unrooted binary trees (class K) with one black node."""
    BoltzmannSamplerBase.oracle = EvaluationOracle(reference_evals)
    grammar = binary_tree_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'K'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    # There are only 2 possibilities.
    graphs_labs = [
        (nx.path_graph(2), 1, 4),
        (nx.path_graph(3), 2, 5),  # TODO here something looks wrong when you run it.
    ]

    test_distribution_for_l_size(
        grammar,
        sampled_class,
        symbolic_x, symbolic_y,
        1,  # l-size
        graphs_labs,
        num_samples)


def test_distribution_K_l_2(num_samples=100):
    BoltzmannSamplerBase.oracle = EvaluationOracle(reference_evals)
    grammar = binary_tree_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'K'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    star_path_1 = nx.star_graph(3)
    star_path_1.add_edge(1, 4)
    star_path_2 = nx.star_graph(3)
    star_path_2.add_edge(1, 4)
    star_path_2.add_edge(4, 5)
    other = nx.Graph(star_path_1)
    other.add_edge(4, 5)
    other.add_edge(4, 6)
    # The first factor is due to the position of the leaves and the second are the labellings.
    graphs_labs_u_size = [
        (nx.path_graph(3), 1 * 2, 5),
        (nx.path_graph(4), 4 * 2, 6),
        (nx.path_graph(5), 4 * 2, 7),
        (star_path_1, 2 * 2, 7),
        (star_path_2, 4 * 2, 8),
        (other, 1 * 2, 9)
    ]

    test_distribution_for_l_size(
        grammar,
        sampled_class,
        symbolic_x, symbolic_y,
        2,  # l-size
        graphs_labs_u_size,
        num_samples)


def test_distribution_G_3_arrow_l_2(num_samples=100):
    BoltzmannSamplerBase.oracle = EvaluationOracle(reference_evals)
    grammar = three_connected_graph_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'G_3_arrow'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    # There is only 1 possibility, this test is sort of boring.
    graphs_labs_u_size = [
        (nx.complete_graph(4), 1, 5)
    ]

    test_distribution_for_l_size(
        grammar,
        sampled_class,
        symbolic_x, symbolic_y,
        2,  # l-size
        graphs_labs_u_size,
        num_samples=num_samples)


def test_distribution_G_3_arrow_l_3(num_samples=100):
    BoltzmannSamplerBase.oracle = EvaluationOracle(reference_evals)
    grammar = three_connected_graph_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'G_3_arrow'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    cycle_with_midpoint = nx.cycle_graph(4)
    cycle_with_midpoint.add_edges_from([(0, 4), (1, 4), (2, 4), (3, 4)])
    fully_triangulated = nx.complete_graph(4)
    fully_triangulated.add_edges_from([(0, 4), (1, 4), (2, 4)])
    other = nx.cycle_graph(4)
    other.add_edges_from([(0, 4), (1, 4), (2, 4)])

    # See p. 12 (2) and p. 16.
    # The number of labellings come from deriving the generating function G_3 by y and then multiplying by 2.
    # The l-size is 2 less for edge rooted graphs, so we divide by 4*5 to get the form x³/3! * ...
    graphs_labs_u_size = [
        (cycle_with_midpoint, 2 * 8 * 15 / (4 * 5), 7),
        (fully_triangulated, 2 * 9 * 10 / (4 * 5), 8)
    ]

    test_distribution_for_l_size(
        grammar,
        sampled_class,
        symbolic_x, symbolic_y,
        3,  # l-size
        graphs_labs_u_size,
        num_samples=num_samples)


def test_distribution_G_3_arrow_l_4(num_samples=100):
    BoltzmannSamplerBase.oracle = EvaluationOracle(reference_evals)
    grammar = three_connected_graph_grammar()
    grammar.init()
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    sampled_class = 'G_3_arrow'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    # TODO we do not have enough data here to make this test

    g9 = nx.Graph()
    g9.add_edges_from([(0, 1), (0, 3), (0, 5), (1, 3), (1, 4), (2, 3), (2, 5), (2, 4), (4, 5)])
    g10_1 = nx.Graph()
    g10_1.add_edges_from([(0, 1), (0, 3), (0, 2), (0, 5), (1, 2), (1, 4), (1, 5), (2, 3), (3, 4), (4, 5)])
    g10_2 = nx.Graph()
    g10_2.add_edges_from([(0, 1), (0, 2), (0, 3), (1, 2), (1, 5), (2, 3), (2, 5), (2, 4), (3, 4), (4, 5)])
    g11_1 = nx.Graph()
    g11_1.add_edges_from([(0, 1), (0, 5), (0, 4), (0, 3), (1, 4), (1, 5), (1, 2), (2, 3), (2, 5), (3, 5), (3, 4)])
    g11_2 = nx.Graph()
    g11_2.add_edges_from([(0, 1), (0, 3), (0, 2), (0, 5), (0, 4), (1, 2), (1, 5), (1, 3), (2, 3), (3, 4), (4, 5)])
    g12_1 = nx.Graph()
    g12_1.add_edges_from(
        [(0, 1), (0, 2), (0, 3), (0, 5), (0, 4), (1, 2), (1, 4), (2, 3), (2, 4), (2, 5), (3, 5), (4, 5)])
    g12_2 = nx.Graph()
    g12_2.add_edges_from(
        [(0, 1), (0, 2), (0, 3), (0, 5), (1, 2), (1, 4), (1, 5), (2, 3), (2, 4), (3, 4), (3, 5), (4, 5)])

    # ...
    graphs_labs_u_size = [
        (g9, 2 * 9 * 60 / (6 * 5), 8),
        (g10_1, 2 * 10 * 432 / (6 * 5), 9),
        (g10_2, 2 * 10 * 0 / (6 * 5), 9),  # Don't know how many there are with 10 edges
        (g11_1, 2 * 11 * 540 / (6 * 5), 10),
        (g11_2, 2 * 11 * 0 / (6 * 5), 10),  # Same as above ...
        (g12_1, 2 * 12 * 195 / (6 * 5), 11),
        (g12_2, 2 * 12 * 0 / (6 * 5), 11)  # Same as above ...
    ]

    test_distribution_for_l_size(
        grammar, sampled_class, symbolic_x, symbolic_y, 4, graphs_labs_u_size, num_samples=num_samples)


def test_distribution_G_2_dx_l_3(num_samples=100):
    """Test if 2-connected planar graphs with exactly 4 nodes have the right distribution."""
    BoltzmannSamplerBase.oracle = EvaluationOracle(reference_evals)
    grammar = two_connected_graph_grammar()
    grammar.init()
    # grammar.precompute_evals('G_2_dx', 'x*G_1_dx(x,y)', 'y')

    # All two-connected planar graphs with 4 nodes and the number of their automorphisms.
    # See p.15, Fig. 5.
    cycle_with_chord = nx.cycle_graph(4)
    cycle_with_chord.add_edge(0, 2)
    graphs_labs = [
        (nx.cycle_graph(4), 3, 4),
        (cycle_with_chord, 6, 5),
        (nx.complete_graph(4), 1, 6)
    ]

    test_distribution_for_l_size(grammar, 'G_2_dx', 'x*G_1_dx(x,y)', 'y', 3, graphs_labs, num_samples=num_samples)


def test_distribution_G_2_dx_dx_l_3(num_samples=100):
    """Test if 2-connected planar graphs with exactly 4 nodes have the right distribution."""
    BoltzmannSamplerBase.oracle = EvaluationOracle(reference_evals)
    grammar = two_connected_graph_grammar()
    grammar.init()
    # grammar.precompute_evals('G_2_dx', 'x*G_1_dx(x,y)', 'y')

    # All two-connected planar graphs with 4 nodes and the number of their labellings.
    # See p.15, Fig. 5.
    cycle_with_chord = nx.cycle_graph(4)
    cycle_with_chord.add_edge(0, 2)
    graphs_labs = [
        (nx.cycle_graph(4), 3, 4),
        (cycle_with_chord, 6, 5),
        (nx.complete_graph(4), 1, 6)
    ]

    test_distribution_for_l_size(grammar, 'G_2_dx_dx', 'x*G_1_dx(x,y)', 'y', 2, graphs_labs, num_samples=num_samples)


def test_distribution_G_1_l_3(num_samples=100):
    """Test if connected planar graphs with exactly 4 nodes have the right distribution."""
    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    grammar = one_connected_graph_grammar()
    grammar.init()

    graphs_labs = [
        (nx.path_graph(3), 3, 2),
        (nx.complete_graph(3), 1, 3)
    ]

    test_distribution_for_l_size(grammar, 'G_1', 'x', 'y', 3, graphs_labs, num_samples=num_samples)


def test_distribution_G_1_l_4(num_samples=100):
    """Test if connected planar graphs with exactly 4 nodes have the right distribution."""
    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    grammar = one_connected_graph_grammar()
    grammar.init()

    # All one-connected planar graphs with 4 nodes and the number of their labellings.
    # See p.15, Fig. 5.
    cycle_with_chord = nx.cycle_graph(4)
    cycle_with_chord.add_edge(0, 2)
    graphs_labs = [
        (nx.path_graph(4), 12, 3),
        (nx.star_graph(3), 4, 3),
        (nx.lollipop_graph(3, 1), 12, 4),
        (nx.cycle_graph(4), 3, 4),
        (cycle_with_chord, 6, 5),
        (nx.complete_graph(4), 1, 6)
    ]

    test_distribution_for_l_size(grammar, 'G_1', 'x', 'y', 4, graphs_labs, num_samples=num_samples)


def test_distribution_G_1_dx_l_2(num_samples=100):
    """Test if connected planar graphs with exactly 4 nodes have the right distribution."""
    BoltzmannSamplerBase.oracle = EvaluationOracle(reference_evals)
    grammar = one_connected_graph_grammar()
    grammar.init()

    graphs_labs = [
        (nx.path_graph(3), 3, 2),
        (nx.complete_graph(3), 1, 3)
    ]

    test_distribution_for_l_size(grammar, 'G_1_dx', 'x', 'y', 2, graphs_labs, num_samples=num_samples)


def test_distribution_G_1_dx_l_3(num_samples=100):
    """Test if connected planar graphs with exactly 4 nodes have the right distribution."""
    BoltzmannSamplerBase.oracle = EvaluationOracle(reference_evals)
    grammar = one_connected_graph_grammar()
    grammar.init()

    # All one-connected planar graphs with 4 nodes and the number of their labellings.
    # See p.15, Fig. 5.
    cycle_with_chord = nx.cycle_graph(4)
    cycle_with_chord.add_edge(0, 2)
    graphs_labs = [
        (nx.path_graph(4), 12, 3),
        (nx.star_graph(3), 4, 3),
        (nx.lollipop_graph(3, 1), 12, 4),
        (nx.cycle_graph(4), 3, 4),
        (cycle_with_chord, 6, 5),
        (nx.complete_graph(4), 1, 6)
    ]

    test_distribution_for_l_size(grammar, 'G_1_dx', 'x', 'y', 3, graphs_labs, num_samples=num_samples)


def test_distribution_G_1_dx_dx_l_2(num_samples=100):
    """Test if connected planar graphs with exactly 4 nodes have the right distribution."""
    BoltzmannSamplerBase.oracle = EvaluationOracle(reference_evals)
    grammar = one_connected_graph_grammar()
    grammar.init()

    # All one-connected planar graphs with 4 nodes and the number of their labellings.
    # See p.15, Fig. 5.
    cycle_with_chord = nx.cycle_graph(4)
    cycle_with_chord.add_edge(0, 2)
    graphs_labs = [
        (nx.path_graph(4), 12, 3),
        (nx.star_graph(3), 4, 3),
        (nx.lollipop_graph(3, 1), 12, 4),
        (nx.cycle_graph(4), 3, 4),
        (cycle_with_chord, 6, 5),
        (nx.complete_graph(4), 1, 6)
    ]

    test_distribution_for_l_size(grammar, 'G_1_dx_dx', 'x', 'y', 2, graphs_labs, num_samples=num_samples)


if __name__ == "__main__":
    import random

    random.seed(0)

    # test_distribution_G_1_l_3(100)
    # test_distribution_G_1_l_4(100)
    # test_distribution_G_1_dx_l_2(1000)
    # test_distribution_G_1_dx_l_3(1000)
    # test_distribution_G_1_dx_dx_l_2(1000)

    # test_distribution_G_2_dx_l_3(100)

    # test_distribution_R_w_l_1(1000)
    # test_distribution_R_b_l_1(1000)
    # test_distribution_K_dy_l_1(1000)
    # test_distribution_K_l_2(1000)
    # test_distribution_K_l_1(1000) # TODO this looks broken

    # test_distribution_G_3_arrow_l_2(1000)  # TODO make this a probability test
    # test_distribution_G_3_arrow_l_3(100)
    # test_distribution_G_3_arrow_l_4(1000)  # TODO make this a probability test

    # BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    # grammar = one_connected_graph_grammar()
    # grammar.init()
    # grammar.precompute_evals('G_1_dx_dx', 'x', 'y')

    # sequence counting connected planar graphs

    # [1,1,4,38,727,26013,1597690,149248656,18919743219,
    #  3005354096360,569226803220234,124594074249852576,
    #  30861014504270954737,8520443838646833231236,
    #  2592150684565935977152860,
    #  861079753184429687852978432,
    #  310008316267496041749182487881]

    # test_boltzmann_prob(grammar, 'G_1_dx_dx', 'x', 'y', 3, 727, 2 * 10**6)
