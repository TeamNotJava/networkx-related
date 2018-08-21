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
from planar_graph_sampler.test.mock_objects_creator import create_sample_binary_tree
from planar_graph_sampler.bijections.closure import Closure
# from framework.generic_samplers import BoltzmannSamplerBase
# from framework.decomposition_grammar import AliasSampler, DecompositionGrammar
# from planar_graph_sampler.grammar.binary_tree_decomposition import binary_tree_grammar
# from planar_graph_sampler.evaluations_planar_graph import EvaluationOracle, planar_graph_evals_n100, planar_graph_evals_n1000


class TestClosure(object):
    """Unit tests for closure of binary trees."""

    def test_partial_closure(self):
        """Checks if the computed partial closure is correct"""

        print("Test partial closure")
        btree_half_edge = create_sample_binary_tree()
        init_half_edge = Closure()._bicolored_partial_closure(btree_half_edge)

        edge_list = init_half_edge.get_all_half_edges()
        stem_list = []

        for edge in edge_list:
            if edge.opposite is None:
                stem_list.append(edge)

        # Check for each stem if it has at most two full edges as successors
        for stem in stem_list:
            count = 0
            current_half_edge = stem
            while True:
                current_half_edge = current_half_edge.next
                if current_half_edge is stem:
                    break
                if current_half_edge.opposite is not None:
                    current_half_edge = current_half_edge.opposite
                    count = count + 1
                    assert_true(count < 3, "A half-edge has more than 2 full successor edges")
                else:
                    break

    def test_connections_between_half_edges(self):
        """Checks if the connections between the edges are correct."""
        
        btree_half_edge = create_sample_binary_tree()
        init_half_edge = Closure()._bicolored_complete_closure(btree_half_edge)

        edge_list = init_half_edge.get_all_half_edges()
        nodes = init_half_edge.node_dict()
        hex_half_edge = None
        num_hex_half_edges = 0
        for edge in edge_list:
            if edge.is_hexagonal:
                num_hex_half_edges += 1
            if hex_half_edge is None and edge.is_hexagonal \
                    and edge.prior.is_hexagonal:
                hex_half_edge = edge
            assert_true(edge is edge.next.prior)
            assert_true(edge is edge.prior.next)
            assert_true(edge is edge.opposite.opposite)
            assert_true(edge.opposite is not None)

        assert_true(num_hex_half_edges == 12)

        # Test if the outer face is a hexagon
        curr_half_edge = hex_half_edge
        assert_true(curr_half_edge.is_hexagonal)
        hex_edges = 0
        while True:
            curr_half_edge = curr_half_edge.opposite
            assert_true(curr_half_edge.is_hexagonal)
            if curr_half_edge == hex_half_edge:
                break
            curr_half_edge = curr_half_edge.next
            assert_true(curr_half_edge.is_hexagonal)
            if curr_half_edge == hex_half_edge:
                break
            hex_edges += 1
        assert_true(hex_edges == 5)

        # Test if every node has at most two hexagonal edges
        for node in nodes:
            half_edges = nodes[node]
            num_hex = 0
            for e in half_edges:
                if e.is_hexagonal:
                    num_hex += 1
            assert_true(num_hex < 3)

    def test_planarity_of_embedding(self):
        """Checks if half edges at every node are planar."""

        print("Test embedding")
        btree_half_edge = create_sample_binary_tree()
        init_half_edge = Closure()._bicolored_complete_closure(btree_half_edge)
        edge_list = init_half_edge.get_all_half_edges()

        # Check if there are two different edges that have the same
        # prior/next half-edge
        for edge in edge_list:
            for i in edge_list:
                assert_false(id(i) != id(edge) and (i.prior is edge.prior or i.next is edge.next), "Two edges with the same next or prior")


    def test_concrete_btree_partial_closure(self):
        """Tests if the connections in the concret btree are correct after partial closure"""

        print("Test concrete partail closure")
        btree_half_edge = create_sample_binary_tree()
        init_half_edge = Closure()._bicolored_partial_closure(btree_half_edge)

        nodes = init_half_edge.node_dict()

        for n in nodes:
            if n == 0:
                n_half_edges = nodes[n]
                new_edge = False
                for he in n_half_edges:
                    if he.opposite is not None and he.opposite.node_nr == 6:
                        new_edge = True
                assert_true(new_edge, "No edge (0,6)")
            if n == 1:
                n_half_edges = nodes[n]
                new_edge = False
                for he in n_half_edges:
                    if he.opposite is not None and he.opposite.node_nr == 3:
                        new_edge = True
                assert_true(new_edge, "No edge (1,3)")
            if n == 3:
                n_half_edges = nodes[n]
                new_edge = False
                for he in n_half_edges:
                    if he.opposite is not None and he.opposite.node_nr == 1:
                        new_edge = True
                assert_true(new_edge, "No edge (3,1)")
            if n == 4:
                n_half_edges = nodes[n]
                new_edge = False
                for he in n_half_edges:
                    if he.opposite is not None and he.opposite.node_nr == 5:
                        new_edge = True
                assert_true(new_edge, "No edge (4,5)")
            if n == 6:
                n_half_edges = nodes[n]
                new_edge = False
                for he in n_half_edges:
                    if he.opposite is not None and he.opposite.node_nr == 0:
                        new_edge = True
                assert_true(new_edge, "No edge (6,0)")

    def test_concrete_btree_complete_closure(self):
        """Tests connections in the concrete binary tree after complet closure"""
    
        print("Test concrete complete closure")
        btree_half_edge = create_sample_binary_tree()
        init_half_edge = Closure()._bicolored_complete_closure(btree_half_edge)

        nodes = init_half_edge.node_dict()
        hexagon_nodes = []
        first_hex = btree_half_edge.opposite
        hexagon_nodes.append(first_hex.node_nr)
        current_half_edge = first_hex.prior.opposite
        while(True):
            if current_half_edge == first_hex.next.next:
                break
            hexagon_nodes.append(current_half_edge.node_nr)
            current_half_edge = current_half_edge.next.opposite

        for n in nodes:
            n_hf = nodes[n]
            test = True
            for i in n_hf:
                # Test only nodes with non hexagonal edges
                if i.is_hexagonal:
                    test = False
            if test:
                if n == 0:
                    n_half_edges = nodes[n]
                    new_edge = False
                    for he in n_half_edges:
                        if he.opposite is not None and he.opposite.node_nr == hexagon_nodes[0]:
                            new_edge = True
                    assert_true(new_edge, "No edge (0,0) (btree,hex)")
                if n == 1:
                    n_half_edges = nodes[n]
                    new_edge = False
                    for he in n_half_edges:
                        if he.opposite is not None and he.opposite.node_nr == hexagon_nodes[1]:
                            new_edge = True
                    assert_true(new_edge, "No edge (1,1) (btree,hex)")
                if n == 3:
                    n_half_edges = nodes[n]
                    new_edge = False
                    for he in n_half_edges:
                        if he.opposite is not None and he.opposite.node_nr == hexagon_nodes[2]:
                            new_edge = True
                    assert_true(new_edge, "No edge (3,2) (btree,hex)")
                if n == 5:
                    n_half_edges = nodes[n]
                    new_edge = False
                    for he in n_half_edges:
                        if he.opposite is not None:
                            print(he.opposite.node_nr)
                        if he.opposite is not None and he.opposite.node_nr == hexagon_nodes[3]:
                            new_edge = True
                    assert_true(new_edge, "No edge (5,3) (btree,hex)")
                if n == 4:
                    n_half_edges = nodes[n]
                    new_edge = False
                    for he in n_half_edges:
                        if he.opposite is not None and he.opposite.node_nr == hexagon_nodes[4]:
                            new_edge = True
                    assert_true(new_edge, "No edge (4,4) (btree,hex)")
                if n == 7:
                    n_half_edges = nodes[n]
                    new_edge_1 = False
                    new_edge_2 = False
                    for he in n_half_edges:
                        if he.opposite is not None and he.opposite.node_nr == hexagon_nodes[4]:
                            new_edge_1 = True
                        if he.opposite is not None and he.opposite.node_nr == hexagon_nodes[0]:
                            new_edge_2 = True
                    assert_true(new_edge_1, "No edge (7,4) (btree,hex)")
                    assert_true(new_edge_2, "No edge (7,0) (btree,hex)")

            for n in  hexagon_nodes:
                if n == hexagon_nodes[0]:
                    n_half_edges = nodes[n]
                    new_edge_1 = False
                    new_edge_2 = False
                    for he in n_half_edges:
                        if he.opposite is not None and he.opposite.node_nr == 7:
                            new_edge_1 = True
                        if he.opposite is not None and he.opposite.node_nr == 0:
                            new_edge_2 = True
                    assert_true(new_edge_1, "No edge (0,7) (hex,btree")
                    assert_true(new_edge_1, "No edge (0,0) (hex,btree")
                if n == hexagon_nodes[1]:
                    n_half_edges = nodes[n]
                    new_edge = False
                    for he in n_half_edges:
                        if he.opposite is not None and he.opposite.node_nr == 1:
                            new_edge = True
                    assert_true(new_edge, "No edge (1,1) (hex,btree")
                if n == hexagon_nodes[2]:
                    n_half_edges = nodes[n]
                    new_edge = False
                    for he in n_half_edges:
                        if he.opposite is not None and he.opposite.node_nr == 3:
                            new_edge = True
                    assert_true(new_edge, "No edge (2,3) (hex,btree")
                if n == hexagon_nodes[3]:
                    n_half_edges = nodes[n]
                    new_edge = False
                    for he in n_half_edges:
                        if he.opposite is not None and he.opposite.node_nr == 5:
                            new_edge = True
                    assert_true(new_edge, "No edge (3,5) (hex,btree")
                if n == hexagon_nodes[4]:
                    n_half_edges = nodes[n]
                    new_edge_1 = False
                    new_edge_2 = False
                    for he in n_half_edges:
                        if he.opposite is not None and he.opposite.node_nr == 4:
                            new_edge_1 = True
                        if he.opposite is not None and he.opposite.node_nr == 7:
                            new_edge_2 = True
                    assert_true(new_edge_1, "No edge (4,4) (hex,btree")
                    assert_true(new_edge_2, "No edge (4,7) (hex,btree")
                







                    


        