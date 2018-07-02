from framework.bijections.network_substitution import EdgeByNetworkSubstitution
from framework.bijections.halfedge import  HalfEdge
from framework.combinatorial_classes.network import NetworkClass
from framework.combinatorial_classes.three_connected_graph import EdgeRootedThreeConnectedPlanarGraph

def test_edge_by_netwrok_substitution():
    '''
    Tests the edgy by network substitution operation.
    :return:
    '''

    graph_vertices_list = []
    graph_edges_list = []

    graph_root_edge = HalfEdge()
    graph_root_edge.index=1

    graph_root_edge_opposite = HalfEdge
    graph_root_edge_opposite.index = 2

    graph_root_edge.opposite = graph_root_edge_opposite
    graph_root_edge_opposite.opposite = graph_root_edge

    third = HalfEdge()
    third.index = 13
    graph_root_edge.next = third
    graph_root_edge.prior = third
    third.prior = graph_root_edge
    third.next = graph_root_edge
    graph_edges_list.append(third)

    fourth = HalfEdge()
    graph_root_edge_opposite.index = 4
    third.opposite = fourth
    fourth.opposite = third
    graph_vertices_list.append(fourth)

    fifth = HalfEdge()
    fifth.index = 5
    fifth.prior = fourth
    fourth.next = fifth
    graph_edges_list.append(fifth)
    edge_for_substitution = fifth

    sixth = HalfEdge()
    sixth.index = 6
    sixth.next = fourth
    fourth.prior = sixth
    sixth.prior = fifth
    fifth.next = sixth
    graph_edges_list.append(sixth)

    seventh = HalfEdge()
    seventh.index = 7
    seventh.opposite = fifth
    fifth.opposite = seventh
    graph_vertices_list.append(seventh)

    eighth = HalfEdge()
    eighth.index = 8
    eighth.next = seventh
    eighth.prior = seventh
    seventh.next = eighth
    seventh.prior = eighth
    graph_edges_list.append(eighth)

    ninth = HalfEdge()
    ninth.index = 9
    ninth.opposite = eighth
    eighth.opposite = ninth
    ninth.next = graph_root_edge_opposite
    graph_root_edge_opposite.prior = ninth

    tenth = HalfEdge()
    tenth.index = 10
    tenth.opposite = sixth
    sixth.opposite = tenth
    tenth.next = ninth
    ninth.prior = tenth
    tenth.prior = graph_root_edge_opposite
    graph_root_edge_opposite.next = tenth

    three_connected_graph = EdgeRootedThreeConnectedPlanarGraph(graph_vertices_list, graph_edges_list, graph_root_edge)

    network_edges_list = []
    network_vertices_list = []

    network_root_edge = HalfEdge()
    network_root_edge.index = 1

    network_root_edge_opposite = HalfEdge()
    network_root_edge_opposite.index = 6
    network_root_edge.opposite = network_root_edge_opposite
    network_root_edge_opposite.opposite = network_root_edge

    net_second = HalfEdge()
    net_second.index = 2
    net_second.prior = network_root_edge
    net_second.next = network_root_edge
    network_root_edge.next = net_second
    network_root_edge.prior = net_second
    network_edges_list.append(net_second)

    net_third = HalfEdge()
    net_third.index = 3
    net_second.opposite = net_third
    net_third.opposite = net_second
    network_vertices_list.append(net_third)

    net_fourth = HalfEdge()
    net_fourth.index = 4
    net_fourth.prior = net_third
    net_fourth.next = net_third
    net_third.next = net_fourth
    net_third.prior = net_fourth
    network_edges_list.append(net_fourth)

    net_fifth = HalfEdge()
    net_fifth.index = 5
    net_fifth.opposite = net_fourth
    net_fourth.opposite = net_fifth
    net_fifth.next = network_root_edge_opposite
    net_fifth.prior = network_root_edge_opposite
    network_root_edge_opposite.prior = net_fifth
    network_root_edge_opposite.next = net_fifth

    network = NetworkClass(network_vertices_list, network_edges_list, network_root_edge)

    EdgeByNetworkSubstitution().substitute_edge_by_network(three_connected_graph, edge_for_substitution, network)

if __name__ == "__main__":
    test_edge_by_netwrok_substitution()