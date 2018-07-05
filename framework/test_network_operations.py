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

    graph_root_edge_opposite = HalfEdge

    graph_root_edge.opposite = graph_root_edge_opposite
    graph_root_edge_opposite.opposite = graph_root_edge

    third = HalfEdge()
    graph_root_edge.next = third
    graph_root_edge.prior = third
    third.prior = graph_root_edge
    third.next = graph_root_edge
    graph_edges_list.append(third)

    fourth = HalfEdge()
    third.opposite = fourth
    fourth.opposite = third
    graph_vertices_list.append(fourth)

    fifth = HalfEdge()
    fifth.prior = fourth
    fourth.next = fifth
    graph_edges_list.append(fifth)

    sixth = HalfEdge()
    sixth.next = fourth
    fourth.prior = sixth
    sixth.prior = fifth
    fifth.next = sixth
    graph_edges_list.append(sixth)

    seventh = HalfEdge()
    seventh.opposite = fifth
    fifth.opposite = seventh
    graph_vertices_list.append(seventh)

    eighth = HalfEdge()
    eighth.next = seventh
    eighth.prior = seventh
    seventh.next = eighth
    seventh.prior = eighth
    graph_edges_list.append(eighth)

    ninth = HalfEdge()
    ninth.opposite = eighth
    eighth.opposite = ninth
    ninth.next = graph_root_edge_opposite
    graph_root_edge_opposite.prior = ninth

    tenth = HalfEdge()
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

    network_root_edge_opposite = HalfEdge()
    network_root_edge.opposite = network_root_edge_opposite
    network_root_edge_opposite.opposite = network_root_edge

    net_second = HalfEdge()
    net_second.prior = network_root_edge
    net_second.next = network_root_edge
    network_root_edge.next = net_second
    network_root_edge.prior = net_second
    network_edges_list.append(net_second)

    net_third = HalfEdge()
    net_second.opposite = net_third
    net_third.opposite = net_second
    network_vertices_list.append(net_third)

    net_fourth = HalfEdge()
    net_fourth.prior = net_third
    net_fourth.next = net_third
    net_third.next = net_fourth
    net_third.prior = net_fourth
    network_edges_list.append(net_fourth)

    net_fifth = HalfEdge()
    net_fifth.opposite = net_fourth
    net_fourth.opposite = net_fifth
    net_fifth.next = network_root_edge_opposite
    net_fifth.prior = network_root_edge_opposite
    network_root_edge_opposite.prior = net_fifth
    network_root_edge_opposite.next = net_fifth

    net_seventh = HalfEdge()
    net_seventh.prior = net_second
    net_second.next = net_seventh
    net_seventh.next = network_root_edge
    network_root_edge.prior = net_seventh
    network_edges_list.append(net_seventh)

    net_eighth = HalfEdge()
    net_eighth.opposite = net_seventh
    net_seventh.opposite = net_eighth
    network_vertices_list.append(net_eighth)

    net_nineth = HalfEdge()
    net_nineth.prior = net_eighth
    net_eighth.next = net_nineth
    net_nineth.next = net_eighth
    net_eighth.prior = net_nineth
    network_edges_list.append(net_nineth)

    net_tenth = HalfEdge()
    net_tenth.prior = network_root_edge_opposite
    network_root_edge_opposite.next = net_tenth
    net_tenth.next = net_fifth
    net_fifth.prior = net_tenth
    net_tenth.opposite = net_nineth
    net_nineth.opposite = net_tenth


    network = NetworkClass(network_vertices_list, network_edges_list, network_root_edge)

    edge_for_substitution = fifth
    EdgeByNetworkSubstitution().substitute_edge_by_network(three_connected_graph, edge_for_substitution, network)
    # Check vertices
    assert len(three_connected_graph.vertices_list) == 4

    # Check Edges
    assert len(three_connected_graph.edges_list) == 7
    # First node with zero pole merging
    assert fifth.opposite == net_third
    assert net_third.opposite == fifth
    assert sixth.prior == net_seventh
    assert net_seventh.next == sixth
    assert fifth.next == net_seventh
    assert net_seventh.prior == fifth

    # Second node with inf-pole merging
    assert seventh.opposite == net_nineth
    assert net_nineth.opposite == seventh
    assert eighth.prior == net_fifth
    assert net_fifth.next == eighth
    assert seventh.next == net_fifth
    assert net_fifth.prior == seventh


if __name__ == "__main__":
    test_edge_by_netwrok_substitution()