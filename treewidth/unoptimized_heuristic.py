import networkx as nx
import sys


# Calculate min degree with respective node
def min_degree_node(G):
    min_degree = sys.maxsize
    min_node = None
    for (node, degree) in G.degree:
        if degree < min_degree:
            min_node = node
            min_degree = degree
    return min_node, min_degree


# Calculates the tree-width from a tree decomposition
def tree_width_from_decomp(g):
    return max(len(bag) for bag in g.nodes) - 1


# Calculates tree width decomposition
def tree_decomp(G):
    (elim_node, min_deg) = min_degree_node(G)
    if min_deg == G.number_of_nodes() - 1:
        # Fully connected: Decomposition is single node
        decomp = nx.Graph()
        decomp.add_node(frozenset(G.nodes))
        return decomp

    if G.degree(elim_node) == 0:
        # The graph has multiple components
        raise nx.NetworkXError("Input graph has multiple components.")

    # Create copy of graph and remove elim_node
    gp = G.copy()
    gp.remove_node(elim_node)

    # Connect all neighbours with each other
    neighbors = set(G.neighbors(elim_node))
    for n in neighbors:
        for m in neighbors:
            if (n != m):
                gp.add_edge(n, m)

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
    decomp.add_edge(old_bag, neighbors)
    return decomp

if __name__ == '__main__':
    # Test on graph from page 2 of "Discovering Treewidth" (Hans L. Bodlaender)
    G = nx.Graph()
    G.add_edges_from([('a', 'b'), ('b', 'c'), ('b', 'd'),
                      ('c', 'e'), ('c', 'f'), ('d', 'f'),
                      ('d', 'g'), ('e', 'f'), ('f', 'g')])

    decomp = tree_decomp(G)
    for (left, right) in decomp.edges:
        print("".join(left), "".join(right))

    print("Treewidth: ", tree_width_from_decomp(decomp))
    """
    Output: 
    
    fgd fcd
    fcd fce
    fcd bcd
    bcd ab
    Treewidth:  2
    """
