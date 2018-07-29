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

from planar_graph_sampler.bijections.primal_map import PrimalMap


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
        outer_vertex_half_edge = init_half_edge.opposite.next.opposite.next.opposite.next
        print ('%s    %s' % (init_half_edge.node_nr, outer_vertex_half_edge.node_nr))

        # Creates the queue for the BFS.
        queue = list()
        # Put the init half edge into the queue.
        queue.append((init_half_edge, 0, False, set()))

        while len(queue) != 0:
            # Pop the _first element from the FIFO queue.
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
