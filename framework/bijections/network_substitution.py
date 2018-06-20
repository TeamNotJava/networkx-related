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

"""Substitute the edge of the graph with whole network.
"""

import networkx.classes.map
import networkx as nx
import copy.deepcopy as deepcopy



class EdgeByNetworkSubstitution:


    def _check_for_equal_edges(self, query_edge, edge_to_compare_with):
        '''
        Checks wether edges is the equal with network_root_edge.
        :return: True if the edges are equal, False otherwise
        '''
        return (query_edge[0] is edge_to_compare_with[0] and query_edge[1] is edge_to_compare_with[1]) \
               or (query_edge[0] is edge_to_compare_with[1] and query_edge[1] is edge_to_compare_with[0])



    # Finds the closest prev edge of (u,v) in to_map with respect to u .
    def _find_nonpoles_closest_prev_in_to_map(self, to_map, network, u, v, node_mapping):

        # We check for the base case when the vertex is still not part of the graph or does not have any edges.
        u_mapped = node_mapping[u]
        if u_mapped not in to_map.nodes() or len(to_map[u_mapped]) == 0:
            return None

        # We search for closest prev edge of (u,v) with respect to u.
        from_map_prev_edge_walker = network.get_prev_edge(u, v)
        while from_map_prev_edge_walker[1] is not v:
            if from_map_prev_edge_walker[1] in node_mapping:
                prev_v_mapped = node_mapping[from_map_prev_edge_walker[1]]
                if prev_v_mapped in to_map[u_mapped]:
                    return prev_v_mapped

            # Check the other ones
            from_map_prev_edge_walker = network.get_prev_edge(from_map_prev_edge_walker[0], from_map_prev_edge_walker[1])

        raise nx.exception.NetworkXException('A previous edge for ({0}, {1}) was not found ahtoulgh the base case '
                                             'is fulfilled. This should not be the case.'.format(u, v))



    def substitute_edge_by_network(self, original_map, edge_for_substitution, network):
        '''
        Substitute the edge from the map with the whole network given as an argument.

        :param original_map: the original map in which the network will be plugged in
        :param edge_for_substitution: the edge for substitution from the original map
        :param network : the network for plugging in
        :return: new object from the map class where the edge from the original map is substituted with the network
        '''

        to_map = deepcopy(original_map)

        network_root_ege = network.roog_edge()
        zero_pole = network_root_ege[0]
        inf_pole = network_root_ege[1]

        network_zero_pole_prev = network.get_prev_edge(zero_pole, inf_pole)
        network_zero_pole_next = network.get_next_edge(zero_pole, inf_pole)

        network_inf_pole_prev = network.get_prev_edge(inf_pole, zero_pole)
        network_inf_pole_next = network.get_next_edge(inf_pole, zero_pole)

        to_map_size = len(to_map.nodes())
        index_for_map = to_map_size

        # We have to copy the network nodes and edges in the to_map. Only the edge between the poles and its next
        # edges on both sides are excluded.
        node_mapping = dict()
        for edge in network.edges():
            # We map the nodes to the new nodes in the to_map
            u = edge[0]
            v = edge[1]
            if u not in node_mapping:
                node_mapping[u] = index_for_map
                index_for_map += 1
            if v not in node_mapping:
                node_mapping[v] = index_for_map
                index_for_map += 1

            # Exclude the root edge, and its poles next edges.
            if self._check_for_equal_edges(edge, network_root_ege) or \
                self._check_for_equal_edges(edge, network_zero_pole_next) or \
                self._check_for_equal_edges(edge, network_inf_pole_next):

                continue

            # We search for the closest previous edges with respect to u and v
            prev_of_u_mapped = self._find_closest_prev_in_to_map(to_map, network, u, v, node_mapping)
            prev_of_v_mapped = self._find_closest_prev_in_to_map(to_map, network, v, u, node_mapping)

            # Check whether the prev references are pointing to some of the poles. If that's the case then a switch to
            # the vertices of the substitution edge is needed.
            if node_mapping[zero_pole] is prev_of_u_mapped:
                prev_of_u_mapped = edge_for_substitution[0]
            if node_mapping[inf_pole] is prev_of_u_mapped:
                prev_of_u_mapped = edge_for_substitution[1]
            # Same for prev_of_v_mapped
            if node_mapping[zero_pole] is prev_of_v_mapped:
                prev_of_v_mapped = edge_for_substitution[0]
            if node_mapping[inf_pole] is prev_of_v_mapped:
                prev_of_v_mapped = edge_for_substitution[1]

            # Check the special cases with the poles
            if u is not zero_pole and u is not inf_pole and v is not zero_pole and v is not inf_pole:
                # Get the mapped values
                u_mapped = node_mapping[u]
                v_mapped = node_mapping[v]
                # Add the edge directly in the to_map
                to_map.add_edge(u_mapped, v_mapped, prev_of_u_mapped, prev_of_v_mapped)
            else:
                # The poles have to be merged
                # TODO RECHECK this part
                to_map.add_edge(u_mapped, v_mapped, prev_of_u_mapped, prev_of_v_mapped)
