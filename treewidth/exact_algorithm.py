import networkx as nx
import itertools
import sys


def exact_tree_width(G):
    # Initialize treewidth for empty subgraph
    tree_width = {frozenset(): -1}

    # V: nodes of original graph
    V = frozenset(G.nodes)

    # Start with subsets of size 1 up to V
    for i in range(1, G.number_of_nodes() + 1):

        for S in itertools.combinations(V, i):
            # S is a subset of V of size i
            S = frozenset(S)  # Convert to frozenset

            V_diff_S = V.difference(S)

            # Calculate tree width for subgraph of S with formula: TW(S) =  min_{v in V}  max{ TW(S-{v}), Q(S-{v},v) }
            min_tw = sys.maxsize

            for v in S:
                # tw1 = TW(S-{v})    (as in formula above)
                tw1 = tree_width[S.difference([v])]

                # tw2 = Q(S-{v},v)   (as in formula above)
                # Q(S,v) defined as in "On exact algorithms for treewidth" section 2.3 (page 4)
                tw2 = 0
                for w in V_diff_S.difference(v):
                    subgraph = G.subgraph(S.union([v, w]))
                    if nx.has_path(subgraph, v, w):
                        tw2 += 1

                # Calculate the maximum (as in formula above)
                max_tw = max(tw1, tw2)
                if max_tw < min_tw:
                    # Update the minimum over all v (as in formula above)
                    min_tw = max_tw

            # Assign the calculated treewidth for the subgraph of S
            tree_width[S] = min_tw

    return tree_width[V]


# Test on graph from page 2 of "Discovering Treewidth" (Hans L. Bodlaender)
G = nx.Graph()
G.add_edges_from([('a', 'b'), ('b', 'c'), ('b', 'd'),
                  ('c', 'e'), ('c', 'f'), ('d', 'f'),
                  ('d', 'g'), ('e', 'f'), ('f', 'g')])

print("Treewidth: ", exact_tree_width(G))
"""
Output: 

Treewidth:  2
"""
