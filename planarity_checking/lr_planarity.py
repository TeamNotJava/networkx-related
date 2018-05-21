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


class ConflictPair(object):
    def __init__(self, left=Interval(), right=Interval()):
        self.left = left
        self.right = right

    def swap(self):
        temp = self.left
        self.left = self.right
        self.right = temp


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
        # The edge that induces a same_constraint that contradicts the dirrent-constraint above
        self.non_mergeable_same_constraint_edge = None

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
                            self.non_mergeable_same_constraint_edge = e
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
                            self.non_mergeable_same_constraint_edge = ei
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

    def _get_cycle_nodes(self, back_edge):
        # Returns a set of nodes in the fundamental cycle of back_edge
        nodes = set()
        # Start with highest node
        current_node = back_edge[0]
        nodes.add(current_node)
        while current_node != back_edge[1]:  # Move down the tree until low node of back_edge is found.
            current_node = self.parent_edge[current_node][0]
            nodes.add(current_node)
        return nodes

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

        cycle_l_l = self._get_cycle_nodes(l_l)
        cycle_l_r = self._get_cycle_nodes(l_r)
        intersection_l_l_with_l_r = cycle_l_l.intersection(cycle_l_r)

        # Find forking edges e_l and e_r
        e_l = l_l
        while e_l[0] not in intersection_l_l_with_l_r:
            e_l = self.parent_edge[e_l[0]]
        fork = e_l[0]
        e_r = l_r
        while e_r[0] != fork:
            e_r = self.parent_edge[e_r[0]]

        print(f"Parents: {self.parent_edge}")
        print(f"Cycle l_l: {cycle_l_l} Cycle l_r: {cycle_l_r} intersection: {intersection_l_l_with_l_r }")
        print(f"e_l: {e_l} e_r: {e_r} fork: {fork}")
        print(f"lowpt_edge(e_l): {self.lowpt_edge[e_l]} lowpt_edge(e_r): {self.lowpt_edge[e_r]}")
        print(f"Same constraint edge: {self.non_mergeable_same_constraint_edge} lowpt_edge(sce): {self.lowpt_edge[self.non_mergeable_same_constraint_edge]}")

        # TODO: Check that this is correct
        same_constraint_nodes = self._get_cycle_nodes(self.lowpt_edge[self.non_mergeable_same_constraint_edge])

        # l_l and l_r are always part of counterexample
        subgraph_nodes = cycle_l_l.union(cycle_l_r)
        # A same-constraint is also needed in the counterexample
        subgraph_nodes.update(same_constraint_nodes)

        # 3. Check counterexample case
        if self.lowpt[l_l] != self.lowpt[l_r]:
            # Type 1
            print("Type 1: K_3_3")
            if self.lowpt[l_l] > self.lowpt[l_r]:
                additional_cycle = self.lowpt_edge[e_l]
            else:
                additional_cycle = self.lowpt_edge[e_r]
            # Add cycle to enforce different-constraint
            subgraph_nodes.update(self._get_cycle_nodes(additional_cycle))
        else:
            # Type 2 or Type 3
            if self.lowpt[e_l] == self.lowpt[e_r]:
                # Type 2
                print("Type 2: K_3_3")
                # Add cycles to enforce different-constraint
                subgraph_nodes.update(self._get_cycle_nodes(self.lowpt_edge[e_r]))
                subgraph_nodes.update(self._get_cycle_nodes(self.lowpt_edge[e_l]))
                # Remove overlapping parts of C(l_l) C(l_r) and the same-constraint cycle
                current_node = fork
                while current_node not in same_constraint_nodes:
                    current_node = self.parent_edge[current_node][0]
                # Don't remove the first node
                current_node = self.parent_edge[current_node][0]
                # Remove all parent nodes until the join point of l_l and l_r is reached
                while current_node != l_l[1]:
                    subgraph_nodes.remove(current_node)
            else:
                # Type 3
                print("Type 3: K_5")
                raise NotImplementedError

        return subgraph_nodes


if __name__ == '__main__':
    #k5 = nx.complete_graph(5)
    G = nx.fast_gnp_random_graph(10, 0.4)
    print(G.adj)
    from networkx.drawing.nx_agraph import write_dot
    write_dot(G, 'temp.dot')
    result = check_planarity(G)
    print(result)
    write_dot(G.subgraph(result[1]), 'subgraph.dot')