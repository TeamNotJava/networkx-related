from collections import defaultdict
import networkx as nx


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

    def lr_planarity(self):
        if self.G.order() > 2 and self.G.size() > 3*self.G.order() - 6:
            raise nx.NetworkXUnfeasible()

        # ordering
        for v in self.G:
            if self.height[v] is None:
                self.height[v] = 0
                self.roots.append(v)
                self.dfs1(v)

        self.G = None # just unsetting this for correctness purposes

        # testing
        for v in self.DG:
            self.ordered_adjs[v] = sorted(self.DG[v], key=lambda w: self.nesting_depth[(v, w)])
        for v in self.roots:
            self.dfs2(v)

        # this is irrelevant for checking the planar embedding
        # embedding
        # def sign(e):
        #    if self.ref[e] is not None:
        #        self.side[e] = self.side[e] * sign(self.ref[e])
        #        self.ref[e] = None
        #    return self.side[e]

        # for e in self.DG.edges:
        #    self.nesting_depth[e] = sign(e)*self.nesting_depth[e]
        # for v in self.DG:
        #     self.ordered_adjs[v] = sorted(self.DG[v], key=lambda w: self.nesting_depth[(v, w)])
        # for v in self.roots:
        #    self.dfs3(v)


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

#    def dfs3(self, v):
#        for w in self.ordered_adjs[v]:
#            ei = (v, w)
#            if ei == self.parent_edge[w]:
#                # tree edge
#                #TODO: make ei first element in adj list of w
#
#                self.left_ref[v] = ei
#                self.right_ref[v] = ei
#                dfs3(w)
#            else:
#                # back edge
#                if self.side[ei] == 1:
#                    #TODO: place ei after right_ref[w] in adj list of w
#                else:
#                    #TODO: place ei beforre left_ref[w] in adj list of w
#                    self.left_ref[w] = ei
