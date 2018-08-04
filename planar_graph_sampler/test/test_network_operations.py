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

from planar_graph_sampler.test.mock_objects_creator import create_three_connected_graph, \
    create_sample_network_for_testing_merge_operations, create_sample_network_for_testing_substitution_operation
from planar_graph_sampler.bijections.networks import *


def test_edge_by_netwrok_substitution():
    """Tests the edge by network substitution operation."""
    three_connected_graph = create_three_connected_graph()
    tcg_fifth = three_connected_graph.root_half_edge.next.opposite.next
    tcg_sixth = tcg_fifth.next
    tcg_seventh = tcg_fifth.opposite
    tcg_eighth = tcg_seventh.next

    network = create_sample_network_for_testing_substitution_operation()
    network_zero_pole = network.zero_pole
    network_inf_pole = network.inf_pole
    net_third = network_zero_pole.next.opposite
    net_fifth = network_inf_pole.prior
    net_seventh = network_zero_pole.prior
    net_nineth = net_seventh.opposite.next

    edge_for_substitution = tcg_fifth
    substitute_edge_by_network(edge_for_substitution, network)

    # Check vertices
    assert three_connected_graph.l_size == 4
    # Check Edges
    assert three_connected_graph.u_size == 7

    # First node with zero pole merging
    assert tcg_fifth.opposite == net_third
    assert net_third.opposite == tcg_fifth
    assert tcg_sixth.prior == net_seventh
    assert net_seventh.next == tcg_sixth
    assert tcg_fifth.next == net_seventh
    assert net_seventh.prior == tcg_fifth

    # Second node with inf-pole merging
    assert tcg_seventh.opposite == net_nineth
    assert net_nineth.opposite == tcg_seventh
    assert tcg_eighth.prior == net_fifth
    assert net_fifth.next == tcg_eighth
    assert tcg_seventh.next == net_fifth
    assert net_fifth.prior == tcg_seventh

    # Check the node numbers updates
    half_edge_walker = edge_for_substitution.next
    assert edge_for_substitution.node_nr == 3
    while half_edge_walker != edge_for_substitution:
        assert half_edge_walker.node_nr == edge_for_substitution.node_nr
        half_edge_walker = half_edge_walker.next

    half_edge_walker = tcg_seventh.next
    assert tcg_seventh.node_nr == 4
    while half_edge_walker != tcg_seventh:
        assert half_edge_walker.node_nr == tcg_seventh.node_nr
        half_edge_walker = half_edge_walker.next


def test_series_merge_of_networks():
    """Tests the merging of two networks in series."""
    first_network = create_sample_network_for_testing_merge_operations(0)
    first_net_zero_pole_node_nr = first_network.zero_pole.node_nr
    first_net_inf_pole = first_network.inf_pole
    first_net_inf_pole_next_initial = first_net_inf_pole.next
    first_net_inf_pole_prior_initial = first_net_inf_pole.prior
    expected_node_number = first_net_inf_pole.node_nr

    second_network = create_sample_network_for_testing_merge_operations(10)
    second_net_zero_pole = second_network.zero_pole
    second_net_zero_pole_next_initial = second_net_zero_pole.next
    second_net_zero_pole_edge_prior_initial = second_net_zero_pole.prior
    second_net_inf_pole_node_nr = second_network.inf_pole.node_nr

    series_merged_result = merge_networks_in_series(first_network, second_network)

    # Merge in series result is never linked network
    assert series_merged_result.is_linked is False

    # Check the root edge
    assert series_merged_result.zero_pole.node_nr == first_net_zero_pole_node_nr
    assert series_merged_result.inf_pole.node_nr == second_net_inf_pole_node_nr

    # Check the number of elements in vertices and edges list
    assert series_merged_result.l_size == 5
    assert series_merged_result.u_size == 8

    # Check the the in pointers. The networks are not linked so their poles should be removed.
    assert first_net_inf_pole_next_initial.prior == second_net_zero_pole_edge_prior_initial
    assert second_net_zero_pole_edge_prior_initial.next == first_net_inf_pole_next_initial
    assert first_net_inf_pole_prior_initial.next == second_net_zero_pole_next_initial
    assert second_net_zero_pole_next_initial.prior == first_net_inf_pole_prior_initial

    # Check the node numbers of the merged edge
    assert expected_node_number == 2
    half_edge_walker = first_net_inf_pole_prior_initial.next
    while half_edge_walker != first_net_inf_pole_prior_initial.prior:
        assert half_edge_walker.node_nr == expected_node_number
        half_edge_walker = half_edge_walker.next


def test_series_merge_of_linked_networks():
    """Tests the merging of two networks in series."""
    first_network = create_sample_network_for_testing_merge_operations(0, True)
    first_net_zero_pole_node_nr = first_network.zero_pole.node_nr
    first_net_inf_pole = first_network.inf_pole
    first_net_inf_pole_prior_initial = first_net_inf_pole.prior
    expected_node_number = first_net_inf_pole.node_nr

    second_network = create_sample_network_for_testing_merge_operations(10, True)
    second_net_zero_pole = second_network.zero_pole
    second_net_zero_pole_edge_prior_initial = second_net_zero_pole.prior
    second_net_inf_pole_node_nr = second_network.inf_pole.node_nr

    series_merged_result = merge_networks_in_series(first_network, second_network)

    # Merge in series result is never linked network
    assert series_merged_result.is_linked is False

    # Check the root edge
    assert series_merged_result.zero_pole.node_nr == first_net_zero_pole_node_nr
    assert series_merged_result.inf_pole.node_nr == second_net_inf_pole_node_nr

    # Check the number of elements in vertices and edges list
    assert series_merged_result.l_size == 5
    # The edges between the poles of the networks are kept.
    assert series_merged_result.u_size == 10

    # Check the the in pointers. The networks are linked therefore the half edges between the poles are kept.
    assert first_net_inf_pole.prior == second_net_zero_pole_edge_prior_initial
    assert second_net_zero_pole_edge_prior_initial.next == first_net_inf_pole
    assert first_net_inf_pole_prior_initial.next == second_net_zero_pole
    assert second_net_zero_pole.prior == first_net_inf_pole_prior_initial

    # Check the node numbers of the merged edge
    assert expected_node_number == 2
    half_edge_walker = first_net_inf_pole_prior_initial.next
    while half_edge_walker != first_net_inf_pole_prior_initial.prior:
        assert half_edge_walker.node_nr == expected_node_number
        half_edge_walker = half_edge_walker.next


def test_parallel_merge_of_networks():
    """Tests the merging of two networks in parallel."""
    first_network = create_sample_network_for_testing_merge_operations()
    first_net_zero_pole = first_network.zero_pole
    first_net_zero_pole_prior_initial = first_net_zero_pole.prior
    first_net_inf_pole = first_net_zero_pole.opposite
    first_net_inf_pole_next_initial = first_net_inf_pole.next

    second_network = create_sample_network_for_testing_merge_operations(10)
    second_net_zero_pole = second_network.zero_pole
    second_net_inf_pole = second_network.inf_pole

    second_net_zero_pole_next_initial = second_net_zero_pole.next
    second_net_zero_pole_prior_initial = second_net_zero_pole.prior
    second_net_inf_pole_next_initial = second_net_inf_pole.next
    second_net_inf_pole_prior_initial = second_net_inf_pole.prior

    merge_in_parallel_result = merge_networks_in_parallel(first_network, second_network)

    # Check whether the network is linked. It shouldn't be since both networks used in the operation are not.
    assert merge_in_parallel_result.is_linked is False

    # Check the sizes of the resulted network
    assert merge_in_parallel_result.l_size == 4
    assert merge_in_parallel_result.u_size == 8

    # Check the pointers updates in the zero pole
    assert first_net_zero_pole.prior == second_net_zero_pole_prior_initial
    assert second_net_zero_pole_prior_initial.next == first_net_zero_pole
    assert first_net_zero_pole_prior_initial.next == second_net_zero_pole_next_initial
    assert second_net_zero_pole_next_initial.prior == first_net_zero_pole_prior_initial

    # Check the pointers updates in the inf pole
    assert first_net_inf_pole.next == second_net_inf_pole_next_initial
    assert second_net_inf_pole_next_initial.prior == first_net_inf_pole
    assert first_net_inf_pole_next_initial.prior == second_net_inf_pole_prior_initial
    assert second_net_inf_pole_prior_initial.next == first_net_inf_pole_next_initial

    # Check the node numbers update
    assert first_net_zero_pole.node_nr == 1
    half_edge_walker = first_net_zero_pole.next
    while half_edge_walker != first_net_zero_pole:
        assert half_edge_walker.node_nr == first_net_zero_pole.node_nr
        half_edge_walker = half_edge_walker.next

    assert first_net_inf_pole.node_nr == 2
    half_edge_walker = first_net_inf_pole.next
    while half_edge_walker != first_net_inf_pole:
        assert half_edge_walker.node_nr == first_net_inf_pole.node_nr
        half_edge_walker = half_edge_walker.next


def test_parallel_merge_with_linked_network():
    """Tests the merging of two networks in parallel."""
    first_network = create_sample_network_for_testing_merge_operations(is_linked=True)
    first_net_zero_pole = first_network.zero_pole
    first_net_zero_pole_prior_initial = first_net_zero_pole.prior
    first_net_inf_pole = first_net_zero_pole.opposite
    first_net_inf_pole_next_initial = first_net_inf_pole.next

    second_network = create_sample_network_for_testing_merge_operations(10)
    second_net_zero_pole = second_network.zero_pole
    second_net_inf_pole = second_network.inf_pole

    second_net_zero_pole_next_initial = second_net_zero_pole.next
    second_net_zero_pole_prior_initial = second_net_zero_pole.prior
    second_net_inf_pole_next_initial = second_net_inf_pole.next
    second_net_inf_pole_prior_initial = second_net_inf_pole.prior

    merge_in_parallel_result = merge_networks_in_parallel(first_network, second_network)

    # Check whether the network is linked. First network is linked so the result also should be
    assert merge_in_parallel_result.is_linked is True

    # Check the sizes of the resulted network
    assert merge_in_parallel_result.l_size == 4
    # Since the first network is linked the edge between the poles is counted.
    assert merge_in_parallel_result.u_size == 9

    # Check the pointers updates in the zero pole
    assert first_net_zero_pole.prior == second_net_zero_pole_prior_initial
    assert second_net_zero_pole_prior_initial.next == first_net_zero_pole
    assert first_net_zero_pole_prior_initial.next == second_net_zero_pole_next_initial
    assert second_net_zero_pole_next_initial.prior == first_net_zero_pole_prior_initial

    # Check the pointers updates in the inf pole
    assert first_net_inf_pole.next == second_net_inf_pole_next_initial
    assert second_net_inf_pole_next_initial.prior == first_net_inf_pole
    assert first_net_inf_pole_next_initial.prior == second_net_inf_pole_prior_initial
    assert second_net_inf_pole_prior_initial.next == first_net_inf_pole_next_initial

    # Check the node numbers update
    assert first_net_zero_pole.node_nr == 1
    half_edge_walker = first_net_zero_pole.next
    while half_edge_walker != first_net_zero_pole:
        assert half_edge_walker.node_nr == first_net_zero_pole.node_nr
        half_edge_walker = half_edge_walker.next

    assert first_net_inf_pole.node_nr == 2
    half_edge_walker = first_net_inf_pole.next
    while half_edge_walker != first_net_inf_pole:
        assert half_edge_walker.node_nr == first_net_inf_pole.node_nr
        half_edge_walker = half_edge_walker.next


if __name__ == "__main__":
    test_edge_by_netwrok_substitution()
    test_parallel_merge_of_networks()
    test_parallel_merge_with_linked_network()
    test_series_merge_of_networks()
    test_series_merge_of_linked_networks()
