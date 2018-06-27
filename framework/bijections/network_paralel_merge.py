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


class NetworkMergeInParallel:

    def merge_networks_in_parallel(self, network, network_for_plugging):
        '''
        Merges the network for plugging into network in parallel which means their respective inf-poles and
        0-poles coincide.

        :param network: first network which will result of the merge operation
        :param network_for_plugging: second network which is plugged in the first one
        '''

        # Extract the poles from both networks
        first_net_zero_pole_edge = network.root_half_edge
        first_net_inf_pole_edge = first_net_zero_pole_edge.opposite

        second_net_zero_pole_edge = network_for_plugging.root_half_edge
        second_net_inf_pole_edge = second_net_zero_pole_edge.opposite

        # Merge their 0-poles
        first_net_zero_pole_prior = first_net_zero_pole_edge.prior
        second_net_zero_pole_next = second_net_zero_pole_edge.next
        second_net_zero_pole_prior = second_net_zero_pole_edge.prior
        first_net_zero_pole_edge.prior = second_net_zero_pole_prior
        second_net_zero_pole_prior.next = first_net_zero_pole_edge
        first_net_zero_pole_prior.next = second_net_zero_pole_next
        second_net_zero_pole_next.prior = first_net_zero_pole_prior

        # Merge their inf-poles
        first_net_inf_pole_next = first_net_inf_pole_edge.next
        second_net_inf_pole_prior = second_net_inf_pole_edge.prior
        second_net_inf_pole_next = second_net_inf_pole_edge.next
        first_net_inf_pole_edge.next = second_net_inf_pole_next
        second_net_inf_pole_next.prior = first_net_inf_pole_edge
        first_net_inf_pole_next.prior = second_net_inf_pole_prior
        second_net_inf_pole_prior.next = first_net_inf_pole_next

        # Add the vertices list from the second network into the first one
        network.vertices_list += network_for_plugging.vertices_list

        # Add the edges from the second network into the first one
        network.edges_list += network_for_plugging.edges_list

        return network