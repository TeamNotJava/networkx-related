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
from planar_graph_sampler.combinatorial_classes.network import Network
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge


class NetworkMergeInSeries:

    def merge_networks_in_series(self, network, network_for_plugging):
        """
        Merges the network for plugging into netwrok in a serial manner which means that the infinite pole from the
        network is identified with the 0-pole from network_for_plugging.

        :param network: _first network which will result in merged networks
        :param network_for_plugging: _second network which will be plugged in the _first one
        """

        new_l_size = network.l_size() + network_for_plugging.l_size() + 1
        new_u_size = network.u_size() + network_for_plugging.u_size()

        # Extract the poles from both networks
        first_net_zero_pole_edge = network.get_zero_pole()
        first_net_inf_pole_edge = network.get_inf_pole()

        second_net_zero_pole_edge = network_for_plugging.get_zero_pole()
        second_net_inf_pole_edge = network_for_plugging.get_inf_pole()

        # Create a new half edges for connecting the poles of the network. The edge will not be part from the edges list
        new_root_half_edge = HalfEdge()
        # TODO check if this is 'insert_after'
        new_root_half_edge.node_nr = first_net_zero_pole_edge.node_nr
        new_root_half_edge.next = first_net_zero_pole_edge.next
        new_root_half_edge.prior = first_net_zero_pole_edge
        new_root_half_edge.next.prior = new_root_half_edge
        first_net_zero_pole_edge.next = new_root_half_edge
        #new_root_half_edge = first_net_zero_pole_edge.insert_after()

        new_root_opposite = HalfEdge()
        new_root_opposite.node_nr = second_net_inf_pole_edge.node_nr
        new_root_opposite.next = second_net_inf_pole_edge.next
        new_root_opposite.prior = second_net_inf_pole_edge
        new_root_opposite.next.prior = new_root_opposite
        second_net_inf_pole_edge.next = new_root_opposite

        new_root_half_edge.opposite = new_root_opposite
        new_root_opposite.opposite = new_root_half_edge

        # Set the new root edge in the network.
        #network.root_half_edge = new_root_half_edge

        # Get the half edges from both networks for merging
        first_net_inf_pole_prior = first_net_inf_pole_edge.prior
        second_net_zero_pole_edge_prior = second_net_zero_pole_edge.prior

        # Merge the both networks so that the inf-pole from the _first network is identified with the zero-pole from the _second one
        # Handling different while merging the two networks.
        first_net_inf_pole_edge.prior = second_net_zero_pole_edge_prior
        second_net_zero_pole_edge_prior.next = first_net_inf_pole_edge

        first_net_inf_pole_prior.next = second_net_zero_pole_edge
        second_net_zero_pole_edge.prior = first_net_inf_pole_prior

        # Update the node numbers in the _second network zero-pole edges
        half_edge_walker = first_net_inf_pole_prior.next
        while half_edge_walker != first_net_inf_pole_prior:
            half_edge_walker.node_nr = first_net_inf_pole_edge.node_nr
            half_edge_walker = half_edge_walker.next

        # Add the vertices list from the _second network into the _first one
        #network.vertices_list += network_for_plugging.vertices_list
        #network.vertices_list.append(first_net_inf_pole_edge)

        # Add the edges from the _second network into the _first one

        #network.edges_list += network_for_plugging.edges_list

        # After a serial merge the poles are never linked.
        return Network(new_root_half_edge, is_linked=False, l_size=new_l_size, u_size=new_u_size)
