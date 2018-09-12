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


from planar_graph_sampler.combinatorial_classes.halfedge import ClosureHalfEdge
from planar_graph_sampler.combinatorial_classes.dissection import \
    IrreducibleDissection
from planar_graph_sampler.grammar.grammar_utils import Counter

counter = Counter()


class Closure:
    """
    This class is needed for transformation of a Boltzmann sampler for
    bicolored binary trees into a Boltzmann sampler for 3-connected planar
    graphs.
    """

    def _bicolored_partial_closure(self, init_half_edge):
        """Computes bicolored partial closure on a binary tree.
        When possible adds a new edge to get faces of degree four.
        """
        stack = [init_half_edge]
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
                        current_half_edge.add_to_closure(top_half_edge, False,
                                                         new_half_edge)
                        current_half_edge = top_half_edge.prior
                    else:
                        stack.append(top_half_edge)

        if init_half_edge.opposite is not None:
            # Iterate to first stem
            # half_edge_list = init_half_edge.get_all_half_edges_gen()
            for edge in init_half_edge.get_all_half_edges_gen():
                if edge.opposite is None:
                    return edge
        else:
            return init_half_edge

    def _bicolored_complete_closure(self, init_half_edge):
        """Computes bicolored complete closure on a planar map of a binary
        tree in order to obtain an irreducible dissection of the hexagon with
        quadrangular inner faces.

        Parameters
        ----------
        init_half_edge: ClosureHalfEdge
            The half-edge that we get when we convert a binary tree into a
            planar map.
        """
        starting_half_edge = self._bicolored_partial_closure(init_half_edge)

        # Construct hexagon
        hexagon = [ClosureHalfEdge() for _ in range(12)]
        hexagon_start_half_edge = self._construct_hexagon(hexagon,
                                                          starting_half_edge)

        # Connect the starting half-edge of our planar map with the _first
        # node of the hexagon
        new_half_edge = ClosureHalfEdge()
        hexagon_start_half_edge.add_to_closure(starting_half_edge, True,
                                               new_half_edge)

        connecting_half_edge = new_half_edge

        # Now traverse the planar map. Depending on the distance between a
        # new inner edge and the next half-edge one can assign the new half
        # edge to a certain hexagon node
        distance = 0
        hexagon_iter = hexagon_start_half_edge
        current_half_edge = starting_half_edge
        hexagon_iter_index = 0
        # This variable is needed in order to check if we already visited
        # more than one node of the hexagon
        visited_more = False
        while True:
            current_half_edge = current_half_edge.next

            if current_half_edge is starting_half_edge:
                break

            # If the opposite is None then we have to assign it to one of the
            #  hexagon nodes
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
                    connecting_half_edge.add_to_closure(current_half_edge,
                                                        True, fresh_half_edge)
                else:
                    hexagon_iter.add_to_closure(current_half_edge,
                                                True, fresh_half_edge)
                distance = 0
            else:
                current_half_edge = current_half_edge.opposite
                distance += 1

        return hexagon[0]

    def _construct_hexagon(self, hexagon_half_edges, partial_closure_edge):
        """Constructs a hexagon from a list of half_edges."""
        color = partial_closure_edge.color
        inv_color = 1 - color

        # Indicate that they belong to the hexagon
        for i in range(12):
            hexagon_half_edges[i].is_hexagonal = True

        # Set opposite edges
        it = 0
        while it < 11:
            hexagon_half_edges[it].opposite = hexagon_half_edges[it + 1]
            hexagon_half_edges[it + 1].opposite = hexagon_half_edges[it]
            it += 2

        # Set next and prior half-edges. Here prior and next are the same
        it = 1
        while it < 12:
            hexagon_half_edges[it].next = hexagon_half_edges[(it + 1) % 12]
            hexagon_half_edges[it].prior = hexagon_half_edges[(it + 1) % 12]
            hexagon_half_edges[(it + 1) % 12].next = hexagon_half_edges[it]
            hexagon_half_edges[(it + 1) % 12].prior = hexagon_half_edges[it]
            it += 2

        # Set node number.
        current_half_edge = hexagon_half_edges[11]
        while True:
            node_num = next(counter)
            current_half_edge.node_nr = node_num
            current_half_edge.next.node_nr = node_num
            current_half_edge = current_half_edge.next.opposite
            if current_half_edge is hexagon_half_edges[11]:
                break

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

    def closure(self, binary_tree):
        """Implements the bijection between binary trees and irreducible
        dissections of a hexagon.The partial closure takes a binary tree
        as input and closes the tree, such that every face in the
        resulting graph has degree four. Afterwards, the complete closure
        is performed, where the partially closed binary tree is integrated
        into a hexagon (irreducible dissection of hexagon).
        """
        init_half_edge = binary_tree.half_edge
        # This edge is hexagonal and points in ccw direction.
        init_half_edge = self._bicolored_complete_closure(init_half_edge)
        return IrreducibleDissection(init_half_edge)
