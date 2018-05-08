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
        self._k3_3 = nx.LCF_graph(6, [3, -3], 3)

    @staticmethod
    def check_embedding(G: nx.Graph, embedding):
        """Raises an exception if the combinatorial embedding is not correct

        Parameters
        ----------
        G : NetworkX graph
        embedding : a dict mapping nodes to a list of edges
                This specifies the ordering of the outgoing edges from a node for a combinatorial embedding
        """
        if embedding is None:
            return
        # Calculate connected components
        connected_components = nx.connected_components(G)

        # Check all components
        for component in connected_components:
            # Keep track of already seen faces
            face_set = set()
            # Save already computed faces. Mapping edges (tuple of two nodes) to their left face
            face_map = {}
            for starting_node in component:
                if starting_node not in embedding:
                    raise nx.NetworkXException("The embedding is missing a node.")
                # Calculate all faces around starting_node
                for face_idx in range(0,len(embedding[starting_node])):
                    outgoing_node = embedding[starting_node][face_idx]
                    incoming_node = embedding[starting_node][face_idx-1] # access to -1 wraps around
                    # 1. Check if the face has already been calculated (is this neccessary)
                    # TODO
                    # 2. Calculate face
                    # TODO
                    # 3. Save face
                    # TODO

    def check_counterexample(self, G: nx.Graph, subdivision_nodes: set):
        """Raises an exception if the subdivision_nodes is not a counterexample for planarity of G

        Parameters
        ----------
        G : NetworkX graph
        subdivision_nodes : A set of nodes inducing a subgraph as a counterexample
        """

        # 1. Create the sub graph (sub)
        sub_graph: nx.Graph = nx.Graph(G.subgraph(subdivision_nodes))

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
            if degree == 2:
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
            return nx.is_isomorphic(self._k5, sub_graph)
        elif len(sub_graph) == 6:
            return nx.is_isomorphic(self._k3_3, sub_graph)
        else:
            return False

    def check_graph(self, G, is_planar = None, msg = None):
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
        is_planar_lr, result = lr_planarity.check_planarity(G)

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
            # Check counter example
            self.check_counterexample(G, result)
        else:
            # Check embedding
            self.check_embedding(G, result)

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
    t.test_planar_with_selfloop()
