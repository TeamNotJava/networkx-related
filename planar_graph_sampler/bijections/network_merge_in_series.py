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
    Merges two networks in a series.
"""


class NetworkMergeInSeries:

    def merge_networks_in_series(self, network, network_for_plugging):
        '''
        Merges the network for plugging into netwrok in a serial manner which means that the infinite pole from the
        network is identified with the 0-pole from network_for_plugging.

        :param network: first network which will result in merged networks
        :param network_for_plugging: second network which will be plugged in the first one
        '''

        # Extract the poles from both networks
        first_net_zero_pole_edge = network.root_half_edge
        first_net_inf_pole_edge = first_net_zero_pole_edge.opposite

        second_net_zero_pole_edge = network_for_plugging.root_half_edge
        second_net_inf_pole_edge = second_net_zero_pole_edge.opposite

        # Change the poles in the result network so that now the inf-pole from the second network will be inf-pole in the result one
        first_net_zero_pole_edge.opposite = second_net_inf_pole_edge
        second_net_inf_pole_edge.opposite = first_net_zero_pole_edge

        # Get the half edges from both networks for merging
        first_net_inf_pole_next = first_net_inf_pole_edge.next
        first_net_inf_pole_prior = first_net_inf_pole_edge.prior

        second_net_zero_pole_edge_next = second_net_zero_pole_edge.next
        second_net_zero_pole_edge_prior = second_net_zero_pole_edge.prior

        # Merge the both networks so that the inf-pole from the first network is identified with the zero-pole from the second one
        # Handling different while merging the two networks.
        if first_net_inf_pole_edge is not first_net_inf_pole_next and \
                second_net_zero_pole_edge is not second_net_zero_pole_edge_next: # both vertices have additional connections
            first_net_inf_pole_next.prior = second_net_zero_pole_edge_prior
            second_net_zero_pole_edge_prior.next = first_net_inf_pole_next

            first_net_inf_pole_prior.next = second_net_zero_pole_edge_next
            second_net_zero_pole_edge_next.prior = first_net_inf_pole_prior

        elif first_net_inf_pole_edge is not first_net_inf_pole_next:# Inf pole from first network has add conn.
            first_net_inf_pole_next.prior = first_net_inf_pole_prior
            first_net_inf_pole_prior.next = first_net_inf_pole_next

        elif second_net_zero_pole_edge is not second_net_zero_pole_edge_next:  # Zero pole from the second network has additional conn.
            second_net_zero_pole_edge_next.prior = second_net_zero_pole_edge_prior
            second_net_zero_pole_edge_prior.next = second_net_zero_pole_edge_next


        # Update the node numbers in the second network zero-pole edges
        half_edge_walker = first_net_inf_pole_next
        while half_edge_walker != first_net_inf_pole_prior:
            half_edge_walker.node_nr = first_net_inf_pole_next.node_nr
            half_edge_walker = half_edge_walker.next

        # Add the vertices list from the second network into the first one
        network.vertices_list += network_for_plugging.vertices_list
        # Add the previous inf-pole to the vertices list since now the inf-pole is taken from the second network
        if first_net_inf_pole_edge.next != first_net_inf_pole_edge: # It means it has another connections
            network.vertices_list.append(first_net_inf_pole_next)

        # Add the edges from the second network into the first one
        network.edges_list += network_for_plugging.edges_list

        # Remove the first network inf pole if does not have any other connections.
        if first_net_inf_pole_next == first_net_inf_pole_edge and \
                first_net_inf_pole_edge in network.edges_list:
            network.edges_list.remove(first_net_inf_pole_edge)

        # Remove the second network zero pole if does not have any other connections.
        if second_net_zero_pole_edge.next == second_net_zero_pole_edge and \
                second_net_zero_pole_edge in network.edges_list:
            network.edges_list.remove(second_net_zero_pole_edge)

        return network
