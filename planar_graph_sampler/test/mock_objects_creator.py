# -*- coding: utf-8 -*-
#    Copyright (C) 2018 by
#    Marta Grobelna <marta.grobelna@rwth-aachen.de>
#    Petre Petrov <petrepp4@gmail.com>
#    Rudi Floren <rudi.floren@gmail.com>
#    Tobias Winkler <tobias.winkler1@rwth-aachen.de>
#    All rights reserved.
#    BSD license.
#
# Authors:  Marta Grobelna <marta.grobelna@rwth-aachen.de>
#           Petre Petrov <petrepp4@gmail.com>
#           Rudi Floren <rudi.floren@gmail.com>
#           Tobias Winkler <tobias.winkler1@rwth-aachen.de>

from planar_graph_sampler.combinatorial_classes.halfedge import ClosureHalfEdge, HalfEdge
from planar_graph_sampler.combinatorial_classes.network import Network
from planar_graph_sampler.combinatorial_classes.three_connected_graph import EdgeRootedThreeConnectedPlanarGraph


def create_sample_closure_output():
    """Creates sample closure output used for testing the admissibility check, primal and whitney bijections."""
    half_edges = [ClosureHalfEdge() for _ in range(65)]

    # Set node_nrs
    for i in range(1, 5):
        half_edges[i].node_nr = 1
        half_edges[i].color = 'black'
    for i in range(5, 8):
        half_edges[i].node_nr = 6
        half_edges[i].color = 'white'
    for i in range(8, 11):
        half_edges[i].node_nr = 13
        half_edges[i].color = 'black'
    for i in range(11, 15):
        half_edges[i].node_nr = 7
        half_edges[i].color = 'white'
    for i in range(15, 18):
        half_edges[i].node_nr = 8
        half_edges[i].color = 'black'
    for i in range(18, 21):
        half_edges[i].node_nr = 2
        half_edges[i].color = 'white'
    for i in range(21, 24):
        half_edges[i].node_nr = 3
        half_edges[i].color = 'black'
    for i in range(24, 27):
        half_edges[i].node_nr = 9
        half_edges[i].color = 'white'
    for i in range(27, 32):
        half_edges[i].node_nr = 10
        half_edges[i].color = 'black'
    for i in range(32, 35):
        half_edges[i].node_nr = 12
        half_edges[i].color = 'white'
    for i in range(35, 39):
        half_edges[i].node_nr = 5
        half_edges[i].color = 'black'
    for i in range(39, 41):
        half_edges[i].node_nr = 11
        half_edges[i].color = 'white'
    for i in range(41, 45):
        half_edges[i].node_nr = 4
        half_edges[i].color = 'white'

    # Set opposite half-edges
    half_edges[1].opposite = half_edges[5]
    half_edges[5].opposite = half_edges[1]
    half_edges[3].opposite = half_edges[19]
    half_edges[19].opposite = half_edges[3]
    half_edges[4].opposite = half_edges[12]
    half_edges[12].opposite = half_edges[4]
    half_edges[6].opposite = half_edges[8]
    half_edges[8].opposite = half_edges[6]
    half_edges[7].opposite = half_edges[35]
    half_edges[35].opposite = half_edges[7]
    half_edges[9].opposite = half_edges[11]
    half_edges[11].opposite = half_edges[9]
    half_edges[13].opposite = half_edges[15]
    half_edges[15].opposite = half_edges[13]
    half_edges[16].opposite = half_edges[18]
    half_edges[18].opposite = half_edges[16]
    half_edges[17].opposite = half_edges[26]
    half_edges[26].opposite = half_edges[17]
    half_edges[14].opposite = half_edges[31]
    half_edges[31].opposite = half_edges[14]
    half_edges[10].opposite = half_edges[34]
    half_edges[34].opposite = half_edges[10]
    half_edges[32].opposite = half_edges[30]
    half_edges[30].opposite = half_edges[32]
    half_edges[33].opposite = half_edges[36]
    half_edges[36].opposite = half_edges[33]
    half_edges[39].opposite = half_edges[37]
    half_edges[37].opposite = half_edges[39]
    half_edges[29].opposite = half_edges[40]
    half_edges[40].opposite = half_edges[29]
    half_edges[27].opposite = half_edges[25]
    half_edges[25].opposite = half_edges[27]
    half_edges[21].opposite = half_edges[20]
    half_edges[20].opposite = half_edges[21]
    half_edges[23].opposite = half_edges[24]
    half_edges[24].opposite = half_edges[23]
    half_edges[28].opposite = half_edges[43]
    half_edges[43].opposite = half_edges[28]
    half_edges[38].opposite = half_edges[42]
    half_edges[42].opposite = half_edges[38]
    half_edges[44].opposite = half_edges[22]
    half_edges[22].opposite = half_edges[44]
    # Set prior and next
    half_edges[1].prior = half_edges[3]
    half_edges[3].next = half_edges[1]
    half_edges[3].prior = half_edges[4]
    half_edges[4].next = half_edges[3]
    half_edges[4].prior = half_edges[1]
    half_edges[1].next = half_edges[4]
    half_edges[5].prior = half_edges[6]
    half_edges[6].next = half_edges[5]
    half_edges[6].prior = half_edges[7]
    half_edges[7].next = half_edges[6]
    half_edges[7].prior = half_edges[5]
    half_edges[5].next = half_edges[7]
    half_edges[8].prior = half_edges[9]
    half_edges[9].next = half_edges[8]
    half_edges[9].prior = half_edges[10]
    half_edges[10].next = half_edges[9]
    half_edges[10].prior = half_edges[8]
    half_edges[8].next = half_edges[10]
    half_edges[11].prior = half_edges[12]
    half_edges[12].next = half_edges[11]
    half_edges[12].prior = half_edges[13]
    half_edges[13].next = half_edges[12]
    half_edges[13].prior = half_edges[14]
    half_edges[14].next = half_edges[13]
    half_edges[14].prior = half_edges[11]
    half_edges[11].next = half_edges[14]
    half_edges[15].prior = half_edges[16]
    half_edges[16].next = half_edges[15]
    half_edges[16].prior = half_edges[17]
    half_edges[17].next = half_edges[16]
    half_edges[17].prior = half_edges[15]
    half_edges[15].next = half_edges[17]
    half_edges[18].prior = half_edges[19]
    half_edges[19].next = half_edges[18]
    half_edges[19].prior = half_edges[20]
    half_edges[20].next = half_edges[19]
    half_edges[20].prior = half_edges[18]
    half_edges[18].next = half_edges[20]
    half_edges[21].prior = half_edges[22]
    half_edges[22].next = half_edges[21]
    half_edges[22].prior = half_edges[23]
    half_edges[23].next = half_edges[22]
    half_edges[23].prior = half_edges[21]
    half_edges[21].next = half_edges[23]
    half_edges[24].prior = half_edges[25]
    half_edges[25].next = half_edges[24]
    half_edges[25].prior = half_edges[26]
    half_edges[26].next = half_edges[25]
    half_edges[26].prior = half_edges[24]
    half_edges[24].next = half_edges[26]
    half_edges[27].prior = half_edges[28]
    half_edges[28].next = half_edges[27]
    half_edges[28].prior = half_edges[29]
    half_edges[29].next = half_edges[28]
    half_edges[29].prior = half_edges[30]
    half_edges[30].next = half_edges[29]
    half_edges[30].prior = half_edges[31]
    half_edges[31].next = half_edges[30]
    half_edges[31].prior = half_edges[27]
    half_edges[27].next = half_edges[31]
    half_edges[32].prior = half_edges[33]
    half_edges[33].next = half_edges[32]
    half_edges[33].prior = half_edges[34]
    half_edges[34].next = half_edges[33]
    half_edges[34].prior = half_edges[32]
    half_edges[32].next = half_edges[34]
    half_edges[35].prior = half_edges[36]
    half_edges[36].next = half_edges[35]
    half_edges[36].prior = half_edges[37]
    half_edges[37].next = half_edges[36]
    half_edges[37].prior = half_edges[38]
    half_edges[38].next = half_edges[37]
    half_edges[38].prior = half_edges[35]
    half_edges[35].next = half_edges[38]
    half_edges[39].prior = half_edges[40]
    half_edges[40].next = half_edges[39]
    half_edges[40].prior = half_edges[39]
    half_edges[39].next = half_edges[40]
    half_edges[42].prior = half_edges[43]
    half_edges[43].next = half_edges[42]
    half_edges[43].prior = half_edges[44]
    half_edges[44].next = half_edges[43]
    half_edges[44].prior = half_edges[42]
    half_edges[42].next = half_edges[44]

    # Mark the half edges from the hexagon
    half_edges[3].is_hexagonal = True
    half_edges[19].is_hexagonal = True
    half_edges[20].is_hexagonal = True
    half_edges[21].is_hexagonal = True
    half_edges[22].is_hexagonal = True
    half_edges[44].is_hexagonal = True
    half_edges[42].is_hexagonal = True
    half_edges[38].is_hexagonal = True
    half_edges[35].is_hexagonal = True
    half_edges[7].is_hexagonal = True
    half_edges[5].is_hexagonal = True
    half_edges[1].is_hexagonal = True

    return half_edges


def create_specific_closure_output_for_admissibility_check_test():
    half_edges = [ClosureHalfEdge() for _ in range(27)]

    for i in range(1, 3):
        half_edges[i].node_nr = 0
        half_edges[i].color = 'black'
    for i in range(3, 7):
        half_edges[i].node_nr = 5
        half_edges[i].color = 'white'
    for i in range(7, 10):
        half_edges[i].node_nr = 3
        half_edges[i].color = 'black'
    for i in range(10, 13):
        half_edges[i].node_nr = 9
        half_edges[i].color = 'white'
    for i in range(13, 15):
        half_edges[i].node_nr = 6
        half_edges[i].color = 'black'
    for i in range(15, 18):
        half_edges[i].node_nr = 2
        half_edges[i].color = 'black'
    for i in range(18, 21):
        half_edges[i].node_nr = 4
        half_edges[i].color = 'white'
    for i in range(21, 24):
        half_edges[i].node_nr = 7
        half_edges[i].color = 'white'
    for i in range(24, 27):
        half_edges[i].node_nr = 8
        half_edges[i].color = 'black'

    # Set up the next and prior pointers.
    half_edges[1].next = half_edges[2]
    half_edges[2].prior = half_edges[1]
    half_edges[2].next = half_edges[1]
    half_edges[1].prior = half_edges[2]
    half_edges[3].next = half_edges[4]
    half_edges[4].prior = half_edges[3]
    half_edges[4].next = half_edges[5]
    half_edges[5].prior = half_edges[4]
    half_edges[5].next = half_edges[6]
    half_edges[6].prior = half_edges[5]
    half_edges[6].next = half_edges[3]
    half_edges[3].prior = half_edges[6]
    half_edges[7].next = half_edges[8]
    half_edges[8].prior = half_edges[7]
    half_edges[8].next = half_edges[9]
    half_edges[9].prior = half_edges[8]
    half_edges[9].next = half_edges[7]
    half_edges[7].prior = half_edges[9]
    half_edges[10].next = half_edges[11]
    half_edges[11].prior = half_edges[10]
    half_edges[11].next = half_edges[12]
    half_edges[12].prior = half_edges[11]
    half_edges[12].next = half_edges[10]
    half_edges[10].prior = half_edges[12]
    half_edges[13].next = half_edges[14]
    half_edges[14].prior = half_edges[13]
    half_edges[14].next = half_edges[13]
    half_edges[13].prior = half_edges[14]
    half_edges[15].next = half_edges[16]
    half_edges[16].prior = half_edges[15]
    half_edges[16].next = half_edges[17]
    half_edges[17].prior = half_edges[16]
    half_edges[17].next = half_edges[15]
    half_edges[15].prior = half_edges[17]
    half_edges[18].next = half_edges[19]
    half_edges[19].prior = half_edges[18]
    half_edges[19].next = half_edges[20]
    half_edges[20].prior = half_edges[19]
    half_edges[20].next = half_edges[18]
    half_edges[18].prior = half_edges[20]
    half_edges[21].next = half_edges[22]
    half_edges[22].prior = half_edges[21]
    half_edges[22].next = half_edges[23]
    half_edges[23].prior = half_edges[22]
    half_edges[23].next = half_edges[21]
    half_edges[21].prior = half_edges[23]
    half_edges[24].next = half_edges[25]
    half_edges[25].prior = half_edges[24]
    half_edges[25].next = half_edges[26]
    half_edges[26].prior = half_edges[25]
    half_edges[26].next = half_edges[24]
    half_edges[24].prior = half_edges[26]

    # Set up the opposite pointers
    half_edges[1].opposite = half_edges[3]
    half_edges[3].opposite = half_edges[1]
    half_edges[2].opposite = half_edges[10]
    half_edges[10].opposite = half_edges[2]
    half_edges[4].opposite = half_edges[7]
    half_edges[7].opposite = half_edges[4]
    half_edges[5].opposite = half_edges[15]
    half_edges[15].opposite = half_edges[5]
    half_edges[6].opposite = half_edges[13]
    half_edges[13].opposite = half_edges[6]
    half_edges[8].opposite = half_edges[12]
    half_edges[12].opposite = half_edges[8]
    half_edges[9].opposite = half_edges[18]
    half_edges[18].opposite = half_edges[9]
    half_edges[11].opposite = half_edges[24]
    half_edges[24].opposite = half_edges[11]
    half_edges[14].opposite = half_edges[21]
    half_edges[21].opposite = half_edges[14]
    half_edges[16].opposite = half_edges[20]
    half_edges[20].opposite = half_edges[16]
    half_edges[17].opposite = half_edges[22]
    half_edges[22].opposite = half_edges[17]
    half_edges[19].opposite = half_edges[26]
    half_edges[26].opposite = half_edges[19]
    half_edges[23].opposite = half_edges[25]
    half_edges[25].opposite = half_edges[23]

    # Set up is_hexagonal property
    half_edges[1].is_hexagonal = True
    half_edges[2].is_hexagonal = True
    half_edges[3].is_hexagonal = True
    half_edges[6].is_hexagonal = True
    half_edges[13].is_hexagonal = True
    half_edges[14].is_hexagonal = True
    half_edges[21].is_hexagonal = True
    half_edges[23].is_hexagonal = True
    half_edges[25].is_hexagonal = True
    half_edges[24].is_hexagonal = True
    half_edges[11].is_hexagonal = True
    half_edges[10].is_hexagonal = True

    return half_edges


def create_three_connected_graph(lowest_node_number=0):
    """Creates a three connected graph used for testing the network operations."""
    first_net_vertices_list = []
    first_net_edges_list = []

    first_net_root_edge = HalfEdge()
    first_net_root_edge.node_nr = 1 + lowest_node_number

    first_net_root_edge_opposite = HalfEdge()
    first_net_root_edge_opposite.node_nr = 2 + lowest_node_number
    first_net_root_edge.opposite = first_net_root_edge_opposite
    first_net_root_edge_opposite.opposite = first_net_root_edge

    third = HalfEdge()
    third.node_nr = 1 + lowest_node_number
    first_net_root_edge.next = third
    first_net_root_edge.prior = third
    third.prior = first_net_root_edge
    third.next = first_net_root_edge
    first_net_edges_list.append(third)

    fourth = HalfEdge()
    fourth.node_nr = 3 + lowest_node_number
    third.opposite = fourth
    fourth.opposite = third
    first_net_vertices_list.append(fourth)

    fifth = HalfEdge()
    fifth.node_nr = 3 + lowest_node_number
    fifth.prior = fourth
    fourth.next = fifth
    first_net_edges_list.append(fifth)

    sixth = HalfEdge()
    sixth.node_nr = 3 + lowest_node_number
    sixth.next = fourth
    fourth.prior = sixth
    sixth.prior = fifth
    fifth.next = sixth
    first_net_edges_list.append(sixth)

    seventh = HalfEdge()
    seventh.node_nr = 4 + lowest_node_number
    seventh.opposite = fifth
    fifth.opposite = seventh
    first_net_vertices_list.append(seventh)

    eighth = HalfEdge()
    eighth.node_nr = 4 + lowest_node_number
    eighth.next = seventh
    eighth.prior = seventh
    seventh.next = eighth
    seventh.prior = eighth
    first_net_edges_list.append(eighth)

    ninth = HalfEdge()
    ninth.node_nr = 2 + lowest_node_number
    ninth.opposite = eighth
    eighth.opposite = ninth
    ninth.next = first_net_root_edge_opposite
    first_net_root_edge_opposite.prior = ninth

    tenth = HalfEdge()
    tenth.node_nr = 2 + lowest_node_number
    tenth.opposite = sixth
    sixth.opposite = tenth
    tenth.next = ninth
    ninth.prior = tenth
    tenth.prior = first_net_root_edge_opposite
    first_net_root_edge_opposite.next = tenth

    return EdgeRootedThreeConnectedPlanarGraph(first_net_root_edge)


def create_sample_network_for_testing_merge_operations(lowest_node_nr=0, is_linked=False):
    graph = create_three_connected_graph(lowest_node_nr)
    return Network(graph.half_edge, is_linked)


def create_sample_network_for_testing_substitution_operation(is_linked=False):
    network_root_edge = HalfEdge()
    network_root_edge.node_nr = 11

    network_root_edge_opposite = HalfEdge()
    network_root_edge_opposite.node_nr = 13
    network_root_edge.opposite = network_root_edge_opposite
    network_root_edge_opposite.opposite = network_root_edge

    net_second = HalfEdge()
    net_second.node_nr = 11
    net_second.prior = network_root_edge
    network_root_edge.next = net_second

    net_third = HalfEdge()
    net_third.node_nr = 12
    net_second.opposite = net_third
    net_third.opposite = net_second

    net_fourth = HalfEdge()
    net_fourth.node_nr = 12
    net_fourth.prior = net_third
    net_fourth.next = net_third
    net_third.next = net_fourth
    net_third.prior = net_fourth

    net_fifth = HalfEdge()
    net_fifth.node_nr = 13
    net_fifth.opposite = net_fourth
    net_fourth.opposite = net_fifth
    net_fifth.next = network_root_edge_opposite
    network_root_edge_opposite.prior = net_fifth

    net_seventh = HalfEdge()
    net_seventh.node_nr = 11
    net_seventh.prior = net_second
    net_second.next = net_seventh
    net_seventh.next = network_root_edge
    network_root_edge.prior = net_seventh

    net_eighth = HalfEdge()
    net_eighth.node_nr = 14
    net_eighth.opposite = net_seventh
    net_seventh.opposite = net_eighth

    net_nineth = HalfEdge()
    net_nineth.node_nr = 14
    net_nineth.prior = net_eighth
    net_eighth.next = net_nineth
    net_nineth.next = net_eighth
    net_eighth.prior = net_nineth

    net_tenth = HalfEdge()
    net_tenth.node_nr = 13
    net_tenth.prior = network_root_edge_opposite
    network_root_edge_opposite.next = net_tenth
    net_tenth.next = net_fifth
    net_fifth.prior = net_tenth
    net_tenth.opposite = net_nineth
    net_nineth.opposite = net_tenth

    return Network(network_root_edge, is_linked)

def create_sample_binary_tree():

    half_edges = [ClosureHalfEdge() for _ in range(24)]

    half_edges[0].node_nr = 0
    half_edges[0].color = 'black'
    half_edges[0].next = half_edges[1]
    half_edges[0].prior = half_edges[5]
    half_edges[0].opposite = None

    half_edges[1].node_nr = 0
    half_edges[1].color = 'black'
    half_edges[1].next = half_edges[5]
    half_edges[1].prior = half_edges[0]
    half_edges[1].opposite = half_edges[2]

    half_edges[2].node_nr = 1
    half_edges[2].color = 'white'
    half_edges[2].next = half_edges[3]
    half_edges[2].prior = half_edges[4]
    half_edges[2].opposite = half_edges[1]

    half_edges[3].node_nr = 1
    half_edges[3].color = 'white'
    half_edges[3].next = half_edges[4]
    half_edges[3].prior = half_edges[2]
    half_edges[3].opposite = None

    half_edges[4].node_nr = 1
    half_edges[4].color = 'white'
    half_edges[4].next = half_edges[2]
    half_edges[4].prior = half_edges[3]
    half_edges[4].opposite = None

    half_edges[5].node_nr = 0
    half_edges[5].color = 'black'
    half_edges[5].next = half_edges[0]
    half_edges[5].prior = half_edges[1]
    half_edges[5].opposite = half_edges[6]
    
    half_edges[6].node_nr = 2
    half_edges[6].color = 'white'
    half_edges[6].next = half_edges[7]
    half_edges[6].prior = half_edges[14]
    half_edges[6].opposite = half_edges[5]

    half_edges[7].node_nr = 2
    half_edges[7].color = 'white'
    half_edges[7].next = half_edges[14]
    half_edges[7].prior = half_edges[6]
    half_edges[7].opposite = half_edges[8]

    half_edges[8].node_nr = 3
    half_edges[8].color = 'black'
    half_edges[8].next = half_edges[9]
    half_edges[8].prior = half_edges[10]
    half_edges[8].opposite = half_edges[7]

    half_edges[9].node_nr = 3
    half_edges[9].color = 'black'
    half_edges[9].next = half_edges[10]
    half_edges[9].prior = half_edges[8]
    half_edges[9].opposite = None

    half_edges[10].node_nr = 3
    half_edges[10].color = 'black'
    half_edges[10].next = half_edges[8]
    half_edges[10].prior = half_edges[9]
    half_edges[10].opposite = half_edges[11]

    half_edges[11].node_nr = 5
    half_edges[11].color = 'white'
    half_edges[11].next = half_edges[12]
    half_edges[11].prior = half_edges[13]
    half_edges[11].opposite = half_edges[10]

    half_edges[12].node_nr = 5
    half_edges[12].color = 'white'
    half_edges[12].next = half_edges[13]
    half_edges[12].prior = half_edges[11]
    half_edges[12].opposite = None

    half_edges[13].node_nr = 5
    half_edges[13].color = 'white'
    half_edges[13].next = half_edges[11]
    half_edges[13].prior = half_edges[12]
    half_edges[13].opposite = None

    half_edges[14].node_nr = 2
    half_edges[14].color = 'white'
    half_edges[14].next = half_edges[6]
    half_edges[14].prior = half_edges[7]
    half_edges[14].opposite = half_edges[15]

    half_edges[15].node_nr = 4
    half_edges[15].color = 'black'
    half_edges[15].next = half_edges[16]
    half_edges[15].prior = half_edges[17]
    half_edges[15].opposite = half_edges[14]

    half_edges[16].node_nr = 4
    half_edges[16].color = 'black'
    half_edges[16].next = half_edges[17]
    half_edges[16].prior = half_edges[15]
    half_edges[16].opposite = None

    half_edges[17].node_nr = 4
    half_edges[17].color = 'black'
    half_edges[17].next = half_edges[15]
    half_edges[17].prior = half_edges[16]
    half_edges[17].opposite = half_edges[18]

    half_edges[18].node_nr = 6
    half_edges[18].color = 'white'
    half_edges[18].next = half_edges[19]
    half_edges[18].prior = half_edges[23]
    half_edges[18].opposite = half_edges[17]

    half_edges[19].node_nr = 6
    half_edges[19].color = 'white'
    half_edges[19].next = half_edges[23]
    half_edges[19].prior = half_edges[18]
    half_edges[19].opposite = half_edges[20]

    half_edges[20].node_nr = 7
    half_edges[20].color = 'black'
    half_edges[20].next = half_edges[21]
    half_edges[20].prior = half_edges[22]
    half_edges[20].opposite = half_edges[19]

    half_edges[21].node_nr = 7
    half_edges[21].color = 'black'
    half_edges[21].next = half_edges[22]
    half_edges[21].prior = half_edges[20]
    half_edges[21].opposite = None

    half_edges[22].node_nr = 7
    half_edges[22].color = 'black'
    half_edges[22].next = half_edges[20]
    half_edges[22].prior = half_edges[21]
    half_edges[22].opposite = None

    half_edges[23].node_nr = 6
    half_edges[23].color = 'white'
    half_edges[23].next = half_edges[18]
    half_edges[23].prior = half_edges[19]
    half_edges[23].opposite = None

    return half_edges[0]
