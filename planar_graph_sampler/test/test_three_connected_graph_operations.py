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

from nose.tools import assert_false, assert_true
from planar_graph_sampler.bijections.primal_map import PrimalMap
from planar_graph_sampler.combinatorial_classes.dissection import IrreducibleDissection
from planar_graph_sampler.combinatorial_classes.three_connected_graph import EdgeRootedThreeConnectedPlanarGraph
from planar_graph_sampler.test.mock_objects_creator import create_sample_closure_output, \
    create_specific_closure_output_for_admissibility_check_test


class TestThreeConnectedGraphOperations(object):
    """Unit tests for the three connected graph operations."""
    def test_admissibility_check(self):
        """
        Tests the admissibility check for a closure output.
        """
        half_edges_list = create_sample_closure_output()

        dissection = IrreducibleDissection(half_edges_list[1])
        assert_false(dissection.is_admissible)

        # Test with removing edges
        half_edges_list[27].prior = half_edges_list[29]
        half_edges_list[29].next = half_edges_list[27]

        half_edges_list[42].prior = half_edges_list[44]
        half_edges_list[44].next = half_edges_list[42]

        assert_true(dissection.is_admissible)

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

        for i in range(49, 52):
            half_edges_list[i].node_nr = 14
        for i in range(52, 55):
            half_edges_list[i].node_nr = 16
        for i in range(56, 59):
            half_edges_list[i].node_nr = 15

        # Add the next and prior pinters
        half_edges_list[49].prior = half_edges_list[50]
        half_edges_list[50].next = half_edges_list[49]
        half_edges_list[50].prior = half_edges_list[51]
        half_edges_list[51].next = half_edges_list[50]
        half_edges_list[51].prior = half_edges_list[49]
        half_edges_list[49].next = half_edges_list[51]
        half_edges_list[52].prior = half_edges_list[53]
        half_edges_list[53].next = half_edges_list[52]
        half_edges_list[53].prior = half_edges_list[54]
        half_edges_list[54].next = half_edges_list[53]
        half_edges_list[54].prior = half_edges_list[52]
        half_edges_list[52].next = half_edges_list[54]
        half_edges_list[56].prior = half_edges_list[57]
        half_edges_list[57].next = half_edges_list[56]
        half_edges_list[57].prior = half_edges_list[58]
        half_edges_list[58].next = half_edges_list[57]
        half_edges_list[58].prior = half_edges_list[56]
        half_edges_list[56].next = half_edges_list[58]

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

        assert_true(dissection.is_admissible)

    def test_admissibility_check_with_initially_wrong_result(self):
        """
        TDD for fixing the bug in admissibility check.
        """
        half_edges = create_specific_closure_output_for_admissibility_check_test()

        dissection = IrreducibleDissection(half_edges[2])
        assert_false(dissection.is_admissible)
        assert_false(dissection.is_admissible_slow)

    def test_primal_map(self):
        """
        Test the primal map bijection.
        """
        half_edges = create_sample_closure_output()
        three_map = PrimalMap().primal_map_bijection(IrreducibleDissection(half_edges[1]).half_edge)

        # Create Three connected graph and corresponding nx graph
        three_connected_graph = EdgeRootedThreeConnectedPlanarGraph(three_map)
        nx_graph = three_connected_graph.to_networkx_graph()

        # Check the edges
        expected_edges_list = [(5, 1), (13, 1), (8, 1), (3, 1), (3, 8), (10, 8), (13, 10), (5, 10)]
        for edge in expected_edges_list:
            assert_true(nx_graph.has_edge(edge[0], edge[1]))
            assert_true(nx_graph.has_edge(edge[1], edge[0]))
