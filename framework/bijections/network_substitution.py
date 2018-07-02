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
    Substitute and edge from the tree connected map with a network.
"""

class EdgeByNetworkSubstitution:

    def substitute_edge_by_network(self, tree_connected_graph, half_edge_for_sub, network):
        '''
        Substitute the edge from the tree connected graph with the whole network given as an argument.

        :param tree_connected_graph: target tree connected graph where the network will be plugged in
        :param half_edge_for_sub: the half edge which corresponding full edge have to be changed
        :param network : the network for plugging in
        '''

        # Extract the opposite half edge from the tree connected graph.
        half_edge_for_sub_opp = half_edge_for_sub.opposite

        # Get the needed edges for manipulation from the network.
        net_root_half_edge = network.root_half_edge
        net_root_half_edge_next = net_root_half_edge.next
        net_root_half_edge_prior = net_root_half_edge.prior
        net_root_half_edge_opp_next = net_root_half_edge.opposite.next
        net_root_half_edge_opp_prior = net_root_half_edge.opposite.prior

        # Identify the zero pole with the the half_edge_for_sub vertex.
        half_edge_for_sub.opposite = net_root_half_edge_next.opposite
        net_root_half_edge_next.opposite.opposite = half_edge_for_sub
        if net_root_half_edge_next is not net_root_half_edge_prior:
            # Switch the pointers so that the network_root_edge and its next are not included
            half_edge_for_sub_next = half_edge_for_sub.next

            half_edge_for_sub.next = net_root_half_edge_next.next
            net_root_half_edge_next.prior = half_edge_for_sub

            half_edge_for_sub_next.prior = net_root_half_edge_prior
            net_root_half_edge_prior.next = half_edge_for_sub_next


        # Identify the inf pole with the the half_edge_for_sub_opp vertex.
        half_edge_for_sub_opp.opposite = net_root_half_edge_opp_next.opposite
        net_root_half_edge_opp_next.opposite.opposite = half_edge_for_sub_opp
        if net_root_half_edge_opp_next is not net_root_half_edge_opp_prior:
            # Switch the pointers so that the network_root_edge_opp and its next are not included
            half_edge_for_sub_opp_next = half_edge_for_sub_opp.next

            half_edge_for_sub_opp.next = net_root_half_edge_opp_prior
            net_root_half_edge_opp_prior.prior = half_edge_for_sub_opp

            half_edge_for_sub_opp_next.prior = net_root_half_edge_opp_prior
            net_root_half_edge_opp_prior.next = half_edge_for_sub_opp_next

        # Add the vertices from the network to the tree connected graph vertex list
        # The poles are not part from the vertices list, therefore we don't have to exclude them.
        tree_connected_graph.vertices_list += network.vertices_list

        # Add the edges from the network to the edges list from the tree connected graph.
        result_edges_set = set()
        # Add the edges from the tree connected graph and the network
        result_edges_set.update(tree_connected_graph.edges_list)
        result_edges_set.update(network.edges_list)

        # Exclude all possible half edges from the tree and network to prevent both half edges that share and edge to be
        # in the set
        for edge_for_removing in [net_root_half_edge, net_root_half_edge.opposite, net_root_half_edge_next,
                             net_root_half_edge_opp_next, net_root_half_edge_next.opposite,
                             net_root_half_edge_opp_next.opposite, half_edge_for_sub, half_edge_for_sub_opp]:
            if edge_for_removing in result_edges_set:
                result_edges_set.remove(edge_for_removing)

        # Add only the edges from one side
        result_edges_set.update([half_edge_for_sub, half_edge_for_sub_opp])

        # Reinitialize the list of the edges from the tree_connected_graph
        tree_connected_graph.edges_list.clear()
        tree_connected_graph.edges_list += result_edges_set