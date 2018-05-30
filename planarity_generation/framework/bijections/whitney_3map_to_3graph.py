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

import networkx as nx
import matplotlib.pyplot as plt
from framework.bijections.primal_map import  PrimalMap
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

        # Recursively extract the components from the 3-connected map.
        vertices_list = set()
        edges_list = set()
        self.__extract_3_graph_components_rec(root_half_edge, root_half_edge, set(), vertices_list, edges_list)

        # We transform the extracted components to the nx.Graph structure
        nx_graph = self.__create_graph_from_components(root_half_edge, vertices_list, edges_list)

        # We create a tuple of the root edge node numbers.
        root_edge = (root_half_edge.node_nr, root_half_edge.opposite.node_nr)

        return EdgeRootedThreeConnectedPlanarGraph(nx_graph, root_edge)



    def __extract_3_graph_components_rec(
            self, first_half_edge, root_half_edge, visited_half_edges, vertices_list, edges_list):
        # Check if the half edge has been already processed
        if first_half_edge.index in visited_half_edges:
            return

        # Mark the first half edge and the ones with which it shares a vertex to visited.
        visited_half_edges.add(first_half_edge.index)
        walker_half_edge = first_half_edge.next
        while walker_half_edge != first_half_edge:
            visited_half_edges.add(first_half_edge.index)
            walker_half_edge = walker_half_edge.next

        # Check if the first half edge is different from the root and root.opposite. If this is true,
        # than the first half edge is added to a vertices list.
        walker_half_edge = first_half_edge
        if walker_half_edge.node_nr != root_half_edge.node_nr and walker_half_edge.node_nr != root_half_edge.opposite.node_nr:
            print(walker_half_edge)
            vertices_list.add(walker_half_edge.node_nr)

        # Insert half edges to the edges list.
        walker_half_edge = walker_half_edge.next
        while walker_half_edge != first_half_edge:
            # The condition that one half edge should fullfill for inserting.
            if walker_half_edge != root_half_edge and walker_half_edge.opposite.index not in visited_half_edges:
                from_vertex = min(walker_half_edge.node_nr, walker_half_edge.opposite.node_nr)
                to_vertex = max(walker_half_edge.node_nr, walker_half_edge.opposite.node_nr)
                edges_list.add((from_vertex, to_vertex))
            walker_half_edge = walker_half_edge.next

        # Call the function recursively for the opposite half edges.
        walker_half_edge = walker_half_edge.next
        while walker_half_edge != first_half_edge:
            self.__extract_3_graph_components_rec(
                walker_half_edge.opposite, root_half_edge, visited_half_edges, vertices_list, edges_list)
            walker_half_edge = walker_half_edge.next



    def __create_graph_from_components(self, root_half_edge, vertices_list, edges_list):

        G = nx.Graph()

        # By the Whitney bijection, the root edge vertices should not be part of the graph, but since we have other
        # edges that are connected with this vertices and from this point we are using nx.Graph structure,
        # they have to be added. In order to give the correct number of L-vertices in EdgeRootedThreeConnectedPlanarGraph
        # we always have to substract 2 from the number of nodes.
        G.add_node(root_half_edge.node_nr)
        G.add_node(root_half_edge.opposite.node_nr)

        # print('Vertices list: ' + vertices_list.__repr__())
        # print('Vertices list: ' + edges_list.__repr__())

        # We add all other vertices from the vertices list.
        for vertex_number in vertices_list:
            G.add_node(vertex_number)

        # We add the adges in the nx graph structure.
        for edge in edges_list:
            G.add_edge(edge[0], edge[1])

        return G

    def test_whitney_bijection(self):
        # print("Start test...")
        primal_map = PrimalMap()
        half_edges = primal_map.create_sample_closure_output()

        # Make the primal map bijection
        primal_map = primal_map
        three_map = primal_map.primal_map_bijection(half_edges[1])

        # Make the Whiney bijection
        whiney_bijection = WhitneyBijection()
        edge_rooted_three_connected_graph = whiney_bijection.whitney_bijection(three_map)

        # Chech the properties
        print(edge_rooted_three_connected_graph)

        print(len(edge_rooted_three_connected_graph.graph.nodes))
        nx.draw(edge_rooted_three_connected_graph.graph)
        plt.show()


if __name__ == "__main__":
    WhitneyBijection().test_whitney_bijection()