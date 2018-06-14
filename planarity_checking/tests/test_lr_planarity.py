#!/usr/bin/env python
from nose.tools import assert_equals

import networkx as nx

from planarity_checking import lr_planarity

class TestLRPlanarity:
    """Nose Unit tests for the :mod:`networkx.algorithms.TODO` module.

    Tests three things:
     - Check that the result is correct (returns planar if and only if the graph is actually planar)
     - In case a counter example is retured: Check if it is correct
     - In case an embedding is returned: Check if its actually an embedding

    """

    def setUp(self):
        self._k5 = nx.complete_graph(5)
        self._k3_3 = nx.complete_bipartite_graph(3, 3)

    @staticmethod
    def check_embedding(G: nx.Graph, embedding):
        """Raises an exception if the combinatorial embedding is not correct
        # TODO: Consider special cases for self loops
        # TODO: More descriptive exceptions
        Parameters
        ----------
        G : NetworkX graph
        embedding : a dict mapping nodes to a list of edges
                This specifies the ordering of the outgoing edges from a node for a combinatorial embedding

        Notes
        -----
        Checks the following things:
          - The type of the embedding is a dict
          - Every node in the graph has to be contained in the embedding
          - The original graph actually contains the adjecency structure from the embedding
          - A node is not contained twice in the neighbor list from a node in the embedding
          - The cycles around each face are correct (no unexpected cycle)
          - Every outgoing edge in the embedding also has an incoming edge in the embedding
          - Checks that all edges in the original graph have been counted
          - Checks that euler's formula holds for the number of edges, faces and nodes for each component

        The number of faces is determined by using the combinatorial embedding to folowing a path around face
        While following the path around the face every edge on the way (in this direction) is marked such that the face
        is not counted twice.
        """

        if not isinstance(embedding, dict):
            raise nx.NetworkXException("Bad embedding. Not of type dict")

        # Calculate connected components
        connected_components = nx.connected_components(G)

        # Check all components
        for component in connected_components:
            if len(component) == 1:
                if len(embedding[list(component)[0]]) != 0:
                    # The node should not have a neighbor
                    raise nx.NetworkXException("Bad embedding. Single node component has neighbors.")
                else:
                    continue

            component_subgraph = nx.subgraph(G, component)
            # Count the number of faces
            number_faces = 0
            # Keep track of which faces have already been counted.
            # Set of edges where the face to the left was already counted
            edges_counted = set()
            for starting_node in component:
                if starting_node not in embedding:
                    raise nx.NetworkXException("The embedding is missing a node.")
                # Keep track of all neighbors of the starting node to ensure no neighbor is contained twice
                neighbor_set = set()
                # Calculate all faces around starting_node
                for face_idx in range(0, len(embedding[starting_node])):
                    outgoing_node = embedding[starting_node][face_idx]
                    incoming_node = embedding[starting_node][face_idx-1]  # access to -1 wraps around
                    # 1. Check that the edges exists in the original graph (check both directions in case of diGraph)
                    has_outgoing_edge = component_subgraph.has_edge(starting_node, outgoing_node)
                    has_outgoing_edge_reversed = component_subgraph.has_edge(outgoing_node, starting_node)
                    if not has_outgoing_edge and not has_outgoing_edge_reversed:
                        raise nx.NetworkXException("Bad planar embedding. The embedding contains an edge not present in the original graph")

                    # 2. Check that a neighbor node is not contained twice in the adjecency list
                    if outgoing_node in neighbor_set:
                        raise nx.NetworkXException("Bad planar embedding. A node is contained twice in the adjacency list.")
                    neighbor_set.add(outgoing_node)

                    # 3. Check if the face has already been calculated
                    if (starting_node, outgoing_node) in edges_counted:
                        # This face was already counted
                        continue
                    edges_counted.add((starting_node, outgoing_node))

                    # 4. Count this face
                    number_faces += 1

                    # 5. Add all edges to edges_counted which have this face to their left
                    visited_nodes = set()  # Keep track of visited nodes
                    current_node = starting_node
                    next_node = outgoing_node
                    while next_node != starting_node:  # Abort if the cycle is complete
                        # Check that we have not visited the current node yet (starting_node lies outside of the cycle).
                        if current_node in visited_nodes:
                            raise nx.NetworkXException("Bad planar embedding. A node is contained twice in a cycle aound a face.")
                        visited_nodes.add(current_node)

                        # Obtain outgoing edge from next node
                        try:
                            incoming_idx = embedding[next_node].index(current_node)
                        except ValueError:
                            raise nx.NetworkXException("Bad planar embedding. No incoming edge for an outgoing edge.")
                        # Outgoing edge is to the right of the incoming idx (or the idx rolls over to 0)
                        if incoming_idx == len(embedding[next_node])-1:
                            outgoing_idx = 0
                        else:
                            outgoing_idx = incoming_idx + 1

                        # Set next edge
                        current_node = next_node
                        next_node = embedding[next_node][outgoing_idx]
                        current_edge = (current_node, next_node)

                        # All edges around this face should not have been counted
                        if current_edge in edges_counted:
                            raise nx.NetworkXException("Bad planar embedding. The number of faces could not be determined.")

                        # Remember that this edge has been counted
                        edges_counted.add(current_edge)

                    # 6. Check if the incoming node is correct
                    assert_equals(current_node, incoming_node, "Bad planar embedding. A path around a face did not end at the expected incoming node.")

            # Length of edges_counted must be even
            if len(edges_counted) % 2 != 0:
                raise nx.NetworkXException("Counted an uneven number of half edges")
            number_edges = len(edges_counted) // 2
            number_nodes = len(component)

            # Check that all edges have been counted
            for u, v in component_subgraph.edges:
                if u != v and ( (u, v) not in edges_counted or (v, u) not in edges_counted) :
                    raise nx.NetworkXException("Bad planar embedding. An edge has not been counted")

            # Check if the number of faces matches the expected value (euler's formula)
            if number_nodes - number_edges + number_faces != 2:
                raise nx.NetworkXException("Bad planar embedding. Number of faces does not match euler's formula.")

    def check_counterexample(self, G, subdivision_nodes):
        """Raises an exception if the subdivision_nodes is not a counterexample for planarity of G

        Parameters
        ----------
        G : NetworkX graph
        subdivision_nodes : A set of nodes inducing a subgraph as a counterexample
        """
        # 1. Create the sub graph (sub)
        sub_graph = nx.Graph(G.subgraph(subdivision_nodes))

        # 2. Remove self loops
        for u in sub_graph:
            if sub_graph.has_edge(u, u):
                sub_graph.remove_edge(u, u)

        # Keep track of nodes we might need to contract
        contract = list(subdivision_nodes)

        # 3. Contract Edges
        while len(contract) > 0:
            contract_node = contract.pop()
            if contract_node not in sub_graph:
                # Node was already contracted
                continue
            degree = sub_graph.degree[contract_node]
            # Check if we can remove the node
            if degree == 2:  # TODO: Can it happen that we have isolated nodes that we might want to remove?
                # Get the two neighbors
                neighbors = iter(sub_graph[contract_node])
                u = next(neighbors)
                v = next(neighbors)
                # Save nodes for later
                contract.append(u)
                contract.append(v)
                # Contract edge
                sub_graph.remove_node(contract_node)
                sub_graph.add_edge(u, v)

        # 4. Check for isomorphism with K5 or K3_3 graphs
        if len(sub_graph) == 5:
            if not nx.is_isomorphic(self._k5, sub_graph):
                raise nx.NetworkXException("Bad counter example.")
        elif len(sub_graph) == 6:
            if not nx.is_isomorphic(self._k3_3, sub_graph):
                raise nx.NetworkXException("Bad counter example.")
        else:
            raise nx.NetworkXException("Bad counter example.")

    def check_graph(self, G, is_planar=None, msg=None):
        """Raises an exception if the lr_planarity check returs a wrong result

        Parameters
        ----------
        G : NetworkX graph
        is_planar : bool
                The expected result of the planarity check.
                If set to None only counter example or embedding are verified.
        msg : str
                A message for the exception if the is_planar argument does not match the result.

        """

        # Obtain planarity results
        is_planar_lr, result = lr_planarity.check_planarity(G, counterexample=True)

        if is_planar is not None:
            # Set a default message for the assert
            if msg is None:
                if is_planar:
                    msg = "Wrong result of planarity check. Should be planar."
                else:
                    msg = "Wrong result of planarity check. Should be non-planar."
            # Check if the result is as expected
            assert_equals(is_planar, is_planar_lr, msg)

        if is_planar:
            # Check embedding
            self.check_embedding(G, result)
        else:
            # Check counter example
            self.check_counterexample(G, result)

    def test_simple_planar_graph(self):
        e = [(1, 2), (2, 3), (3, 4), (4, 6), (6, 7), (7, 1), (1, 5), (5, 2), (2, 4), (4, 5), (5, 7)]
        self.check_graph(nx.Graph(e), is_planar=True)

    def test_planar_with_selfloop(self):
        e = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (1, 2), (1, 3), (1, 5), (2, 5), (2, 4), (3, 4), (3, 5), (4, 5)]
        self.check_graph(nx.Graph(e), is_planar=True)

    def test_k3_3(self):
        self.check_graph(self._k3_3, is_planar=False)

    def test_k5(self):
        self.check_graph(self._k5, is_planar=False)

    def test_multiple_components_planar(self):
        e = [(1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4)]
        self.check_graph(nx.Graph(e), is_planar=True)

    def test_multiple_components_non_planar(self):
        G = nx.complete_graph(5)
        # Add another planar component to the non planar component --> G stays non planar
        G.add_edges_from([(6, 7), (7, 8), (8, 6)])
        self.check_graph(G, is_planar=False)

    def test_non_planar_with_selfloop(self):
        G = nx.complete_graph(5)
        # Add self loops
        for i in range(5):
            G.add_edge(i, i)
        self.check_graph(G, is_planar=False)

    def test_non_planar1(self):
        """Tests a graph that has no subgraph directly isomorph to K5 or K3_3"""
        e = [(1, 5), (1, 6), (1, 7), (2, 6), (2, 3), (3, 5), (3, 7), (4, 5), (4, 6), (4, 7)]
        self.check_graph(nx.Graph(e), is_planar=False)

    def test_loop(self):
        # currently fails in dfs3 with KeyError at selfloop
        e = [(1, 2), (2, 2)]
        G = nx.Graph(e)
        self.check_graph(G, is_planar=True)

    def test_comp(self):
        # currently fails embedding check (due to euler's formula)
        e = [(1, 2), (3, 4)]
        G = nx.Graph(e)
        G.remove_edge(1, 2)
        self.check_graph(G, is_planar=True)

    def test_goldner_harary(self):
        # goldner-harary graph
        # http://en.wikipedia.org/wiki/Goldner%E2%80%93Harary_graph
        # a maximal planar graph
        e = [
            (1, 2), (1, 3), (1, 4), (1, 5), (1, 7), (1, 8), (1, 10),
            (1, 11), (2, 3), (2, 4), (2, 6), (2, 7), (2, 9), (2, 10),
            (2, 11), (3, 4), (4, 5), (4, 6), (4, 7), (5, 7), (6, 7),
            (7, 8), (7, 9), (7, 10), (8, 10), (9, 10), (10, 11)
        ]
        G = nx.Graph(e)
        self.check_graph(G, is_planar=True, msg="Golder-Harary maximal planargraph was classified as planar")


if __name__ == '__main__':
    # I have temporarily added a main method so you don't actually have to run nose
    t = TestLRPlanarity()
    t.setUp()
    t.test_goldner_harary()
    t.test_k3_3()
    t.test_k5()
    t.test_non_planar1()
    t.test_simple_planar_graph()
    t.test_non_planar_with_selfloop()
    t.test_multiple_components_planar()
    t.test_multiple_components_non_planar()
    t.test_planar_with_selfloop()
    t.test_loop()
    t.test_comp()