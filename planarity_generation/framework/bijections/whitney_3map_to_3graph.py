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

"""Make a bijection between the irreducible quadrangulation to a 3-connected map.
"""

from networkx import Graph
from framework.bijections.halfedge import HalfEdge
from framework.combinatorial_classes.three_connected_graph import EdgeRootedThreeConnectedPlanarGraph


class WhitneyBijection:

    def whitney_bijection(self, root_half_edge):
        '''
        Given the 3 connected map returned from the Primal bijection,
        this function extract the 3-connected graph from it.
        The difference between 3-connected map and 3-connected graph is that
        the graph have excluded the root edge from the U-atoms(edges) and
        its vertices from the L-atoms(vertices).

        Detailed explanation in 4.1.2.
        :return: EdgeRootedThreeConnectedPlanarGraph
        '''

        vertices_list = []
        edges_list = []
        self.__extract_3_graph_components_rec(root_half_edge, root_half_edge, set(), vertices_list, edges_list)

        root_edge, nx_graph = self.__create_graph_from_components(vertices_list, edges_list)
        return EdgeRootedThreeConnectedPlanarGraph(root_edge, nx_graph)



    def __extract_3_graph_components_rec(
            self, first_half_edge, root_half_edge, visited_half_edges, vertices_list, edges_list):
        # Check if the half edge has been already processed
        if first_half_edge.index in visited_half_edges:
            return

        # Mark the first half edge and the ones with which it shares a vertex to visited.
        visited_half_edges.update(first_half_edge.index)
        walker_half_edge = first_half_edge.next
        while walker_half_edge != first_half_edge:
            visited_half_edges.update(first_half_edge.index)
            walker_half_edge = walker_half_edge.next

        # Check if the first half edge is different from the root and root.opposite. If this is true,
        # than the first half edge is added to a vertices list.
        walker_half_edge = first_half_edge
        if walker_half_edge != root_half_edge and walker_half_edge.opposite != root_half_edge:
            vertices_list.append(walker_half_edge)

        # Insert half edges to the edges list.
        walker_half_edge = walker_half_edge.next
        while walker_half_edge != first_half_edge:
            # The condition that one half edge should fullfill for inserting.
            if walker_half_edge != root_half_edge and walker_half_edge.opposite.index not in visited_half_edges:
                edges_list.append(walker_half_edge)
            walker_half_edge = walker_half_edge.next

        # Call the function recursively for the opposite half edges.
        walker_half_edge = walker_half_edge.next
        while walker_half_edge != first_half_edge:
            self.__extract_3_graph_components_rec(
                walker_half_edge.opposite, root_half_edge, visited_half_edges, vertices_list, edges_list)
            walker_half_edge = walker_half_edge.next



    def __create_graph_from_components(self, vertices_list, edges_list):
        pass