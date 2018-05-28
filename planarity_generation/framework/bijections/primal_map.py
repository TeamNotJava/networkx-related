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

from framework.bijections.halfedge import HalfEdge

class PrimalMap:

    def primal_map_bijection(self, init_half_edge):
        ''' Given the irreducible quandrigulation returned from the Closure,
        this function extract the 3-connected map from it.

        See more in 4.1.3 where the bijection is described.

        :return:
        '''
        associated_half_edge_in_3_map = {}
        self.__primal_map_bijection_rec(init_half_edge, associated_half_edge_in_3_map)
        return associated_half_edge_in_3_map[init_half_edge.next]



    # Recursively transforms the irreducible quandrigulation to the three conected map.
    # The next and prev pointers are kept as before, but the opposite pointer in the
    # half edge is pointing to the opposite half-edge in the face.
    def __primal_map_bijection_rec(self, init_half_edge, associated_half_edges_in_3_map):
        # Associate the initial half edge
        initial_half_edge_association = HalfEdge()
        initial_half_edge_association.index = init_half_edge.index
        associated_half_edges_in_3_map[init_half_edge] = initial_half_edge_association

        # Associate the half edges that are on the same vertex as tie initial one.
        walker_half_edge = init_half_edge.next
        while walker_half_edge is not init_half_edge:
            walker_association = HalfEdge()
            walker_association.index = walker_half_edge.index
            associated_half_edges_in_3_map[walker_half_edge] = walker_association

            # Connect the association with the association of the prev half-edge
            walker_association.prior = associated_half_edges_in_3_map[walker_half_edge.prior]
            associated_half_edges_in_3_map[walker_half_edge.prior].next = walker_association

            # Continue with the next edges
            walker_half_edge = walker_half_edge.next

        # Add the final connection
        initial_half_edge_association.prior = associated_half_edges_in_3_map[init_half_edge.prior]
        associated_half_edges_in_3_map[init_half_edge.prior].next = initial_half_edge_association

        # Make the opposite pointer of the half edge to point to the opposite half edge in the face.
        skipFirst = True
        walker_half_edge = init_half_edge
        while walker_half_edge is not init_half_edge and skipFirst is True:
            skipFirst = False
            opposite_half_edge_in_face = walker_half_edge.next.opposite.next.opposite

            # Check for already processed half edges
            if opposite_half_edge_in_face not in associated_half_edges_in_3_map:
                self.__primal_map_bijection_rec(opposite_half_edge_in_face, associated_half_edges_in_3_map)

            # Make the actual opposite connection between the associations
            associated_half_edges_in_3_map[opposite_half_edge_in_face].opposite = associated_half_edges_in_3_map[
                walker_half_edge]
            associated_half_edges_in_3_map[walker_half_edge].opposite = associated_half_edges_in_3_map[
                opposite_half_edge_in_face]

            # Continue with the next edges
            walker_half_edge = walker_half_edge.next