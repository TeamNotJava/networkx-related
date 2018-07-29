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

from planar_graph_sampler.bijections.primal_map import primal_map
from planar_graph_sampler.combinatorial_classes.dissection import IrreducibleDissection
from planar_graph_sampler.bijections.whitney_3map_to_3graph import whitney
from planar_graph_sampler.rejections.admissibility_check import AdmissibilityChecker
from planar_graph_sampler.test.mock_objects_creator import create_sample_closure_output

def test_admissibility_check():
    '''
    Tests the admissibility check for a closure output.
    :return:
    '''
    half_edges_list = create_sample_closure_output()

    is_admissible = AdmissibilityChecker().check_admissibility(half_edges_list[1])
    assert False == is_admissible

    # Test with removing edges
    half_edges_list[27].prior = half_edges_list[29]
    half_edges_list[29].next = half_edges_list[27]

    half_edges_list[42].prior = half_edges_list[44]
    half_edges_list[44].next = half_edges_list[42]

    is_admissible = AdmissibilityChecker().check_admissibility(half_edges_list[1])
    assert True == is_admissible

    # Extend the test with adding edges
    half_edges_list[60].node_nr = 3
    half_edges_list[22].prior = half_edges_list[60]
    half_edges_list[60].next = half_edges_list[22]
    half_edges_list[60].prior = half_edges_list[23]
    half_edges_list[23].next = half_edges_list[60]

    half_edges_list[55].node_nr = 5
    half_edges_list[37].prior = half_edges_list[55]
    half_edges_list[55].next = half_edges_list[37]
    half_edges_list[55].prior = half_edges_list[38]
    half_edges_list[38].next = half_edges_list[55]

    half_edges_list[59].node_nr = 10
    half_edges_list[27].prior = half_edges_list[59]
    half_edges_list[59].next = half_edges_list[27]
    half_edges_list[59].prior = half_edges_list[28]
    half_edges_list[28].next = half_edges_list[59]
    half_edges_list[28].prior = half_edges_list[29]
    half_edges_list[29].next = half_edges_list[28]

    half_edges_list[42].prior = half_edges_list[43]
    half_edges_list[44].next = half_edges_list[43]

    for i in range(49, 52): half_edges_list[i].node_nr = 14
    for i in range(52, 55): half_edges_list[i].node_nr = 16
    for i in range(56, 59): half_edges_list[i].node_nr = 15

    # Reassign opposites
    half_edges_list[28].opposite = half_edges_list[54]
    half_edges_list[54].opposite = half_edges_list[28]
    half_edges_list[60].opposite = half_edges_list[56]
    half_edges_list[56].opposite = half_edges_list[60]
    half_edges_list[59].opposite = half_edges_list[58]
    half_edges_list[58].opposite = half_edges_list[59]
    half_edges_list[50].opposite = half_edges_list[57]
    half_edges_list[57].opposite = half_edges_list[50]
    half_edges_list[43].opposite = half_edges_list[51]
    half_edges_list[51].opposite = half_edges_list[43]
    half_edges_list[49].opposite = half_edges_list[52]
    half_edges_list[52].opposite = half_edges_list[49]
    half_edges_list[55].opposite = half_edges_list[53]
    half_edges_list[53].opposite = half_edges_list[55]

    is_admissible = AdmissibilityChecker().check_admissibility(half_edges_list[1])
    assert True == is_admissible

def test_primal_map():
    '''
    Test the primal map bijection.
    :return:
    '''
    # print("Start test...")
    half_edges = create_sample_closure_output()

    three_map = primal_map(IrreducibleDissection(half_edges[1]))

    # Check the opposites - third output
    assert three_map.opposite.node_nr == 5
    assert three_map.opposite.opposite.node_nr == 1
    assert three_map.next.opposite.node_nr == 13
    assert three_map.next.opposite.opposite.node_nr == 1
    assert three_map.next.next.opposite.node_nr == 8
    assert three_map.next.next.opposite.opposite.node_nr == 1
    assert three_map.next.next.next.opposite.node_nr == 3
    assert three_map.next.next.next.opposite.opposite.node_nr == 1
    assert three_map.next.next.opposite.next.opposite.node_nr == 10
    assert three_map.next.next.opposite.next.opposite.opposite.node_nr == 8
    assert three_map.next.next.opposite.next.next.opposite.node_nr == 3
    assert three_map.next.next.opposite.next.next.opposite.opposite.node_nr == 8
    assert three_map.next.next.opposite.next.opposite.next.opposite.node_nr == 13
    assert three_map.next.next.opposite.next.opposite.next.opposite.opposite.node_nr == 10
    assert three_map.next.next.opposite.next.opposite.next.next.opposite.node_nr == 5
    assert three_map.next.next.opposite.next.opposite.next.next.opposite.opposite.node_nr == 10


def test_whitney_bijection():
    '''
    Tests the whitney bijection with the prepared output from the primal bijection.
    :return:
    '''
    # print("Start test...")
    half_edges = create_sample_closure_output()

    # Make the primal map bijection
    three_map = primal_map(IrreducibleDissection(half_edges[1]))

    # Make the Whiney bijection
    edge_rooted_three_connected_graph = whitney(three_map)

    # Chech the properties
    print(edge_rooted_three_connected_graph)
    # Check the root edge
    assert edge_rooted_three_connected_graph.root_half_edge.node_nr == 1
    assert edge_rooted_three_connected_graph.root_half_edge.opposite.node_nr == 5

    # Check the vertices list
    vertices_node_numbers = [3, 13, 8, 10]
    for vertex_half_edge in edge_rooted_three_connected_graph.vertices_list:
        assert vertex_half_edge.node_nr in vertices_node_numbers
        vertices_node_numbers.remove(vertex_half_edge.node_nr)
    assert len(vertices_node_numbers) == 0

    # Check the edges list
    edges_node_numbers = [(1, 3), (5, 10), (10, 13), (3, 10), (5, 13), (8, 10), (3, 8), (1, 13), (1, 8), (5, 10)]
    for half_edge in edge_rooted_three_connected_graph.edges_list:
        from_vertex = min(half_edge.node_nr, half_edge.opposite.node_nr)
        to_vertex = max(half_edge.node_nr, half_edge.opposite.node_nr)
        assert (from_vertex, to_vertex) in edges_node_numbers
        edges_node_numbers.remove((from_vertex, to_vertex))
    assert len(edges_node_numbers) == 0

