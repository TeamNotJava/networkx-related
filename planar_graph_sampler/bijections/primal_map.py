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

from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge


class PrimalMap:
    """
    Make a bijection between the irreducible quadrangulation to a 3-connected map.
    """

    def primal_map_bijection(self, init_half_edge):
        """
        Given the irreducible quadrangulation returned from the closure,
        this function extract the 3-connected map from it.

        The next and prev pointers are kept as before, but the opposite pointer in the half edge is pointing to the
        opposite half-edge in the face.

        See more in 4.1.3 where the bijection is described.
        """
        quad_half_edge = self.___quadrangulate(init_half_edge)

        # Start dfs for the pointers reordering.
        associated_half_edges_in_3_map = {}
        stack = list()
        stack.append(quad_half_edge)

        # Stop after the stack gets empty
        while stack:
            top_half_edge = stack.pop()

            top_half_edge_association = HalfEdge()
            top_half_edge_association.node_nr = top_half_edge.node_nr
            associated_half_edges_in_3_map[top_half_edge] = top_half_edge_association

            # Associate the half edges that are on the same vertex as tie initial one.
            walker_half_edge = top_half_edge.next
            while walker_half_edge is not top_half_edge:
                walker_association = HalfEdge()
                walker_association.node_nr = walker_half_edge.node_nr
                associated_half_edges_in_3_map[walker_half_edge] = walker_association

                # Connect the association with the association of the prev half-edge
                walker_association.prior = associated_half_edges_in_3_map[walker_half_edge.prior]
                associated_half_edges_in_3_map[walker_half_edge.prior].next = walker_association

                # Continue with the next edges
                walker_half_edge = walker_half_edge.next

            # Add the final connection
            top_half_edge_association.prior = associated_half_edges_in_3_map[top_half_edge.prior]
            associated_half_edges_in_3_map[top_half_edge.prior].next= top_half_edge_association

            # Make the opposite pointer of the half edge to point to the opposite half edge in the face.
            incident_half_edges = top_half_edge.incident_half_edges()
            for walker_half_edge in incident_half_edges:
                opposite_half_edge_in_face = walker_half_edge.opposite.next.opposite.next

                # Check for already processed half edges
                if opposite_half_edge_in_face not in associated_half_edges_in_3_map:
                    # Process the opposite half edge - push on the stack
                    stack.append(opposite_half_edge_in_face)
                else:
                    # Make the actual opposite connection between the associations
                    associated_half_edges_in_3_map[opposite_half_edge_in_face].opposite = associated_half_edges_in_3_map[
                        walker_half_edge]
                    associated_half_edges_in_3_map[walker_half_edge].opposite = associated_half_edges_in_3_map[
                        opposite_half_edge_in_face]

        return associated_half_edges_in_3_map[quad_half_edge]


    # Makes the outer face of the irreducible dissection quadrangular by adding a new edge
    # between two opposite nodes of the hexagon
    def ___quadrangulate(self, init_half_edge):
        # Add the outer edge
        new_half_edge = HalfEdge()
        new_half_edge.next = init_half_edge
        new_half_edge.prior = init_half_edge.prior
        init_half_edge.prior.next = new_half_edge
        init_half_edge.prior = new_half_edge

        new_half_edge.node_nr = init_half_edge.node_nr
        # new_half_edge.color = init_half_edge.color
        return_edge = new_half_edge

        # Iterate to the opposite node of the hexagon node
        count = 0
        current_half_edge = new_half_edge
        while True:
            current_half_edge = current_half_edge.prior.opposite
            count += 1
            if count == 3:
                break

        fresh_half_edge = HalfEdge()
        fresh_half_edge.opposite = new_half_edge
        new_half_edge.opposite = fresh_half_edge

        fresh_half_edge.prior = current_half_edge.prior
        fresh_half_edge.next = current_half_edge
        current_half_edge.prior.next = fresh_half_edge
        current_half_edge.prior = fresh_half_edge

        fresh_half_edge.node_nr = current_half_edge.node_nr
        # fresh_half_edge.color = current_half_edge.color

        # if return_edge.color is not 0:
        #     return_edge = fresh_half_edge

        #assert (return_edge.color is 0)
        return return_edge

    # Checks if quadrangulation is correct
    def ___test_quadrangulation(self, init_half_edge):
        # Check if every cycle is of degree 4
        edge_list = init_half_edge.get_all_half_edges()

        for half_edge in edge_list:
            current_half_edge = half_edge
            print("Check: ", format(current_half_edge))
            cycle_degree = 0
            while True:
                current_half_edge = current_half_edge.next
                print(current_half_edge)
                cycle_degree += 1
                print("Cycle degree: ", format(cycle_degree))
                assert (current_half_edge.opposite is not None)
                if current_half_edge is half_edge:
                    break
                assert (cycle_degree < 5)
                current_half_edge = current_half_edge.opposite
                if current_half_edge is half_edge:
                    break
                print(current_half_edge)
        print("Quadrangulation is okay")
