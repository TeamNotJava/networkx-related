# to be used in the Bijection sampler

import networkx as nx
from networkx.algorithms.operators import union, union_all
from networkx.algorithms.minors import contracted_nodes
from ..combinatorial_classes.network import NetworkClass


# creates a link_graph (from a u-atom)
# see sampler for Z_U in figure 9
def u_atom_to_network(u_atom):
    link_graph = nx.Graph()
    zero_pole = 'zero'
    inf_pole = 'inf'
    link_graph.add_edge(zero_pole, inf_pole)
    result = NetworkClass(link_graph, zero_pole, inf_pole)
    assert (u_atom.get_u_size() == result.get_u_size())
    assert (u_atom.get_l_size() == result.get_l_size())
    return result


# serial composition of two networks (head and tail)
# see sampler for S in figure 9
def s_decomp_to_network(decomp):
    # decomp has this structure: ((head, l_atom), tail)
    head = decomp.first.first
    # middle = decomp.first.second  # we actually dont need this!
    tail = decomp.second

    # relabel graphs to make them disjoint
    head.relabel('h')
    tail.relabel('t')
    # will raise exception if not disjoint
    result = union(head, tail)
    # merge zero pole of head and infinity pole of tail
    result = contracted_nodes(result, head.zero_pole, tail.inf_pole)
    assert (decomp.get_u_size() == result.get_u_size())
    assert (decomp.get_l_size() == result.get_l_size())
    return NetworkClass(result, head.inf_pole, tail.zero_pole)


# parallel composition of a set of networks
# also adds link between poles
# see sampler for P_1 in figure 9
def p_decomp1_to_network(decomp):
    # decomp has the structure: (link_graph, [set of networks])
    # get the parallel composition of the networks
    result = p_decomp2_to_network(decomp.second)
    # add link between the poles
    result.graph.add_edge(result.zero_pole, result.inf_pole)
    assert (decomp.get_u_size() == result.get_u_size())
    assert (decomp.get_l_size() == result.get_l_size())
    return result


# parallel composition of a set of networks
# does not link the poles
# see sampler for P_2 in figure 9
def p_decomp2_to_network(decomp):
    # decomp has the structure: [set of networks]
    networks = decomp
    # relabel all networks appending their index to their node labels
    for i in range(len(networks)):
        networks[i].relabel(str(i))
    # union_all takes only disjoint graphs
    result_graph = union_all(networks)
    # finally merge all the zero poles and all the inf poles
    # this can be done much more efficient
    for network in networks:
        # networks[0].zero_pole (inf_pole) is the node label to be kept
        result_graph = contracted_nodes(result_graph, networks[0].zero_pole, network.zero_pole)
        result_graph = contracted_nodes(result_graph, networks[0].inf_pole, network.inf_pole)
    result = NetworkClass(result_graph, networks[0].zero_pole, networks[0].inf_pole)
    assert (decomp.get_u_size() == result.get_u_size())
    assert (decomp.get_l_size() == result.get_l_size())
    return result


def g_3_arrow_to_network(three_connected_rooted_planar_graph):
    # just make the root become the link
    raise NotImplementedError

## and all the derived networks stuff also goes here
