import random as rnd

from framework.generic_classes import CombinatorialClass
from planar_graph_sampler.combinatorial_classes.half_edge_graph import HalfEdgeGraph


class IrreducibleDissection(HalfEdgeGraph):
    """

    """

    def __init__(self, half_edge):
        """

        :param half_edge: Half-edge on hexagon boundary in ccw direction.
        """
        assert half_edge.is_hexagonal
        if half_edge.color is not 'black':
            half_edge = half_edge.opposite.next
        assert half_edge.color is 'black'
        super().__init__(half_edge)

    def get_hexagonal_edges(self):
        """
        Gets the three half-edges on the hexagonal boundary incident to a black node and point in ccw direction.
        :return:
        """
        first = self.half_edge
        res = [first]
        second = first.opposite.next.opposite.next
        res.append(second)
        third = second.opposite.next.opposite.next
        res.append(third)
        for he in res:
            assert he.is_hexagonal and he.color is 'black'
        return res

    def root_at_random_hexagonal_edge(self):
        """
        :return:
        """
        self.half_edge = rnd.choice(self.get_hexagonal_edges())

    def get_u_size(self):
        """
        The u-size is the number of faces.
        :return: Number of faces.
        """
        # Not really sure if this is correct.
        return self.number_of_half_edges() / 4

    def get_l_size(self):
        """
        The l-size is the number of black vertices.
        :return:
        """
        raise NotImplementedError

    def is_admissible(self):
        """
        Check whether there is a path of length three which include a inner edge from the root vertex
        to the opposite outer vertex.

        :return: True iff this dissection is admissible.
        """

        # Will be used for checking in the bfs.
        outer_vertex_half_edge = self.half_edge.opposite.next.opposite.next.opposite.next
        # print ('%s    %s' % (self.half_edge.node_nr, outer_vertex_half_edge.node_nr))

        # Creates the queue for the BFS.
        queue = list()
        # Put the init half edge into the queue.
        queue.append((self.half_edge, 0, False, set()))

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

    def to_networkx_graph(self, include_unpaired=None):
        from planar_graph_sampler.combinatorial_classes.half_edge_graph import color_scale
        # Get dict of nodes.
        nodes = self.half_edge.get_node_list()
        # Include the leaves as well.
        G = super().to_networkx_graph(include_unpaired=False)
        for v in G:
            if nodes[v][0].is_hexagonal:
                G.nodes[v]['color'] = '#e8f442'
            else:
                G.nodes[v]['color'] = '#eeeeee'
            if nodes[v][0].color is 'black':
                # Make black nodes darker.
                G.nodes[v]['color'] = color_scale(G.nodes[v]['color'], 0.5)
        return G
