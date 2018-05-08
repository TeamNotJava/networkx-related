#!/usr/bin/env python
from nose.tools import assert_true, assert_false

import networkx as nx

from planarity_checking import lr_planarity

"""
Unit tests for the :mod:`networkx.algorithms.TODO` module.

Tests three things:
 - Check that the result is correct (returns plar if and only if the graph is actually planar)
 - In case a counter example is retured: Check if it is correct
 - In case an embedding is return: Check if its actually an embedding
 
"""


class TestLRPlanarity:

    def setUp(self):
        self.planar_graphs = []
        self.non_planar_graphs = []

        # Set create the planar and non planar graphs
        G = nx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 6), (6, 7), (7, 1), (1, 5), (5, 2), (2, 4), (4, 5), (5, 7)])
        self.planar_graphs.append(G)

        G = nx.Graph()
        G.add_edges_from([(1, 5), (1, 6), (1, 7), (2, 6), (2, 3), (3, 5), (3, 7), (4, 5), (4, 6), (4, 7)])
        self.non_planar_graphs.append(G)

    def test_correctness_planar(self):
        for planar_graph in self.planar_graphs:
            # Check graph for planarity
            is_planar, result = lr_planarity.check_planarity(planar_graph)
            assert_true(is_planar, "A planar graph was classified as non planar.")

    def test_correctness_non_planar(self):
        for non_planar_graph in self.non_planar_graphs:
            # Check graph for planarity
            is_planar, result = lr_planarity.check_planarity(non_planar_graph)
            assert_false(is_planar, "A non planar graph was classified as planar.")

    def test_goldner_harary(self):
        # goldner-harary graph
        # http://en.wikipedia.org/wiki/Goldner%E2%80%93Harary_graph
        # a maximal planar graph
        e= [(1,2 ),( 1,3 ),( 1,4 ),( 1,5 ),( 1,7 ),( 1,8 ),( 1,10 ),
            ( 1,11 ),( 2,3 ),( 2,4 ),( 2,6 ),( 2,7 ),( 2,9 ),( 2,10 ),
            ( 2,11 ),( 3,4 ),( 4,5 ),( 4,6 ),( 4,7 ),( 5,7 ),( 6,7 ),
            ( 7,8 ),( 7,9 ),( 7,10 ),( 8,10 ),( 9,10 ),( 10,11)]
        G=nx.Graph(e)
        assert_true(is_planar, "Golder-Harary maximal planargraph was classified as planar")
