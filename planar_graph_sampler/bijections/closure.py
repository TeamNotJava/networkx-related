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

"""This class is needed for transformation of a Boltzmann sampler for bicolored binary trees
into a Boltzmann sampler for 3-connected planar graphs.
"""

import sys
import os
from planar_graph_sampler.combinatorial_classes.halfedge import ClosureHalfEdge
from planar_graph_sampler.combinatorial_classes.dissection import IrreducibleDissection
from framework.utils import Counter
counter = Counter()

class Closure:

    # Performs bicolored partial closure on a binary tree. When possible add a
    # new edge in order to get faces of degree four.
    def ___bicolored_partial_closure(self, init_half_edge):
        stack = []
        stack.append(init_half_edge)
        break_edge = init_half_edge
        current_half_edge = init_half_edge

        while True:
            current_half_edge = current_half_edge.next

            if current_half_edge.opposite is None:
                if len(stack) == 0:
                    break_edge = current_half_edge
                if current_half_edge is break_edge and len(stack) > 0:
                    break
                stack.append(current_half_edge)
            else:
                current_half_edge = current_half_edge.opposite
                if len(stack) > 0:
                    top_half_edge = stack.pop()
                    top_half_edge.number_proximate_inner_edges += 1

                    if top_half_edge.number_proximate_inner_edges == 3:
                        new_half_edge = ClosureHalfEdge()
                       # new_half_edge.add_to_closure(current_half_edge, current_half_edge.next, top_half_edge, False)
                        current_half_edge.add_to_closure(top_half_edge, False, new_half_edge)
                        current_half_edge = top_half_edge.prior
                    else:
                        stack.append(top_half_edge)

        if init_half_edge.opposite is not None:
            # Iterate to first stem
            half_edge_list = init_half_edge.list_half_edges([])
            for edge in half_edge_list:
                if edge.opposite is None:
                    return edge
        else:
            return init_half_edge

    # Performs bicolored complete closure on a planar map of a binary tree in order to obtain
    # a irreducible dissection of the hexagon with quadrangular inner faces
    # input: init_half_edge is the half-edge that we get when we convert a binary tree into
    # a planar map
    def ___bicolored_complete_closure(self, init_half_edge):
        starting_half_edge = self.___bicolored_partial_closure(init_half_edge)

        # Construct hexagon
        hexagon = [ClosureHalfEdge() for i in range(12)]
        hexagon_start_half_edge = self.___construct_hexagon(hexagon, starting_half_edge)

        # Connect the starting half-edge of our planar map with the first node of the hexagon
        new_half_edge = ClosureHalfEdge()
        #new_half_edge.add_to_closure(hexagon_start_half_edge, hexagon[11], starting_half_edge, True)
        hexagon_start_half_edge.add_to_closure(starting_half_edge, True, new_half_edge)

        connecting_half_edge = new_half_edge

        # Now traverse the planar map. Depending on the distance between a new inner edge and
        # the next half-edge one can assign the new half edge to a certain hexagon node
        distance = 0
        hexagon_iter = hexagon_start_half_edge
        current_half_edge = starting_half_edge
        hexagon_iter_index = 0
        # This variable is needed in order to check if we already visited more than one node of the hexagon
        visited_more = False
        while True:
            current_half_edge = current_half_edge.next

            if current_half_edge is starting_half_edge:
                break

            # If the opposite is None then we have to assign it to one of the hexagon nodes
            if current_half_edge.opposite is None:
                fresh_half_edge = ClosureHalfEdge()
                fresh_half_edge.opposite = current_half_edge
                current_half_edge.opposite = fresh_half_edge

                if distance == 0:
                    # Move 4 hexagon half-edges further
                    hexagon_iter_index = (hexagon.index(hexagon_iter) + 4) % 12
                    hexagon_iter = hexagon[hexagon_iter_index]
                elif distance == 1:
                    # Move 2 hexagon half-edges further
                    hexagon_iter_index = (hexagon.index(hexagon_iter) + 2) % 12
                    hexagon_iter = hexagon[hexagon_iter_index]
                else:
                    # Stay at current hexagon half-edge
                    pass

                assert (hexagon_iter_index < 13)

                if hexagon_iter.node_nr is not hexagon[0].node_nr:
                    visited_more = True

                if visited_more and id(hexagon_iter) == id(hexagon[0]):
                    last_added_edge = connecting_half_edge.next
                    #fresh_half_edge.add_to_closure(connecting_half_edge, last_added_edge, current_half_edge, True)
                    connecting_half_edge.add_to_closure(current_half_edge, True, fresh_half_edge)
                else:
                    last_added_edge = hexagon_iter.next
                    # fresh_half_edge.add_to_closure(hexagon_iter, last_added_edge, current_half_edge, True)
                    hexagon_iter.add_to_closure(current_half_edge, True, fresh_half_edge)

                distance = 0
            else:
                current_half_edge = current_half_edge.opposite
                distance += 1

        return hexagon[0]



    # Constructs a hexagon from a list of half_edges. 
    def ___construct_hexagon(self, hexagon_half_edges, partial_closure_edge):
        inv_color = None
        color = partial_closure_edge.color
        if color is 'white':
            inv_color = 'black'
        else:
            inv_color = 'white'

        # Indicate that they belong to the hexagon
        for i in range(12):
            hexagon_half_edges[i].is_hexagonal = True

        # Set opposite edges
        iter = 0
        while iter < 11:
            hexagon_half_edges[iter].opposite = hexagon_half_edges[iter + 1]
            hexagon_half_edges[iter + 1].opposite = hexagon_half_edges[iter]
            iter += 2

        # Set next and prior half-edges. Here prior and next are the same
        iter = 1
        while iter < 12:
            hexagon_half_edges[iter].next = hexagon_half_edges[(iter + 1) % 12]
            hexagon_half_edges[iter].prior = hexagon_half_edges[(iter + 1) % 12]
            hexagon_half_edges[(iter + 1) % 12].next = hexagon_half_edges[iter]
            hexagon_half_edges[(iter + 1) % 12].prior = hexagon_half_edges[iter]
            iter += 2

        # Set node number.
        current_half_edge = hexagon_half_edges[11]
        while True:
            node_num = next(counter)
            current_half_edge.node_nr = node_num
            current_half_edge.next.node_nr = node_num
            current_half_edge = current_half_edge.next.opposite
            if current_half_edge is hexagon_half_edges[11]:
                break

        even_color = None
        odd_color = None
        if hexagon_half_edges[0].node_nr % 2 == 0:
            # Then all even nodes have to have the inverse color
            even_color = inv_color
            odd_color = color
        else:
            even_color = color
            odd_color = inv_color

        # Set color
        for i in range(12):
            if hexagon_half_edges[i].node_nr % 2 == 0:
                hexagon_half_edges[i].color = even_color
            else:
                hexagon_half_edges[i].color = odd_color

        return hexagon_half_edges[0]

    def test_partial_closure(self, init_half_edge):
        edge_list = init_half_edge.list_half_edges()
        stem_list = []

        for edge in edge_list:
            if edge.opposite is None:
                stem_list.append(edge)

        # Check for each stem if it has at most two full edges as successors
        for stem in stem_list:
            count = 0
            current_half_edge = stem
            while True:
                current_half_edge = current_half_edge.next
                if current_half_edge is stem:
                    break
                if current_half_edge.opposite is not None:
                    current_half_edge = current_half_edge.opposite
                    print("current: ", format(current_half_edge))
                    count = count + 1
                    if count > 2:
                        raise Exception("partial closure failed")
                    assert (count < 3)
                else:
                    break

        print("Partial closure is okay.")

    # Check if the connections between the edges are correct
    def test_connections_between_half_edges(self, init_half_edge):
        edge_list = init_half_edge.list_half_edges([])
        node_dict = init_half_edge.get_node_list()
        hex_half_edge = None
        num_hex_half_edges = 0
        for edge in edge_list:
            if edge.is_hexagonal:
                num_hex_half_edges += 1
            if hex_half_edge is None and edge.is_hexagonal and edge.prior.is_hexagonal:
                hex_half_edge = edge
            assert (edge is edge.next.prior)
            assert (edge is edge.prior.next)
            assert (edge is edge.opposite.opposite)
            assert (edge.opposite is not None)

        assert (num_hex_half_edges == 12)

        # Test if the outer face is a hexagon
        curr_half_edge = hex_half_edge
        assert(curr_half_edge.is_hexagonal)
        hex_edges = 0
        while True:
            curr_half_edge = curr_half_edge.opposite
            assert (curr_half_edge.is_hexagonal)
            if curr_half_edge == hex_half_edge:
                break
            curr_half_edge = curr_half_edge.next
            assert (curr_half_edge.is_hexagonal)
            if curr_half_edge == hex_half_edge:
                break
            hex_edges += 1
        assert(hex_edges == 5)

        # Test if every node has at most two hexagonal edges
        for node in node_dict:
            half_edges = node_dict[node]
            num_hex = 0
            for e in half_edges:
                if e.is_hexagonal:
                    num_hex += 1
            assert (num_hex < 3)
        print("Connections are okay.")

    # Checks if half edges at every node are planar
    def test_planarity_of_embedding(self, init_half_edge):
        edge_list = init_half_edge.list_half_edges([])

        # Check if there are two different edges that have the same prior/next half-edge
        for edge in edge_list:
            for i in edge_list:
                if id(i) != id(edge) and (i.prior is edge.prior or i.next is edge.next):
                    raise Exception("There are two different edges with the samp prior/next.")

        print("Embedding is okay.")

    def closure(self, binary_tree):
        """Implements the bijection between the binary trees and the irreducible
        dissections of hexagon. 
        :param: binary_tree: BinaryTree
        :return: IrreducibleDissection(init_half_edge): IrreducibleDissection
            Irreducible dissection of hexagon
        """
        init_half_edge = binary_tree
        # This edge is hexagonal and points in ccw direction
        init_half_edge = self.___bicolored_complete_closure(init_half_edge)
        self.test_partial_closure(init_half_edge)
        self.test_connections_between_half_edges(init_half_edge)
        self.test_planarity_of_embedding(init_half_edge)
        return IrreducibleDissection(init_half_edge)
