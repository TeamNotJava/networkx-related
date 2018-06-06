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
Check the dissection if ti is irreducible, which means there is no path of length 3 from the root vertex to
the opposite outer vertex.
"""

from framework.bijections.primal_map import PrimalMap


def check_admissibility(dissection):
    """To be used in the grammar.

    :param dissection:
    :return: True if the dissection is irreducible, False otherwise.
    """
    return AdmissibilityChecker().check_admissibility(dissection)


class AdmissibilityChecker:

    def check_admissibility(self, init_half_edge):
        ''' Check whether there is a path of length three which include a innter edge from the root vertex
        to the opposite outer vertex.
        '''

        # Will be used for checking in the bfs.
        # TODO check which Marta again just to be sure
        outer_vertex_half_edge = init_half_edge.opposite

        # Creates the queue for the BFS.
        queue = list()
        # Put the init half edge into the queue.
        queue.append((init_half_edge, 0, False, set()))

        while len(queue) != 0:
            # Pop the first element from the FIFO queue.
            top_element = queue.pop(0)

            # Extract the components from the top element
            top_half_edge = top_element[0]
            distance = top_element[1]
            has_been_inner_edge_included = top_element[2]
            visited_nodes = top_element[3]

            # updated the visited_nodes_set
            visited_nodes.add(top_half_edge.node_nr)

            # start BFS for its neighbours
            walker_half_edge = top_half_edge.next
            while walker_half_edge is not top_half_edge:

                opposite = walker_half_edge.opposite
                # Skipe the vertex if it was already visited.
                if opposite in visited_nodes: continue

                # Prepare the new components of the element
                updated_distance = distance + 1
                new_visited_nodes = set()
                new_visited_nodes.update(visited_nodes)
                inner_edge_included = has_been_inner_edge_included or (opposite.is_hexagonal is False)

                # If the distance is smaller than 3 then the element is added into the queue
                if updated_distance < 3:
                    queue.append((opposite, updated_distance, inner_edge_included, new_visited_nodes))
                else:
                    # If the distance is equal to 3 than we check whether the new vertex is the outer one and
                    # does an inner edge have been included in the path. If both conditions are True, then a path
                    # has been found which means that the dissection is not irreducible. -> Return false.
                    if opposite.node_nr == outer_vertex_half_edge.node_nr and inner_edge_included:
                        return False

                # Continue with the next half edge.
                walker_half_edge = walker_half_edge.next

        # A path has not been found, therefore the dissection is irreducible and we return True.
        return True


    def test_admissibility_check(self):
        half_edges_list = PrimalMap().create_sample_closure_output()

        is_admissible = AdmissibilityChecker().check_admissibility(half_edges_list[2])
        print(is_admissible)  # False

        # Test with removing edges
        half_edges_list[27].next = half_edges_list[29]
        half_edges_list[29].prior = half_edges_list[27]

        half_edges_list[42].next = half_edges_list[44]
        half_edges_list[44].prior = half_edges_list[42]

        is_admissible = AdmissibilityChecker().check_admissibility(half_edges_list[2])
        print(is_admissible)  # True

        # Extend the test with adding edges
        half_edges_list[60].node_nr = 3
        half_edges_list[22].next = half_edges_list[60]
        half_edges_list[60].prior = half_edges_list[22]
        half_edges_list[60].next = half_edges_list[23]
        half_edges_list[23].prior = half_edges_list[60]

        half_edges_list[55].node_nr = 5
        half_edges_list[37].next = half_edges_list[55]
        half_edges_list[55].prior = half_edges_list[37]
        half_edges_list[55].next = half_edges_list[38]
        half_edges_list[38].prior = half_edges_list[55]

        half_edges_list[59].node_nr = 10
        half_edges_list[27].next = half_edges_list[59]
        half_edges_list[59].prior = half_edges_list[27]
        half_edges_list[59].next = half_edges_list[28]
        half_edges_list[28].prior = half_edges_list[59]
        half_edges_list[28].next = half_edges_list[29]
        half_edges_list[29].prior = half_edges_list[28]

        half_edges_list[42].next = half_edges_list[43]
        half_edges_list[44].prior = half_edges_list[43]

        for i in range(49, 52):half_edges_list[i].node_nr = 14
        for i in range(52, 55):half_edges_list[i].node_nr = 16
        for i in range(56, 59):half_edges_list[i].node_nr = 15

        # Reassign opposites
        half_edges_list[28].opposite = half_edges_list[54]
        half_edges_list[54].opposite = half_edges_list[28]
        half_edges_list[60].opposite = half_edges_list[56]
        half_edges_list[56].opposite = half_edges_list[60]
        half_edges_list[59].opposite = half_edges_list[58]
        half_edges_list[58].opposite = half_edges_list[59]
        half_edges_list[50].opposite = half_edges_list[57]
        half_edges_list[57].opposite = half_edges_list[50]
        half_edges_list[43].opposite = half_edges_list[51]
        half_edges_list[51].opposite = half_edges_list[43]
        half_edges_list[49].opposite = half_edges_list[52]
        half_edges_list[52].opposite = half_edges_list[49]
        half_edges_list[55].opposite = half_edges_list[53]
        half_edges_list[53].opposite = half_edges_list[55]

        is_admissible = AdmissibilityChecker().check_admissibility(half_edges_list[2])
        print(is_admissible)  # True

if __name__ == "__main__":
    AdmissibilityChecker().test_admissibility_check()