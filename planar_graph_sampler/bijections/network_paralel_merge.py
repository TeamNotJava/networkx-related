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

"""
    Merges two networks in parallel manner.
"""

from planar_graph_sampler.combinatorial_classes.network import Network


class NetworkMergeInParallel:

    def merge_networks_in_parallel(self, network, network_for_plugging):
        """
        Merges the network for plugging into network in parallel which means their respective inf-poles and
        0-poles coincide.

        :param network: first network which will result of the merge operation
        :param network_for_plugging: second network which is plugged in the first one
        """

        assert not (network.is_linked and network_for_plugging.is_linked)


        new_l_size = network.get_l_size() + network_for_plugging.get_l_size()
        new_u_size = network.get_u_size() + network_for_plugging.get_u_size()
        res_is_linked = network.is_linked or network_for_plugging.is_linked

        # Extract the poles from both networks
        first_net_zero_pole_edge = network.get_zero_pole()
        first_net_inf_pole_edge = network.get_inf_pole()

        second_net_zero_pole_edge = network_for_plugging.get_zero_pole()
        second_net_inf_pole_edge = network_for_plugging.get_inf_pole()

        # Merge their 0-poles
        first_net_zero_pole_prior = first_net_zero_pole_edge.prior
        second_net_zero_pole_next = second_net_zero_pole_edge.next
        second_net_zero_pole_prior = second_net_zero_pole_edge.prior
        first_net_zero_pole_edge.prior = second_net_zero_pole_prior
        second_net_zero_pole_prior.next = first_net_zero_pole_edge
        first_net_zero_pole_prior.next = second_net_zero_pole_next
        second_net_zero_pole_next.prior = first_net_zero_pole_prior

        # Update the node numbers in the zero pole
        half_edge_walker = second_net_zero_pole_edge.next
        while half_edge_walker != first_net_zero_pole_edge:
            half_edge_walker.node_nr = first_net_zero_pole_edge.node_nr
            half_edge_walker = half_edge_walker.next

        # Merge their inf-poles
        first_net_inf_pole_next = first_net_inf_pole_edge.next
        second_net_inf_pole_prior = second_net_inf_pole_edge.prior
        second_net_inf_pole_next = second_net_inf_pole_edge.next
        first_net_inf_pole_edge.next = second_net_inf_pole_next
        second_net_inf_pole_next.prior = first_net_inf_pole_edge
        first_net_inf_pole_next.prior = second_net_inf_pole_prior
        second_net_inf_pole_prior.next = first_net_inf_pole_next

        # Update the node numbers in the inf pole
        half_edge_walker = second_net_inf_pole_next
        while half_edge_walker != first_net_inf_pole_next:
            half_edge_walker.node_nr = first_net_inf_pole_edge.node_nr
            half_edge_walker = half_edge_walker.next

        # Add the vertices list from the second network into the first one
        # network.vertices_list += network_for_plugging.vertices_list

        # Add the edges from the second network into the first one
        # network.edges_list += network_for_plugging.edges_list

        return Network(first_net_zero_pole_edge, res_is_linked, new_l_size, new_u_size)
