import networkx as nx
from nose.tools import assert_equals
from planarity_checking import lr_planarity  #TODO: Change this to the nx import


class TestLRPlanarity:
    """Nose Unit tests for the :mod:`networkx.algorithms.TODO` module.

    Tests three things:
    1. Check that the result is correct
        (returns planar if and only if the graph is actually planar)
    2. In case a counter example is returned: Check if it is correct
    3. In case an embedding is returned: Check if its actually an embedding
    """

    @staticmethod
    def check_graph(G, is_planar=None):
        """Raises an exception if the lr_planarity check returns a wrong result

        Parameters
        ----------
        G : NetworkX graph
        is_planar : bool
            The expected result of the planarity check.
            If set to None only counter example or embedding are verified.

        """

        # obtain results of planarity check
        is_planar_lr, result = lr_planarity.check_planarity(G, True)

        if is_planar is not None:
            # set a message for the assert
            if is_planar:
                msg = "Wrong planarity check result. Should be planar."
            else:
                msg = "Wrong planarity check result. Should be non-planar."

            # check if the result is as expected
            assert_equals(is_planar, is_planar_lr, msg)

            if is_planar:
                # check embedding
                check_embedding(G, result)
            else:
                # check counter example
                check_counterexample(G, result)

    def test_simple_planar_graph(self):
        e = [(1, 2), (2, 3), (3, 4), (4, 6), (6, 7), (7, 1), (1, 5),
             (5, 2), (2, 4), (4, 5), (5, 7)]
        self.check_graph(nx.Graph(e), is_planar=True)

    def test_planar_with_selfloop(self):
        e = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (1, 2), (1, 3),
             (1, 5), (2, 5), (2, 4), (3, 4), (3, 5), (4, 5)]
        self.check_graph(nx.Graph(e), is_planar=True)

    def test_k3_3(self):
        self.check_graph(nx.complete_bipartite_graph(3, 3), is_planar=False)

    def test_k5(self):
        self.check_graph(nx.complete_graph(5), is_planar=False)

    def test_multiple_components_planar(self):
        e = [(1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4)]
        self.check_graph(nx.Graph(e), is_planar=True)

    def test_multiple_components_non_planar(self):
        G = nx.complete_graph(5)
        # add another planar component to the non planar component
        # G stays non planar
        G.add_edges_from([(6, 7), (7, 8), (8, 6)])
        self.check_graph(G, is_planar=False)

    def test_non_planar_with_selfloop(self):
        G = nx.complete_graph(5)
        # add self loops
        for i in range(5):
            G.add_edge(i, i)
        self.check_graph(G, is_planar=False)

    def test_non_planar1(self):
        # tests a graph that has no subgraph directly isomorph to K5 or K3_3
        e = [(1, 5), (1, 6), (1, 7), (2, 6), (2, 3), (3, 5), (3, 7), (4, 5),
             (4, 6), (4, 7)]
        self.check_graph(nx.Graph(e), is_planar=False)

    def test_loop(self):
        # test a graph with a selfloop
        e = [(1, 2), (2, 2)]
        G = nx.Graph(e)
        self.check_graph(G, is_planar=True)

    def test_comp(self):
        # test multiple component graph
        e = [(1, 2), (3, 4)]
        G = nx.Graph(e)
        G.remove_edge(1, 2)
        self.check_graph(G, is_planar=True)

    def test_goldner_harary(self):
        # test goldner-harary graph (a maximal planar graph)
        e = [
            (1, 2), (1, 3), (1, 4), (1, 5), (1, 7), (1, 8), (1, 10),
            (1, 11), (2, 3), (2, 4), (2, 6), (2, 7), (2, 9), (2, 10),
            (2, 11), (3, 4), (4, 5), (4, 6), (4, 7), (5, 7), (6, 7),
            (7, 8), (7, 9), (7, 10), (8, 10), (9, 10), (10, 11)
        ]
        G = nx.Graph(e)
        self.check_graph(G, is_planar=True)

    def test_single_component(self):
        # Test a graph with only a single node
        G = nx.Graph()
        G.add_node(1)
        self.check_graph(G, is_planar=True)


def check_embedding(G, embedding):
    """Raises an exception if the combinatorial embedding is not correct

    Parameters
    ----------
    G : NetworkX graph
    embedding : a dict mapping nodes to a list of edges
        This specifies the ordering of the outgoing edges from a node for
        a combinatorial embedding

    Notes
    -----
    Checks the following things:
        - The type of the embedding is a dict
        - Every node in the graph has to be contained in the embedding
        - The original graph actually contains the adjacency structure
            from the embedding
        - A node is not contained twice in the neighbor list from a node
            in the embedding
        - The cycles around each face are correct (no unexpected cycle)
        - Every outgoing edge in the embedding also has an incoming edge
            in the embedding
        - Checks that all edges in the original graph have been counted
        - Checks that euler's formula holds for the number of edges, faces,
            and nodes for each component

    The number of faces is determined by using the combinatorial embedding
    to follow a path around face. While following the path around the face
    every edge on the way (in this direction) is marked such that the
    face is not counted twice.
    """

    if not isinstance(embedding, dict):
        raise nx.NetworkXException("Bad embedding. Not of type dict")

    # calculate connected components
    connected_components = nx.connected_components(G)

    # check all components
    for component in connected_components:
        if len(component) == 1:
            if len(embedding[list(component)[0]]) != 0:
                # the node should not have a neighbor
                raise nx.NetworkXException(
                    "Bad embedding. Single node component has neighbors.")
            else:
                continue

        component_subgraph = nx.subgraph(G, component)
        # count the number of faces
        number_faces = 0
        # keep track of which faces have already been counted
        # set of edges where the face to the left was already counted
        edges_counted = set()
        for starting_node in component:
            if starting_node not in embedding:
                raise nx.NetworkXException(
                    "Bad embedding. The embedding is missing a node.")
            # keep track of all neighbors of the starting node to ensure no
            # neighbor is contained twice
            neighbor_set = set()
            # calculate all faces around starting_node
            for face_idx in range(0, len(embedding[starting_node])):
                if count_face(embedding, starting_node, face_idx,
                              component_subgraph, neighbor_set, edges_counted):
                    number_faces += 1

        # Length of edges_counted must be even
        if len(edges_counted) % 2 != 0:
            raise nx.NetworkXException(
                "Bad embedding. Counted an uneven number of half edges")
        number_edges = len(edges_counted) // 2
        number_nodes = len(component)

        # Check that all edges have been counted
        for u, v in component_subgraph.edges:
            if u != v and ((u, v) not in edges_counted or
                           (v, u) not in edges_counted):
                raise nx.NetworkXException(
                    "Bad planar embedding. "
                    "An edge has not been counted")

        if number_nodes - number_edges + number_faces != 2:
            # number of faces don't match the expected value (euler's formula)
            raise nx.NetworkXException(
                "Bad planar embedding. "
                "Number of faces does not match euler's formula.")


def count_face(embedding, starting_node, face_idx, component_subgraph,
               neighbor_set, edges_counted):
    """Checks if face was not counted and marks it so it is not counted twice

    The parameters starting_node and face_idx uniquely define a face by
    following the path that starts in starting_node, where we take the
    half-edge from the embedding at embedding[starting_node][face_idx].
    We check that this face was not already counted by checking that no
    half-edge on the path is already contained in edges_counted. We prevent
    that the face is counted twice by adding all half-edges to edges-counted.

    Parameters
    ----------
    embedding: dict
        The embedding that defines the faces
    starting_node:
        A node on the face
    face_idx: int
        Index of the half-edge in embedding[starting_node]
    component_subgraph: NetworkX graph
        The current component of the original graph
        (to verify the edges from the embedding are actually present)
    neighbor_set: set
        Set of all neighbors of starting_node that have already been visited
    edges_counted: set
        Set of all half-edges that belong to a face that has been counted

    Returns
    -------
    is_new_face: bool
        The face has not been counted
    """
    outgoing_node = embedding[starting_node][face_idx]
    incoming_node = embedding[starting_node][face_idx - 1]

    # 1. Check that the edges exists in the original graph
    # (check both directions in case of diGraph)
    has_outgoing_edge = component_subgraph.has_edge(
        starting_node, outgoing_node)
    has_outgoing_edge_reversed = component_subgraph.has_edge(
        outgoing_node, starting_node)
    if not has_outgoing_edge and not has_outgoing_edge_reversed:
        raise nx.NetworkXException(
            "Bad planar embedding."
            "The embedding contains an edge not present in the original graph")

    # 2. Check that a neighbor node is not contained twice in the adj list
    if outgoing_node in neighbor_set:
        raise nx.NetworkXException(
            "Bad planar embedding. "
            "A node is contained twice in the adjacency list.")
    neighbor_set.add(outgoing_node)

    # 3. Check if the face has already been calculated
    if (starting_node, outgoing_node) in edges_counted:
        # This face was already counted
        return False
    edges_counted.add((starting_node, outgoing_node))

    # 4. Add all edges to edges_counted which have this face to their left
    visited_nodes = set()  # Keep track of visited nodes
    current_node = starting_node
    next_node = outgoing_node
    while next_node != starting_node:
        # cycle is not completed yet

        # check that we have not visited the current node yet
        # (starting_node lies outside of the cycle).
        if current_node in visited_nodes:
            raise nx.NetworkXException(
                "Bad planar embedding. A node is contained "
                "twice in a cycle aound a face.")
        visited_nodes.add(current_node)

        # obtain outgoing edge from next node
        try:
            incoming_idx = embedding[next_node].index(current_node)
        except ValueError:
            raise nx.NetworkXException(
                "Bad planar embedding. No incoming edge for an outgoing edge.")
        # outgoing edge is to the right of the incoming idx
        # (or the idx rolls over to 0)
        if incoming_idx == len(embedding[next_node]) - 1:
            outgoing_idx = 0
        else:
            outgoing_idx = incoming_idx + 1

        # set next edge
        current_node = next_node
        next_node = embedding[next_node][outgoing_idx]
        current_edge = (current_node, next_node)

        # all edges around this face should not have been counted
        if current_edge in edges_counted:
            raise nx.NetworkXException(
                "Bad planar embedding. "
                "The number of faces could not be determined.")

        # remember that this edge has been counted
        edges_counted.add(current_edge)

    # 5. Check if the incoming node is correct
    assert_equals(current_node, incoming_node,
                  "Bad planar embedding. "
                  "A path did not end at the expected incoming node.")

    # 6. Count this face
    return True


def check_counterexample(G, subdivision_nodes):
    """Raises an exception if the counterexample is wrong.

    Parameters
    ----------
    G : NetworkX graph
    subdivision_nodes : set
        A set of nodes inducing a subgraph as a counterexample
    """
    # 1. Create the sub graph
    sub_graph = nx.Graph(G.subgraph(subdivision_nodes))

    # 2. Remove self loops
    for u in sub_graph:
        if sub_graph.has_edge(u, u):
            sub_graph.remove_edge(u, u)

    # keep track of nodes we might need to contract
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
        if not nx.is_isomorphic(nx.complete_graph(5), sub_graph):
            raise nx.NetworkXException("Bad counter example.")
    elif len(sub_graph) == 6:
        if not nx.is_isomorphic(nx.complete_bipartite_graph(3, 3), sub_graph):
            raise nx.NetworkXException("Bad counter example.")
    else:
        raise nx.NetworkXException("Bad counter example.")

if __name__ == '__main__':
    # I have temporarily added a main method so you don't actually have to run nose
    t = TestLRPlanarity()
    t.test_planar_with_selfloop()
    t.setUp()
    t.test_goldner_harary()
    t.test_k3_3()
    t.test_k5()
    t.test_non_planar1()
    t.test_simple_planar_graph()
    t.test_non_planar_with_selfloop()
    t.test_multiple_components_planar()
    t.test_multiple_components_non_planar()
    t.test_loop()
    t.test_comp()
    t.test_single_component()
