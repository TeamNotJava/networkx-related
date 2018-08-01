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
from planar_graph_sampler.combinatorial_classes.three_connected_graph import EdgeRootedThreeConnectedPlanarGraph


def create_sample_closure_output():
    """Creates sample closure output used for testing the admissibility check, primal and whitney bijections."""
    half_edges = [ClosureHalfEdge() for _ in range(65)]

    # Set node_nrs
    for i in range(1, 5): half_edges[i].node_nr = 1
    for i in range(1, 5): half_edges[i].color = 'black'
    for i in range(5, 8): half_edges[i].node_nr = 6
    for i in range(5, 8): half_edges[i].color = 'white'
    for i in range(8, 11): half_edges[i].node_nr = 13
    for i in range(8, 11): half_edges[i].color = 'black'
    for i in range(11, 15): half_edges[i].node_nr = 7
    for i in range(11, 15): half_edges[i].color = 'white'
    for i in range(15, 18): half_edges[i].node_nr = 8
    for i in range(15, 18): half_edges[i].color = 'black'
    for i in range(18, 21): half_edges[i].node_nr = 2
    for i in range(18, 21): half_edges[i].color = 'white'
    for i in range(21, 24): half_edges[i].node_nr = 3
    for i in range(21, 24): half_edges[i].color = 'black'
    for i in range(24, 27): half_edges[i].node_nr = 9
    for i in range(24, 27): half_edges[i].color = 'white'
    for i in range(27, 32): half_edges[i].node_nr = 10
    for i in range(27, 32): half_edges[i].color = 'black'
    for i in range(32, 35): half_edges[i].node_nr = 12
    for i in range(32, 35): half_edges[i].color = 'white'
    for i in range(35, 39): half_edges[i].node_nr = 5
    for i in range(35, 39): half_edges[i].color = 'black'
    for i in range(39, 41): half_edges[i].node_nr = 11
    for i in range(39, 41): half_edges[i].color = 'white'
    for i in range(41, 45): half_edges[i].node_nr = 4
    for i in range(41, 45): half_edges[i].color = 'white'

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
