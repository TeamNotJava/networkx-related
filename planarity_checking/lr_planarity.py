from collections import defaultdict
from copy import deepcopy
import networkx as nx



def get_counterexample(G):
    """Return a kuratowski subgraph"""
    if check_planarity(G)[0]:
        raise nx.NetworkXException("G is planar - no counter example.")
    
    subgraph = nx.Graph()
    for u in G:
        nbrs = list(G[u])
        for v in nbrs:
            G.remove_edge(u, v)
            if check_planarity(G)[0]:
                G.add_edge(u, v)
                subgraph.add_edge(u, v)

    return subgraph


def check_planarity(G, counterexample=False):
    """Checks if a graph is planar and returns a counter example or an embedding

     A graph is said to be planar, if it can be drawn in the plane without
     any edge intersections.

    Parameters
    ----------
    G : graph
        A NetworkX graph
    TODO counterexample

    Returns
    -------
    is_planar : bool
        Is true if the graph is planar

    result : TODO
        If the graph is planar this is a planar embedding
        If the graph is not planar this is a counter example

    Notes
    -----
    A (combinatorial) embedding consists of cyclic orderings of the incident edges at each vertex, given such
    an embedding there are multiple approaches discussed in literature to drawing the graph (subject to various constraints, e.g.
    integer coordinates), see e.g. [2].
    TODO time complexity

    TODO
    References
    ----------
    .. [1] Ulrik Brandes:
        The Left-Right Planarity Test
        2009
        http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.217.9208
    .. [2] Takao Nishizeki, Md Saidur Rahman:
        Planar graph drawing
        Lecture Notes Series on Computing: Volume 12
        2004
    """

    planarity = LRPlanarity(G)
    try:
        embedding = planarity.lr_planarity()
    except nx.NetworkXUnfeasible:
        if counterexample:
            return False, get_counterexample(G)
        return False, None
    return True, embedding


class Interval(object):
    def __init__(self, low=None, high=None):
        self.low = low
        self.high = high
    def empty(self):
        return self.low is None and self.high is None
    def copy(self):
        return Interval(self.low, self.high)

    # Return True if interval I conflicts with edge b
    def conflicting(self, b, planarityState):
        return not self.empty() and planarityState.lowpt[self.high] > planarityState.lowpt[b]


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
        self.G = nx.Graph()
        self.G.add_nodes_from(G.nodes)
        for v, w in G.edges:
            if v != w:
                self.G.add_edge(v, w)

        self.roots = []

        # distance from tree root
        self.height = defaultdict(lambda: None)

        self.lowpt = {} # height of lowest return point of an edge
        self.lowpt2 = {} # height of second lowest return point
        self.nesting_depth = {} # for nesting order
        
        #self.oriented = [] # TODO: is unused?
        
        # None -> missing edge
        self.parent_edge = defaultdict(lambda: None)

        # oriented DFS graph
        self.DG = nx.DiGraph()
        self.DG.add_nodes_from(G.nodes)

        self.ordered_adjs = {}

        self.ref = defaultdict(lambda: None)
        self.side = defaultdict(lambda: 1)

        # stack of conflict pairs
        self.S = []
        self.stack_bottom = {}
        self.lowpt_edge = {}

        self.left_ref = {}
        self.right_ref = {}

        self.embedding = defaultdict(lambda: [])

    def lr_planarity(self):
        if self.G.order() > 2 and self.G.size() > 3 * self.G.order() - 6:
            raise nx.NetworkXUnfeasible()

        # orientation of the graph by depth first search traversal
        for v in self.G:
            if self.height[v] is None:
                self.height[v] = 0
                self.roots.append(v)
                self.dfs_orientation(v)

        self.G = None # just unsetting this for correctness purposes

        # testing
        for v in self.DG: # sort the adjacency lists by nesting depth
            # note: this can be done in linear time, but will it be actually faster?
            self.ordered_adjs[v] = sorted(self.DG[v], key=lambda w: self.nesting_depth[(v, w)])
        for v in self.roots:
            self.dfs_testing(v)

        # function to resolve the relative side of an edge to the absolute side 
        def sign(e):
            if self.ref[e] is not None:
                self.side[e] = self.side[e] * sign(self.ref[e])
                self.ref[e] = None
            return self.side[e]

        for e in self.DG.edges:
            self.nesting_depth[e] = sign(e) * self.nesting_depth[e]
        for v in self.DG:
            # sort the adjacency lists again
            self.ordered_adjs[v] = sorted(self.DG[v], key=lambda w: self.nesting_depth[(v, w)])
            # initialize the embedding
            self.embedding[v] = self.ordered_adjs[v].copy()

        # compute the complete embedding
        for v in self.roots:
            self.dfs_embedding(v)

        return dict(self.embedding)

    # Orient the graph by DFS-traversal, compute lowpoints and nesting order
    def dfs_orientation(self, v):
        e = self.parent_edge[v]
        for w in self.G[v]:
            if (v, w) in self.DG.edges or (w, v) in self.DG.edges:
                continue # the edge was already oriented
            vw = (v, w)
            self.DG.add_edge(v, w) # orient the edge

            self.lowpt[vw] = self.height[v]
            self.lowpt2[vw] = self.height[v]
            if self.height[w] is None: # (v, w) is a tree edge
                self.parent_edge[w] = vw
                self.height[w] = self.height[v] + 1
                self.dfs_orientation(w)
            else: # (v, w) is a back edge
                self.lowpt[vw] = self.height[w]

             # determine nesting graph
            self.nesting_depth[vw] = 2 * self.lowpt[vw]
            if self.lowpt2[vw] < self.height[v]: # chordal
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

    def add_constraint(self, ei, e):
        P = ConflictPair()
        # merge return edges of e_i into P.right
        while True:
            Q = self.S.pop()
            if not Q.left.empty():
                Q.swap()
            if not Q.left.empty():  # not planar
                raise nx.NetworkXUnfeasible()
            if self.lowpt[Q.right.low] > self.lowpt[e]:
                # merge intervals
                if P.right.empty():  # topmost interval
                    P.right = Q.right.copy()
                else:
                    self.ref[P.right.low] = Q.right.high
                P.right.low = Q.right.low
            else:  # align
                self.ref[Q.right.low] = self.lowpt_edge[e]
            if top_of_stack(self.S) == self.stack_bottom[ei]:
                break
        # merge conflicting return edges of e_1,...,e_i-1 into P.L
        while top_of_stack(self.S).left.conflicting(ei, self) or top_of_stack(self.S).right.conflicting(ei, self):
            Q = self.S.pop()
            if Q.right.conflicting(ei, self):
                Q.swap()
            if Q.right.conflicting(ei, self):  # not planar
                raise nx.NetworkXUnfeasible()
            # merge interval below lowpt(e_i) into P.R
            self.ref[P.right.low] = Q.right.high
            if Q.right.low is not None:
                P.right.low = Q.right.low

            if P.left.empty():  # topmost interval
                P.left = Q.left.copy()
            else:
                self.ref[P.left.low] = Q.left.high
            P.left.low = Q.left.low

        if not (P.left.empty() and P.right.empty()):
            self.S.append(P)

    # Test for LR partition
    # Raise nx.NetworkXUnfeasible() in case of unresolvable conflict
    def dfs_testing(self, v):

        # Return the lowest lowpoint of a conflict pair
        def lowest(P):
            if P.left.empty():
                return self.lowpt[P.right.low]
            if P.right.empty():
                return self.lowpt[P.left.low]
            return min(self.lowpt[P.left.low], self.lowpt[P.right.low])

        e = self.parent_edge[v]
        for w in self.ordered_adjs[v]:
            ei = (v, w)
            self.stack_bottom[ei] = top_of_stack(self.S)
            if ei == self.parent_edge[w]: # tree edge
                self.dfs_testing(w)
            else: # back edge
                self.lowpt_edge[ei] = ei
                self.S.append(ConflictPair(right=Interval(ei, ei)))

            # integrate new return edges
            if self.lowpt[ei] < self.height[v]:
                if w == self.ordered_adjs[v][0]: # e_i has return edge
                    self.lowpt_edge[e] = self.lowpt_edge[ei]
                else: # add constraints of e_i
                    #TODO
                    self.add_constraints(ei)

        
        # remove back edges returning to parent
        if e is not None: # v isn't root
            u = e[0]
            # trim back edges ending at parent u
            # drop entire conflict pairs
            while self.S and lowest(top_of_stack(self.S)) == self.height[u]:
                P = self.S.pop()
                if P.left.low is not None:
                    self.side[P.left.low] = -1

            if self.S: # one more conflict pair to consider
                P = self.S.pop()
                # trim left interval
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
            if self.lowpt[e] < self.height[u]: # e has return edge
                hl = top_of_stack(self.S).left.high
                hr = top_of_stack(self.S).right.high

                if hl is not None and (hr is None or self.lowpt[hl] > self.lowpt[hr]):
                    self.ref[e] = hl
                else:
                    self.ref[e] = hr

    # Complete the embedding
    def dfs_embedding(self, v):
        for w in self.ordered_adjs[v]:
            ei = (v, w)
            if ei == self.parent_edge[w]: # tree edge
                # make v the first node in embedding list of w
                self.embedding[w].insert(0, v)
                self.left_ref[v] = w
                self.right_ref[v] = w
                self.dfs_embedding(w)
            else: # back edge
                if self.side[ei] == 1:
                    # place v directly after right_ref[w] in embedding list of w
                    self.embedding[w].insert(self.embedding[w].index(self.right_ref[w]) + 1, v)
                else:
                    # place v directly before left_ref[w] in embedding list of w
                    self.embedding[w].insert(self.embedding[w].index(self.left_ref[w]), v)
                    self.left_ref[w] = v