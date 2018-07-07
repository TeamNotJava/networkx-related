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

from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge


def primal_map(dissection):
    """Used in the grammar

    :param dissection:
    """
    # todo what else needs to be done here?
    # petrov: As I have understood the bijection, I think we have implemented everything.
    return PrimalMap().primal_map_bijection(dissection)


class PrimalMap:

    def primal_map_bijection(self, init_half_edge):
        ''' Given the irreducible quandrigulation returned from the Closure,
        this function extract the 3-connected map from it.

        See more in 4.1.3 where the bijection is described.

        :return:
        '''
        associated_half_edge_in_3_map = {}
        self.__primal_map_bijection_rec(init_half_edge, associated_half_edge_in_3_map)
        return associated_half_edge_in_3_map[init_half_edge]

    # Recursively transforms the irreducible quandrigulation to the three conected map.
    # The next and prev pointers are kept as before, but the opposite pointer in the
    # half edge is pointing to the opposite half-edge in the face.
    def __primal_map_bijection_rec(self, init_half_edge, associated_half_edges_in_3_map):
        # Associate the initial half edge
        initial_half_edge_association = HalfEdge()
        initial_half_edge_association.node_nr = init_half_edge.node_nr
        associated_half_edges_in_3_map[init_half_edge] = initial_half_edge_association

        # Associate the half edges that are on the same vertex as tie initial one.
        walker_half_edge = init_half_edge.next
        while walker_half_edge is not init_half_edge:
            walker_association = HalfEdge()
            walker_association.node_nr = walker_half_edge.node_nr
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
        while walker_half_edge is not init_half_edge or skipFirst is True:
            skipFirst = False
            opposite_half_edge_in_face = walker_half_edge.opposite.next.opposite.next
            # print(walker_half_edge.__str__()+ "    " +opposite_half_edge_in_face.__str__())

            # Check for already processed half edges
            if opposite_half_edge_in_face not in associated_half_edges_in_3_map:
                # Process the opposite half edge
                self.__primal_map_bijection_rec(
                    opposite_half_edge_in_face, associated_half_edges_in_3_map)

            # Make the actual opposite connection between the associations
            associated_half_edges_in_3_map[opposite_half_edge_in_face].opposite = associated_half_edges_in_3_map[
                walker_half_edge]
            associated_half_edges_in_3_map[walker_half_edge].opposite = associated_half_edges_in_3_map[
                opposite_half_edge_in_face]

            # Continue with the next edges
            walker_half_edge = walker_half_edge.next

    def test_primal_map(self):
        # print("Start test...")
        half_edges = self.create_sample_closure_output()

        primal_map = PrimalMap()
        three_map = primal_map.primal_map_bijection(half_edges[1])

        # Check the opposites - third output
        print(three_map)  # 9
        print(three_map.opposite)  # 1
        print(three_map.next)  # 35
        print(three_map.next.opposite)  # 2
        print(three_map.next.next)  # 22
        print(three_map.next.next.opposite)  # 3
        print(three_map.prior)  # 16
        print(three_map.prior.opposite)  # 4

        print()
        print(three_map.next.opposite.next)  # 8
        print(three_map.next.opposite.next.opposite)  # 36

        print()
        print(three_map.opposite.next)  # 31
        print(three_map.opposite.next.opposite)  # 10

    def create_sample_closure_output(self):
        half_edges = [HalfEdge() for i in range(65)]

        # Set node_nrs
        for i in range(1, 5): half_edges[i].node_nr = 1
        for i in range(5, 8): half_edges[i].node_nr = 6
        for i in range(8, 11): half_edges[i].node_nr = 13
        for i in range(11, 15): half_edges[i].node_nr = 7
        for i in range(15, 18): half_edges[i].node_nr = 8
        for i in range(18, 21): half_edges[i].node_nr = 2
        for i in range(21, 24): half_edges[i].node_nr = 3
        for i in range(24, 27): half_edges[i].node_nr = 9
        for i in range(27, 32): half_edges[i].node_nr = 10
        for i in range(32, 35): half_edges[i].node_nr = 12
        for i in range(35, 39): half_edges[i].node_nr = 5
        for i in range(39, 41): half_edges[i].node_nr = 11
        for i in range(41, 45): half_edges[i].node_nr = 4
        # Set opposite half-edges
        half_edges[1].opposite = half_edges[5]
        half_edges[5].opposite = half_edges[1]
        half_edges[2].opposite = half_edges[41]
        half_edges[41].opposite = half_edges[2]
        half_edges[3].opposite = half_edges[19]
        half_edges[19].opposite = half_edges[3]
        half_edges[4].opposite = half_edges[12]
        half_edges[12].opposite = half_edges[4]
        half_edges[6].opposite = half_edges[8]
        half_edges[8].opposite = half_edges[6]
        half_edges[7].opposite = half_edges[35]
        half_edges[35].opposite = half_edges[7]
        half_edges[9].opposite = half_edges[11]
        half_edges[11].opposite = half_edges[9]
        half_edges[13].opposite = half_edges[15]
        half_edges[15].opposite = half_edges[13]
        half_edges[16].opposite = half_edges[18]
        half_edges[18].opposite = half_edges[16]
        half_edges[17].opposite = half_edges[26]
        half_edges[26].opposite = half_edges[17]
        half_edges[14].opposite = half_edges[31]
        half_edges[31].opposite = half_edges[14]
        half_edges[10].opposite = half_edges[34]
        half_edges[34].opposite = half_edges[10]
        half_edges[32].opposite = half_edges[30]
        half_edges[30].opposite = half_edges[32]
        half_edges[33].opposite = half_edges[36]
        half_edges[36].opposite = half_edges[33]
        half_edges[39].opposite = half_edges[37]
        half_edges[37].opposite = half_edges[39]
        half_edges[29].opposite = half_edges[40]
        half_edges[40].opposite = half_edges[29]
        half_edges[27].opposite = half_edges[25]
        half_edges[25].opposite = half_edges[27]
        half_edges[21].opposite = half_edges[20]
        half_edges[20].opposite = half_edges[21]
        half_edges[23].opposite = half_edges[24]
        half_edges[24].opposite = half_edges[23]
        half_edges[28].opposite = half_edges[43]
        half_edges[43].opposite = half_edges[28]
        half_edges[38].opposite = half_edges[42]
        half_edges[42].opposite = half_edges[38]
        half_edges[44].opposite = half_edges[22]
        half_edges[22].opposite = half_edges[44]
        # Set next and prior
        half_edges[1].next = half_edges[2]
        half_edges[2].prior = half_edges[1]
        half_edges[2].next = half_edges[3]
        half_edges[3].prior = half_edges[2]
        half_edges[3].next = half_edges[4]
        half_edges[4].prior = half_edges[3]
        half_edges[4].next = half_edges[1]
        half_edges[1].prior = half_edges[4]
        half_edges[5].next = half_edges[6]
        half_edges[6].prior = half_edges[5]
        half_edges[6].next = half_edges[7]
        half_edges[7].prior = half_edges[6]
        half_edges[7].next = half_edges[5]
        half_edges[5].prior = half_edges[7]
        half_edges[8].next = half_edges[9]
        half_edges[9].prior = half_edges[8]
        half_edges[9].next = half_edges[10]
        half_edges[10].prior = half_edges[9]
        half_edges[10].next = half_edges[8]
        half_edges[8].prior = half_edges[10]
        half_edges[11].next = half_edges[12]
        half_edges[12].prior = half_edges[11]
        half_edges[12].next = half_edges[13]
        half_edges[13].prior = half_edges[12]
        half_edges[13].next = half_edges[14]
        half_edges[14].prior = half_edges[13]
        half_edges[14].next = half_edges[11]
        half_edges[11].prior = half_edges[14]
        half_edges[15].next = half_edges[16]
        half_edges[16].prior = half_edges[15]
        half_edges[16].next = half_edges[17]
        half_edges[17].prior = half_edges[16]
        half_edges[17].next = half_edges[15]
        half_edges[15].prior = half_edges[17]
        half_edges[18].next = half_edges[19]
        half_edges[19].prior = half_edges[18]
        half_edges[19].next = half_edges[20]
        half_edges[20].prior = half_edges[19]
        half_edges[20].next = half_edges[18]
        half_edges[18].prior = half_edges[20]
        half_edges[21].next = half_edges[22]
        half_edges[22].prior = half_edges[21]
        half_edges[22].next = half_edges[23]
        half_edges[23].prior = half_edges[22]
        half_edges[23].next = half_edges[21]
        half_edges[21].prior = half_edges[23]
        half_edges[24].next = half_edges[25]
        half_edges[25].prior = half_edges[24]
        half_edges[25].next = half_edges[26]
        half_edges[26].prior = half_edges[25]
        half_edges[26].next = half_edges[24]
        half_edges[24].prior = half_edges[26]
        half_edges[27].next = half_edges[28]
        half_edges[28].prior = half_edges[27]
        half_edges[28].next = half_edges[29]
        half_edges[29].prior = half_edges[28]
        half_edges[29].next = half_edges[30]
        half_edges[30].prior = half_edges[29]
        half_edges[30].next = half_edges[31]
        half_edges[31].prior = half_edges[30]
        half_edges[31].next = half_edges[27]
        half_edges[27].prior = half_edges[31]
        half_edges[32].next = half_edges[33]
        half_edges[33].prior = half_edges[32]
        half_edges[33].next = half_edges[34]
        half_edges[34].prior = half_edges[33]
        half_edges[34].next = half_edges[32]
        half_edges[32].prior = half_edges[34]
        half_edges[35].next = half_edges[36]
        half_edges[36].prior = half_edges[35]
        half_edges[36].next = half_edges[37]
        half_edges[37].prior = half_edges[36]
        half_edges[37].next = half_edges[38]
        half_edges[38].prior = half_edges[37]
        half_edges[38].next = half_edges[35]
        half_edges[35].prior = half_edges[38]
        half_edges[39].next = half_edges[40]
        half_edges[40].prior = half_edges[39]
        half_edges[40].next = half_edges[39]
        half_edges[39].prior = half_edges[40]
        half_edges[41].next = half_edges[42]
        half_edges[42].prior = half_edges[41]
        half_edges[42].next = half_edges[43]
        half_edges[43].prior = half_edges[42]
        half_edges[43].next = half_edges[44]
        half_edges[44].prior = half_edges[43]
        half_edges[44].next = half_edges[41]
        half_edges[41].prior = half_edges[44]

        # Mark the half edges from the haxagon
        half_edges[3].is_hexagonal = True
        half_edges[19].is_hexagonal = True
        half_edges[20].is_hexagonal = True
        half_edges[21].is_hexagonal = True
        half_edges[22].is_hexagonal = True
        half_edges[44].is_hexagonal = True
        half_edges[42].is_hexagonal = True
        half_edges[38].is_hexagonal = True
        half_edges[35].is_hexagonal = True
        half_edges[7].is_hexagonal = True
        half_edges[5].is_hexagonal = True
        half_edges[1].is_hexagonal = True

        return half_edges
