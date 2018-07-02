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


from ..bijections.halfedge import HalfEdge
from ..samplers.generic_samplers import LSubsSampler, SetSampler

class BlockDecomposition:

    # Merges marked vertices of all L-derived two connected graphs in a given list into
    # one unique marked vertex
    # param: l_der_two_connected_list: List of L-derived 2-connected graphs that has to be
    #        merged at their marked vertices
    def merge_set_of_l_der_two_connected_graphs(self, l_der_two_connected_list):
        if len(l_der_two_connected_list) == 1:
            return l_der_two_connected_list[0]

        first_two_connected_graph = l_der_two_connected_list[0]
        second_two_connected_graph = l_der_two_connected_list[1]
        # Does this really work this way??
        merged_two_connected = SetSampler(first_two_connected_graph, second_two_connected_graph)

        for i in range(2, len(l_der_two_connected_list)):
            merged_two_connected = SetSampler(merged_two_connected, l_der_two_connected_list[i])
        
        return merged_two_connected
        


    # Merges unmarked node of a L-derived two-connected graph with a 
    # marked node of a L-derived one-connected graph
    # param: unmarked_node: list of half-edges belonging a unmarked node of a 
    #        L-derived 2-connected graph
    # param: l_der_one_connected: L derived one connected graph
    def replace_node_with_l_der_one_connected(self, unmarked_node, l_der_one_connected):
        one_connected_marked_node = l_der_one_connected.root_vertex
        one_connected_first_half_edge = one_connected_marked_node[0]
        unmakred_first_half_edge = unmarked_node[0]

        # Select two half-edges belonging to the unmakred node in order to 
        # insert the half-edges of the rooted-vertex between them
        prior_half_edge = unmarked_node[0]
        next_half_edge = None
        if len(unmarked_node) == 1:
            next_half_edge = prior_half_edge
        else:
            next_half_edge = prior_half_edge.next

        # Insert all half-edges of the root-vertex
        prior_half_edge.next = one_connected_marked_node[0]
        one_connected_marked_node[0].prior = prior_half_edge
        next_half_edge.prior = one_connected_marked_node[0].prior
        one_connected_marked_node[0].prior.next = next_half_edge

        # Change node number, color and index of the root-vertex (keep the parameters of the unmarked node)
        unmakred_node_nr = unmakred_first_half_edge.node_nr
        unmarked_node_color = unmakred_first_half_edge.color
        unmarked_max_index = unmakred_first_half_edge.get_max_half_edge_index()
        change_color = False
        change_node_nr = False
        index = unmarked_max_index + 1
        if one_connected_first_half_edge.color is not unmarked_node_color:
            change_color = True
        if one_connected_first_half_edge.node_nr is not unmakred_node_nr:
            change_node_nr = True

        for half_edge in one_connected_marked_node:
            half_edge.index = index
            index += 1
            half_edge.marked_vertex = False
            if change_node_nr:
                half_edge.node_nr = unmakred_node_nr
            if change_color:
                half_edge.color = unmarked_node_color


        
         







        


        



        