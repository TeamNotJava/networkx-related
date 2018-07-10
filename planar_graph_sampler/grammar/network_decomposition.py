from framework.class_builder import CombinatorialClassBuilder
from framework.generic_samplers import *
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.evaluation_oracle import EvaluationOracle
from framework.utils import Counter
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100

from planar_graph_sampler.grammar.three_connected_decomposition import three_connected_graph_grammar
from planar_graph_sampler.combinatorial_classes.network import Network
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge
from planar_graph_sampler.bijections.network_merge_in_series import NetworkMergeInSeries
from planar_graph_sampler.bijections.network_paralel_merge import NetworkMergeInParallel

counter = Counter()

class NetworkBuilder(DefaultBuilder):

    def u_atom(self):
        """
        Returns the trivial link network consisting of the poles and an edge between them.
        :return:
        """
        # Create the zero-pole of the network
        root_half_edge = HalfEdge(self_consistent=True)
        root_half_edge.node_nr = next(counter)

        # Creates the inf-pole
        root_half_edge_opposite = HalfEdge(self_consistent=True)
        root_half_edge_opposite.node_nr = next(counter)

        # Link the poles
        root_half_edge.opposite = root_half_edge_opposite
        root_half_edge_opposite.opposite = root_half_edge

        res = Network(root_half_edge, is_linked=True)
        assert res.get_l_size() == 0 and res.get_u_size() == 1


        return res


def bij_s_decomp_to_network(decomp):
    # decomp has this structure: ((first_network, l_atom), second_network)
    network = decomp.first.first
    network_for_plugging = decomp.second

    # Use the serial merge bijection to merge the networks
    result = NetworkMergeInSeries().merge_networks_in_series(network, network_for_plugging)

    # Check the properties
    print("%s %s" % (decomp.get_l_size(), result.get_l_size()))
    print("%s %s" % (decomp.get_u_size(), result.get_u_size()))
    assert (decomp.get_u_size() == result.get_u_size())
    assert (decomp.get_l_size() == result.get_l_size())
    return result


def bij_p_decomp1_to_network(decomp):
    # decomp has the structure: (link_graph, [set of networks])
    # get the parallel composition of the networks
    result = bij_p_decomp2_to_network(decomp.second)
    # add link between the poles
    #result.edges_list.append(result.root_half_edge)
    assert (decomp.get_u_size() == result.get_u_size())
    assert (decomp.get_l_size() == result.get_l_size())
    return result


def bij_p_decomp2_to_network(decomp):
    # decomp has the structure: [set of networks]
    networks = decomp.elems

    # Merge the networks in parallel
    result = networks[0]
    for i in range(1, len(networks)):
        result = NetworkMergeInParallel().merge_networks_in_parallel(result, networks[i])

    # Check the properties
    assert (decomp.get_u_size() == result.get_u_size())
    assert (decomp.get_l_size() == result.get_l_size())
    return result


def bij_g_3_arrow_to_network(g):
    # Extract the components from the three connected rooted planar graph
    #vertices_list = list(three_connected_rooted_planar_graph.vertices_list)
    #edges_list = list(three_connected_rooted_planar_graph.edges_list)
    link_edge = g.get_half_edge()
    # Create and return the network.
    return Network(link_edge, is_linked=True)


def network_grammar():
    """

    :return:
    """

    L = LAtomSampler
    U = UAtomSampler
    G_3_arrow = AliasSampler('G_3_arrow')
    G_3_arrow_dx = AliasSampler('G_3_arrow_dx')
    G_3_arrow_dy = AliasSampler('G_3_arrow_dy')
    D = AliasSampler('D')
    D_dx = AliasSampler('D_dx')
    S = AliasSampler('S')
    S_dx = AliasSampler('S_dx')
    P = AliasSampler('P')
    P_dx = AliasSampler('P_dx')
    H = AliasSampler('H')
    H_dx = AliasSampler('H_dx')
    Bij = BijectionSampler

    grammar = DecompositionGrammar()
    grammar.add_rules(three_connected_graph_grammar().get_rules())

    grammar.add_rules({

        # networks

        'D': U() + S + P + H,

        #'S': Bij((U() + P + H) * L() * D, bij_s_decomp_to_network),
        'S': Bij( U()*L()*U(), bij_s_decomp_to_network),

        'P': Bij((U() * SetSampler(1, S + H)), bij_p_decomp1_to_network)
             + Bij(SetSampler(2, S + H), bij_p_decomp2_to_network),

        'H': Bij(USubsSampler(G_3_arrow, D), bij_g_3_arrow_to_network),

        # l-derived networks

        'D_dx': S_dx + P_dx + H_dx,

        'S_dx': (P_dx + H_dx) * L() * D + (U() + P + H) * (D + L() + D_dx),  # todo bijection

        'P_dx': U() * (S_dx + H_dx) * SetSampler(0, S + H) + (S_dx + H_dx) * SetSampler(1, S + H),  # todo bijection

        'H_dx': USubsSampler(G_3_arrow_dx, D) + D_dx * USubsSampler(G_3_arrow_dy, D_dx),

    })

    grammar.set_builder(['D', 'S', 'P', 'H', 'D_dx', 'S_dx', 'P_dx', 'H_dx'], NetworkBuilder())

    return grammar


if __name__ == '__main__':
    grammar = network_grammar()
    grammar.init()

    BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'y'

    sampled_class = 'S'

    g = grammar.sample(sampled_class, symbolic_x, symbolic_y)

    import matplotlib.pyplot as plt
    g.plot()
    plt.show()
