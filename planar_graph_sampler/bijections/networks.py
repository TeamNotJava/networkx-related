from framework.utils import Counter

from planar_graph_sampler.combinatorial_classes.network import NetworkClass
from planar_graph_sampler.bijections.halfedge import HalfEdge
from planar_graph_sampler.bijections.network_merge_in_series import NetworkMergeInSeries
from planar_graph_sampler.bijections.network_paralel_merge import NetworkMergeInParallel

counter = Counter()


def _create_root_network_edge():
    # Create the zero-pole of the network
    root_half_edge = HalfEdge()
    root_half_edge.next = root_half_edge
    root_half_edge.prior = root_half_edge
    root_half_edge.node_nr = next(counter)

    # Creates the inf-pole
    root_half_edge_opposite = HalfEdge()
    root_half_edge_opposite.next = root_half_edge_opposite
    root_half_edge_opposite.prior = root_half_edge_opposite
    root_half_edge_opposite.node_nr = next(counter)

    # Link the poles
    root_half_edge.opposite = root_half_edge_opposite
    root_half_edge_opposite.opposite = root_half_edge

    return root_half_edge


# creates a link_graph (from a u-atom)
# see sampler for Z_U in figure 9
def u_atom_to_network(u_atom):
    vertices_list = []
    edges_list = []
    root_half_edge = _create_root_network_edge()
    result = NetworkClass(vertices_list, edges_list, root_half_edge)
    assert (u_atom.get_u_size() == result.get_u_size())
    assert (u_atom.get_l_size() == result.get_l_size())
    return result


# serial composition of two networks (head and tail)
# see sampler for S in figure
def s_decomp_to_network(decomp):
    # decomp has this structure: ((first_network, l_atom), second_network)
    network = decomp.first.first
    network_for_plugging = decomp.second

    # Use the serial merge bijection to merge the networks
    result = NetworkMergeInSeries().merge_networks_in_series(network, network_for_plugging)

    # Check the properties
    assert (decomp.get_u_size() == result.get_u_size())
    assert (decomp.get_l_size() == result.get_l_size())
    return result


# parallel composition of a set of networks
# also adds link between poles
# see sampler for P_1 in figure 9
def p_decomp1_to_network(decomp):
    # decomp has the structure: (link_graph, [set of networks])
    # get the parallel composition of the networks
    result = p_decomp2_to_network(decomp.second)
    # add link between the poles
    result.edges_list.append(result.root_half_edge)
    assert (decomp.get_u_size() == result.get_u_size())
    assert (decomp.get_l_size() == result.get_l_size())
    return result


# parallel composition of a set of networks
# does not link the poles
# see sampler for P_2 in figure 9
def p_decomp2_to_network(decomp):
    # decomp has the structure: [set of networks]
    networks = decomp

    # Merge the netwowrks in parallel
    result = networks[0]
    for i in range(1, len(networks)):
        result = NetworkMergeInParallel().merge_networks_in_parallel(result, networks[i])

    # Check the properties
    assert (decomp.get_u_size() == result.get_u_size())
    assert (decomp.get_l_size() == result.get_l_size())
    return result


# Creates a network class from tree connected rooted planar graph.
# Basically just copy the vertices list, edges list and the root edge in the NetworkClass
def g_3_arrow_to_network(three_connected_rooted_planar_graph):
    # Extract the components from the three connected rooted planar graph
    vertices_list = list(three_connected_rooted_planar_graph.vertices_list)
    edges_list = list(three_connected_rooted_planar_graph.edges_list)
    root_half_edge = three_connected_rooted_planar_graph.root_half_edge

    # Create and return the network.
    return NetworkClass(vertices_list, edges_list, root_half_edge)

## and all the derived networks stuff also goes here
