from collections import defaultdict
from copy import deepcopy
import networkx as nx


def check_planarity(G):
    """Checks if a graph is planar and returns a counter example or an embedding

     A graph is said to be planar, if it can be drawn in the plane without
     edge intersections.

    Parameters
    ----------
    G : graph
        A NetworkX graph

    Returns
    -------
    is_planar : bool
        Is true if the graph is planar

    result : TODO
        If the graph is planar this is a planar embedding
        If the graph is not planar this is a counter example

    Notes
    -----
    TODO
    References
    ----------
    .. [1] Ulrik Brandes:
      The Left-Right Planarity Test
      2009
      http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.217.9208
    """

    planarity = LRPlanarity(G)
    try:
        embedding = planarity.lr_planarity()
    except nx.NetworkXUnfeasible:
        return False, planarity.get_counterexample()
    return True, embedding


class Interval(object):
    def __init__(self, low=None, high=None):
        self.low = low
        self.high = high

    def empty(self):
        return self.low is None and self.high is None

    def copy(self):
        return Interval(self.low, self.high)

    def __str__(self):
        return f"[{self.low}, {self.high}]"


class ConflictPair(object):
    def __init__(self, left=Interval(), right=Interval()):
        self.left = left
        self.right = right

    def swap(self):
        temp = self.left
        self.left = self.right
        self.right = temp

    def __str__(self):
        return f"({self.left}, {self.right})"


def top_of_stack(l: list):
    if not l:
        return None

    return l[-1]


class LRPlanarity(object):
    def __init__(self, G: nx.Graph):
        self.G = G
        self.roots = []
        # we treat None as infinity
        self.height = defaultdict(lambda: None)

        self.lowpt = {}
        self.lowpt2 = {}
        self.nesting_depth = {}
        self.oriented = []
        # None -> missing edge
        self.parent_edge = defaultdict(lambda: None)
        self.DG = nx.DiGraph()
        self.DG.add_nodes_from(G.nodes)

        self.ordered_adjs = {}

        self.ref = defaultdict(lambda: None)
        self.side = defaultdict(lambda: 1)
        self.S = []
        self.stack_bottom = {}
        self.lowpt_edge = {}

        self.left_ref = {}
        self.right_ref = {}

        self.embedding = defaultdict(lambda: [])

        # For the counterexample
        # The conflicting interval that represents a conflicting different-constraint
        self.non_mergeable_conflict = None
        self.non_mergeable_conflict_edge = None

    def lr_planarity(self):
        if self.G.order() > 2 and self.G.size() > 3*self.G.order() - 6:
            raise nx.NetworkXUnfeasible()

        # ordering
        for v in self.G:
            if self.height[v] is None:
                self.height[v] = 0
                self.roots.append(v)
                self.dfs1(v)

        #self.G = None # just unsetting this for correctness purposes

        # testing
        for v in self.DG:
            self.ordered_adjs[v] = sorted(self.DG[v], key=lambda w: self.nesting_depth[(v, w)])
        for v in self.roots:
            self.dfs2(v)

        def sign(e):
            if self.ref[e] is not None:
                self.side[e] = self.side[e] * sign(self.ref[e])
                self.ref[e] = None
            return self.side[e]

        for e in self.DG.edges:
            self.nesting_depth[e] = sign(e)*self.nesting_depth[e]
        for v in self.DG:
            self.ordered_adjs[v] = sorted(self.DG[v], key=lambda w: self.nesting_depth[(v, w)])

        for v in self.roots:
            self.dfs3(v)

        return dict(self.embedding)

    def dfs1(self, v):
        e = self.parent_edge[v]
        for w in self.G[v]:
            if (v, w) in self.DG.edges or (w, v) in self.DG.edges:
                continue
            vw = (v, w)
            self.DG.add_edge(v, w)

            self.lowpt[vw] = self.height[v]
            self.lowpt2[vw] = self.height[v]
            if self.height[w] is None:
                self.parent_edge[w] = vw
                self.height[w] = self.height[v] + 1
                self.dfs1(w)
            else:
                self.lowpt[vw] = self.height[w]

            # determine nesting graph
            self.nesting_depth[vw] = 2 * self.lowpt[vw]
            if self.lowpt2[vw] < self.height[v]:
                # chordal
                self.nesting_depth[vw] += 1

            # update lowpoints of parent edge e
            if e is not None:
                if self.lowpt[vw] < self.lowpt[e]:
                    self.lowpt2[e] = min(self.lowpt[e], self.lowpt2[vw])
                    self.lowpt[e] = self.lowpt[vw]
                elif self.lowpt[vw] > self.lowpt[e]:
                    self.lowpt2[e] = min(self.lowpt2[e], self.lowpt[vw])
                else:
                    self.lowpt2[e] = min(self.lowpt2[e], self.lowpt2[vw])

    def dfs2(self, v):
        def conflicting(I, b):
            return not I.empty() and self.lowpt[I.high] > self.lowpt[b]

        def lowest(P):
            if P.left.empty():
                return self.lowpt[P.right.low]
            if P.right.empty():
                return self.lowpt[P.left.low]
            return min(self.lowpt[P.left.low], self.lowpt[P.right.low])

        e = self.parent_edge[v]
        # note: this can be done in linear time, but will it be actually faster?
        for w in self.ordered_adjs[v]:
            ei = (v, w)
            self.stack_bottom[ei] = top_of_stack(self.S)
            if ei == self.parent_edge[w]:
                # tree edge
                self.dfs2(w)
            else:
                # back edge
                self.lowpt_edge[ei] = ei
                self.S.append(ConflictPair(right=Interval(ei, ei)))
            # integrate new return edges
            if self.lowpt[ei] < self.height[v]:
                # e_i has return edge
                if w == self.ordered_adjs[v][0]:
                    self.lowpt_edge[e] = self.lowpt_edge[ei]
                else:
                    # add constraints of e_i
                    P = ConflictPair()
                    # merge return edges of e_i into P.right
                    while True:
                        Q = self.S.pop()
                        if not Q.left.empty():
                            Q.swap()
                        if not Q.left.empty():
                            # Save the conflict to generate a counterexample
                            self.non_mergeable_conflict = Q
                            self.non_mergeable_conflict_edge = self.lowpt_edge[e]
                            raise nx.NetworkXUnfeasible()
                        if self.lowpt[Q.right.low] > self.lowpt[e]:
                            # merge intervals
                            if P.right.empty():
                                # topmost interval
                                P.right = Q.right.copy()
                            else:
                                self.ref[P.right.low] = Q.right.high
                            P.right.low = Q.right.low
                        else:
                            # align
                            self.ref[Q.right.low] = self.lowpt_edge[e]
                        if top_of_stack(self.S) == self.stack_bottom[ei]:
                            break
                    # merge conflicting return edges of e_1,...,e_i-1 into P.L
                    while conflicting(top_of_stack(self.S).left, ei) or conflicting(top_of_stack(self.S).right, ei):
                        Q = self.S.pop()
                        if conflicting(Q.right, ei):
                            Q.swap()
                        if conflicting(Q.right, ei):
                            # Save the conflict to generate a counterexample
                            self.non_mergeable_conflict = Q
                            self.non_mergeable_conflict_edge = self.lowpt_edge[ei]
                            raise nx.NetworkXUnfeasible()
                        # merge interval below lowpt(e_i) into P.R
                        self.ref[P.right.low] = Q.right.high
                        if Q.right.low is not None:
                            P.right.low = Q.right.low

                        if P.left.empty():
                            # topmost interval
                            P.left = Q.left.copy()
                        else:
                            self.ref[P.left.low] = Q.left.high
                        P.left.low = Q.left.low
                    if not (P.left.empty() and P.right.empty()):
                        self.S.append(P)
        # remove back edges returning to parent
        if e is not None:
            # v isn't root
            u = e[0]
            # trim back edges ending at parent u
            # drop entire conflict pairs
            while self.S and lowest(top_of_stack(self.S)) == self.height[u]:
                P = self.S.pop()
                if P.left.low is not None:
                    self.side[P.left.low] = -1
            if self.S:
                # one more conflict pair to consider
                P = self.S.pop()
                while P.left.high is not None and P.left.high[1] == u:
                    P.left.high = self.ref[P.left.high]
                if P.left.high is None and P.left.low is not None:
                    # just emptied
                    self.ref[P.left.low] = P.right.low
                    self.side[P.left.low] = -1
                    P.left.low = None
                # trim right interval
                while P.right.high is not None and P.right.high[1] == u:
                    P.right.high = self.ref[P.right.high]
                if P.right.high is None and P.right.low is not None:
                    # just emptied
                    self.ref[P.right.low] = P.left.low
                    self.side[P.right.low] = -1
                    P.right.low = None
                self.S.append(P)
            # side of e is side of a highest return edge
            if self.lowpt[e] < self.height[u]:
                # e has return edge
                hl = top_of_stack(self.S).left.high
                hr = top_of_stack(self.S).right.high

                if hl is not None and (hr is None or self.lowpt[hl] > self.lowpt[hr]):
                    self.ref[e] = hl
                else:
                    self.ref[e] = hr

    def dfs3(self, v):
        for w in self.ordered_adjs[v]:
            ei = (v, w)
            if ei == self.parent_edge[w]:
                # tree edge
                self.embedding[v].insert(0, w) # this deviates from the paper
                self.left_ref[v] = w
                self.right_ref[v] = w
                self.dfs3(w)
            else:
                # back edge
                if self.side[ei] == 1:
                    self.embedding[w].insert(self.embedding[w].index(self.right_ref[w]) + 1, v)
                else:

                    self.embedding[w].insert(self.embedding[w].index(self.left_ref[w]), v)
                    self.left_ref[w] = v

    def is_backedge(self, edge):
        return self.height[edge[0]] > self.height[edge[1]]

    def _get_cycle(self, back_edge):
        # Returns a set of edges of the fundamental cycle of back_edge
        edges = set()
        # Start with highest node
        edges.add(back_edge)
        current_edge = back_edge
        while True:  # Move down the tree until we reach back_edge agian
            current_edge = self.parent_edge[current_edge[0]]
            edges.add(current_edge)
            if current_edge[0] == back_edge[1]:
                break
        return edges


    def get_counterexample(self):
        # 1. Check if the graph violates euler formula
        if self.G.size() > 3*self.G.order() - 6:
            # No need for a counterexample
            print("Violates euler formula")
            return None

        # 2. Find contradicting fork
        # Contradicting backedges
        l_l = self.non_mergeable_conflict.left.low
        l_r = self.non_mergeable_conflict.right.low
        # Get the minimum height of the low points (later needed for the cycle of the same constraint)
        min_low_point = min(l_l[1], l_r[1])

        cycle_l_l = self._get_cycle(l_l)
        cycle_l_r = self._get_cycle(l_r)
        intersection_l_l_with_l_r = cycle_l_l.intersection(cycle_l_r)

        # Find forking edges e_l and e_r
        e_l = l_l
        while self.parent_edge[e_l[0]] not in intersection_l_l_with_l_r:
            e_l = self.parent_edge[e_l[0]]

        e_r = l_r
        while self.parent_edge[e_r[0]] not in intersection_l_l_with_l_r:
            e_r = self.parent_edge[e_r[0]]
        fork_edge = self.parent_edge[e_r[0]]

        print(f"Parents: {self.parent_edge}")
        print(f"Cycle l_l: {cycle_l_l} Cycle l_r: {cycle_l_r} intersection: {intersection_l_l_with_l_r }")
        print(f"e_l: {e_l} e_r: {e_r} fork: {self.parent_edge[e_r[0]]}")
        print(f"lowpt_edge(e_l): {self.lowpt_edge[e_l]} lowpt_edge(e_r): {self.lowpt_edge[e_r]}")
        print(f"Non mergeable conflict: {self.non_mergeable_conflict}, edge: {self.non_mergeable_conflict_edge}")


        # Get the return edge that induces a same constraint for the required conflict
        # For this we traverse our graph from the node blow the fork down to the root. On each level we check for outgoing nodes
        # We then traverse the tree up again not following the branch we came from
        # As soon as we have found an edge on one of these parts we have found a
        """
        previous_node = fork_edge[1]
        current_node = fork_edge[0]
        same_constraint_edge = None
        while current_node is not None:
            for neighbor in self.DG.neighbors(current_node):
                if neighbor != previous_node:
                    # Check height
                    current_edge = (current_node, neighbor)
                    lowpt = self.lowpt[current_edge]
                    if lowpt < min_low_point:
                        same_constraint_edge = self.lowpt_edge[current_edge]
                        break
            if same_constraint_edge is not None:
                break
            previous_node = current_node
            if self.parent_edge[current_node] is None:
                raise nx.NetworkXError("No same constraint found for a conflict.")
            current_node = self.parent_edge[current_node][0]
        """
        same_constraint_cycle = self._get_cycle(self.non_mergeable_conflict_edge)

        cycles = [cycle_l_l, cycle_l_r, same_constraint_cycle,
                  self._get_cycle(self.lowpt_edge[e_l]), self._get_cycle(self.lowpt_edge[e_r])]
        self.getDotGraph(cycles)

        # l_l and l_r are always part of counterexample
        subgraph_nodes = cycle_l_l.union(cycle_l_r)
        # A same-constraint is also needed in the counterexample
        subgraph_nodes.update(same_constraint_cycle)

        # 3. Check counterexample case
        if self.lowpt[l_l] != self.lowpt[l_r]:
            # Type 1
            print("Type 1: K_3_3")
            if self.lowpt[l_l] > self.lowpt[l_r]:
                additional_cycle = self.lowpt_edge[e_l]
            else:
                additional_cycle = self.lowpt_edge[e_r]
            # Add cycle to enforce different-constraint
            subgraph_nodes.update(self._get_cycle(additional_cycle))
        else:
            # Type 2 or Type 3
            if self.lowpt[e_l] == self.lowpt[e_r]:
                # Type 2
                print("Type 2: K_3_3")
                # Add cycles to enforce different-constraint
                subgraph_nodes.update(self._get_cycle(self.lowpt_edge[e_r]))
                subgraph_nodes.update(self._get_cycle(self.lowpt_edge[e_l]))
                # Remove overlapping parts of C(l_l) C(l_r) and the same-constraint cycle
                overlapping_part = intersection_l_l_with_l_r.intersection(same_constraint_cycle)
                subgraph_nodes.difference_update(overlapping_part)
            else:
                # Type 3
                print("Type 3: K_5")
                raise NotImplementedError

        return nx.Graph(list(subgraph_nodes))

    # Temporarily used to visualize the directed graph with interesting cycles
    def getDotGraph(self, cycles):
        """

        :param cycles:
            Dict that maps color of the cycle to a set of edges that the cycle consists of
        :return:
        """
        # Initialize graph
        import pydot
        graph = pydot.Dot(graph_type='digraph', rankdir='BT', dpi='300')
        graph.set_node_defaults(shape='circle')

        # Obtain nodes ordered by height
        nodes_by_height = {}
        for v in self.height:
            if self.height[v] in nodes_by_height:
                node_set = nodes_by_height[self.height[v]]
            else:
                node_set = set()
                nodes_by_height[self.height[v]] = node_set
            node_set.add(v)

        list_of_heights = list(nodes_by_height)
        list_of_heights.sort()

        # Add nodes to graph
        pydot_nodes = {}
        for height in list_of_heights:
            # Add all nodes of this height
            same_height_graph = pydot.Subgraph(rank='same')
            for v in nodes_by_height[height]:
                pydot_nodes[v] = pydot.Node(name=str(v))
                same_height_graph.add_node(pydot_nodes[v])
            graph.add_subgraph(same_height_graph)

        # Add edges
        for (u, v) in self.DG.edges:
            graph.add_edge(pydot.Edge(u, v))

        cycle_formats = [
            {'color': 'red', 'style': 'bold'},     # l_l
            {'color': 'blue', 'style': 'bold'},   # l_r
            {'color': 'black', 'style': 'bold'},     # same constraint
            {'color': 'red', 'style': 'dotted'},  # lowpt_edge e_l
            {'color': 'blue', 'style': 'dotted'},  # lowpt_edge e_r
        ]
        current_formats = ['color', 'style']

        # Add cycles
        for i, current_cycle in enumerate(cycles):
            for (u, v) in current_cycle:
                obj_dict = {}
                for f in current_formats:
                    obj_dict[f] = cycle_formats[i][f]
                #graph.add_edge(pydot.Edge(u, v, **obj_dict))

        # Save graph
        graph.write('directed_graph.dot')




# Just temporaritl copies from the test_lr_planarity
def find_minor(G, sub_graph):
    sub_graph = sub_graph.copy()
    # 1. Check that each edge is contained in G
    for edge in sub_graph.edges:
        if not G.has_edge(*edge):
            raise nx.NetworkXError("Not a subgraph.")

    # 2. Remove self loops
    for u in sub_graph:
        if sub_graph.has_edge(u, u):
            sub_graph.remove_edge(u, u)

    # Keep track of nodes we might need to contract
    contract = list(sub_graph)

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
    return sub_graph

if __name__ == '__main__':
    #k5 = nx.complete_graph(5)
    G = nx.fast_gnp_random_graph(6, 0.8)
    print(G.adj)
    from networkx.drawing.nx_agraph import write_dot
    write_dot(G, 'temp.dot')
    result = check_planarity(G)
    print(result)
    if not result[0]:
        write_dot(result[1], 'subgraph.dot')
        write_dot(find_minor(G, result[1]), 'subgraph_minor.dot')