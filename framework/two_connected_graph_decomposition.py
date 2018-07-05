from .decomposition_grammar import AliasSampler
from .three_connected_graph_decomposition import three_connected_graph_grammar
from .samplers.generic_samplers import *
from .decomposition_grammar import DecompositionGrammar
from .combinatorial_classes.network import NetworkClass
from .bijections.halfedge import HalfEdge
from .bijections.network_merge_in_series import NetworkMergeInSeries
from .bijections.network_paralel_merge import NetworkMergeInParallel
from .utils import bern
from .bijections.closure import Closure
from .combinatorial_classes import UDerivedClass
from random import choice
import logging

Z = ZeroAtomSampler()
L = LAtomSampler()
U = UAtomSampler()
G_3_arrow = AliasSampler('G_3_arrow')
G_3_arrow_dx = AliasSampler('G_3_arrow_dx')
G_3_arrow_dy = AliasSampler('G_3_arrow_dy')
Link = AliasSampler('Link')
D = AliasSampler('D')
D_dx = AliasSampler('D_dx')
S = AliasSampler('S')
S_dx = AliasSampler('S_dx')
P = AliasSampler('P')
P_dx = AliasSampler('P_dx')
H = AliasSampler('H')
H_dx = AliasSampler('H_dx')
F = AliasSampler('F')
F_dx = AliasSampler('F_dx')
G_2_dy = AliasSampler('G_2_dy')
G_2_dy_dx = AliasSampler('G_2_dy_dx')
G_2_arrow = AliasSampler('G_2_arrow')
G_2_arrow_dx = AliasSampler('G_2_arrow_dx')
Bij = BijectionSampler
DyFromDx = UDerFromLDerSampler
Trans = TransformationSampler

def _create_root_network_edge():
    # Create the zero-pole of the network
    root_half_edge = HalfEdge()
    root_half_edge.next = root_half_edge
    root_half_edge.prior = root_half_edge

    # Creates the inf-pole
    root_half_edge_opposite = HalfEdge
    root_half_edge_opposite.next = root_half_edge_opposite
    root_half_edge_opposite.prior = root_half_edge_opposite

    # Link the poles
    root_half_edge.opposite = root_half_edge_opposite
    root_half_edge_opposite.opposite = root_half_edge

    return root_half_edge

def bij_u_atom_to_network(decomp):
    vertices_list = []
    edges_list = []
    root_half_edge = _create_root_network_edge()
    result = NetworkClass(vertices_list, edges_list, root_half_edge)
    assert (decomp.get_u_size() == result.get_u_size())
    assert (decomp.get_l_size() == result.get_l_size())
    return result

def bij_s_decomp_to_network(decomp):
    # decomp has this structure: ((first_network, l_atom), second_network)
    network = decomp.first.first
    network_for_plugging = decomp.second

    # Use the serial merge bijection to merge the networks
    result = NetworkMergeInSeries().merge_networks_in_series(network, network_for_plugging)

    # Check the properties
    assert (decomp.get_u_size() == result.get_u_size())
    assert (decomp.get_l_size() == result.get_l_size())
    return result

def bij_p_decomp1_to_network(decomp):
    # decomp has the structure: (link_graph, [set of networks])
    # get the parallel composition of the networks
    result = bij_p_decomp2_to_network(decomp.second)
    # add link between the poles
    result.edges_list.append(result.root_half_edge)
    assert (decomp.get_u_size() == result.get_u_size())
    assert (decomp.get_l_size() == result.get_l_size())
    return result

def bij_p_decomp2_to_network(decomp):
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

def bij_g_3_arrow_to_network(decomp):
    three_connected_rooted_planar_graph = decomp.first
    # Extract the components from the three connected rooted planar graph
    vertices_list = list(three_connected_rooted_planar_graph.vertices_list)
    edges_list = list(three_connected_rooted_planar_graph.edges_list)
    root_half_edge = three_connected_rooted_planar_graph.root_half_edge
    # Create and return the network.
    return NetworkClass(vertices_list, edges_list, root_half_edge)

def add_root_edge(decomp):
    #return decomp.second
    if isinstance(decomp, ZeroAtomClass):
        return UAtomClass()
    return decomp

def forget_direction_of_root_edge(decomp):
    return UDerivedClass(decomp, None)

two_connected_graph_grammar = DecompositionGrammar()
two_connected_graph_grammar.add_rules(three_connected_graph_grammar.get_rules())
two_connected_graph_grammar.add_rules({
    # networks
    'Link': Bij(U, bij_u_atom_to_network),  # introduce this just for readability
    'D': Link + S + P + H,
    'S': Bij((Link + P + H) * L * D, bij_s_decomp_to_network),
    'P': Bij((Link * SetSampler(1, S + H)), bij_p_decomp1_to_network) + Bij(SetSampler(2, S + H), bij_p_decomp2_to_network),
    'H': Bij(USubsSampler(G_3_arrow, D), bij_g_3_arrow_to_network),

    # l-derived networks
    'D_dx': S_dx + P_dx + H_dx,
    'S_dx': (P_dx + H_dx) * L * D + (U + P + H) * (D + L + D_dx), # todo bijection
    'P_dx': U * (S_dx + H_dx) * SetSampler(0, S + H) + (S_dx + H_dx) * SetSampler(1, S + H), # todo bijection
    'H_dx': USubsSampler(G_3_arrow_dx, D) + D_dx * USubsSampler(G_3_arrow_dy, D_dx),

    # 2 connected planar graphs
    'G_2_arrow': Trans(Z + D, add_root_edge, 'G_2_arrow'), # have to pass target class label to transformation sampler
    'F': L * L * G_2_arrow,
    'G_2_dy': Trans(F, forget_direction_of_root_edge, 'G_2_dy'),
    'G_2_dx': LDerFromUDerSampler(G_2_dy, 2.0),  # see p. 26

    # l-derived 2 connected planar graphs
    'G_2_arrow_dx': Trans(D_dx, add_root_edge, 'G_2_arrow_dx'),
    'F_dx': L * L * G_2_arrow_dx + (L + L) * G_2_arrow, # notice that 2 * L = L + L
    'G_2_dy_dx': Trans(F_dx, forget_direction_of_root_edge, 'G_2_dy_dx'),
    'G_2_dx_dx': LDerFromUDerSampler(G_2_dy_dx, 1.0),  # see 5.5 # todo here we have to somehow convert dy_dx to dx_dy before calling LDerFromUDer
})
two_connected_graph_grammar.init()