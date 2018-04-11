import networkx as nx
import sys

# Calculate min degree with respective node
def min_degree_node(g: nx.Graph) -> (object, int):
    min_degree = sys.maxsize
    min_node = None
    for (node, degree) in g.degree:
        if degree < min_degree:
            min_node = node
            min_degree = degree
    return min_node, min_degree

# Calculates the tree-width from a tree decomposition
def tree_width_from_decomp(g: nx.Graph) -> int:
    return max(len(bag) for bag in g.nodes) - 1


# Calculates tree width decomposition
def tree_decomp(g : nx.Graph) -> nx.Graph:
    (elim_node,min_deg) = min_degree_node(g)
    if min_deg == g.number_of_nodes() -1:
        # Fully connected: Decomposition is single node
        decomp = nx.Graph()
        decomp.add_node(frozenset(g.nodes))
        return decomp

    if g.degree(elim_node) == 0:
        # The graph has multiple components
        raise nx.NetworkXError

    # Create copy of graph and remove elim_node
    gp = g.copy()
    gp.remove_node(elim_node)

    # Connect all neighbours with each other
    neighbors = set(g.neighbors(elim_node))
    for n in neighbors:
        for m in neighbors:
            if (n != m):
                gp.add_edge(n,m)

    # Recursively compute tree width decomposition
    decomp = tree_decomp(gp)

    # Search old bag in decomposition
    old_bag = None
    for n in decomp.nodes:
        if neighbors <= n:
            old_bag = n
            break

    # Create new node for decomposition
    neighbors.add(elim_node)
    neighbors = frozenset(neighbors)

    # Add edge to decomposition (implicitly also adds the new node)
    decomp.add_edge(old_bag,neighbors)
    return decomp


# Test on graph from page 2 of http://citeseerx.ist.psu.edu/viewdoc/download;jsessionid=24EA9C89C95721F22241A61D21C4BB60?doi=10.1.1.61.3586&rep=rep1&type=pdf
G = nx.Graph()
G.add_edges_from([('a','b'),('b','c'),('b','d'),
                  ('c','e'),('c','f'),('d','f'),
                  ('d','g'),('e','f'),('f','g')])

decomp = tree_decomp(G)
for (left,right) in decomp.edges:
    print("".join(left),"".join(right))

print("Treewidth: ", tree_width_from_decomp(decomp))
"""
Output: 

fgd fcd
fcd fce
fcd bcd
bcd ab
Treewidth:  2
"""
