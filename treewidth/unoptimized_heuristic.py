import networkx as nx
import sys


# Returns the node with minimum degree or None (if the abort condition is met)
def min_degree_heuristic(G):
    min_degree = sys.maxsize
    min_node = None
    for (node, degree) in G.degree:
        if degree < min_degree:
            if degree <= 1:
                # Return early
                return node
            min_node = node
            min_degree = degree

    if min_degree == G.number_of_nodes() - 1:
        # Fully connected: Abort condition
        return None
    else:
        return min_node


# Returns the node that needs to be removed next or None (if the abort condition is met)
def minimum_fill_in_heuristic(G):
    candidate_node = None
    # Still keep track of min_degree to abort earlier
    min_degree = sys.maxsize
    min_fill_in = sys.maxsize

    for (node, degree) in G.degree:
        min_degree = min(min_degree, degree)
        num_fill_in = 0
        # Convert to list in order to access by index
        neighbors = list(G.neighbors(node))
        for i in range(len(neighbors) - 1):
            for j in range(i + 1, len(neighbors)):
                if G.has_edge(neighbors[i], neighbors[j]):
                    num_fill_in += 1
        if num_fill_in < min_fill_in:
            min_fill_in = num_fill_in
            candidate_node = node

    if min_degree == G.number_of_nodes() - 1:
        # Fully connected: Abort condition
        return None
    else:
        return candidate_node


# Calculates the tree-width from a tree decomposition
def tree_width_from_decomp(G):
    return max(len(bag) for bag in G.nodes) - 1


# Calculates tree width decomposition
def tree_decomp(G, heuristic):
    elim_node = heuristic(G)
    if elim_node is None:
        # The abort condition is met. Put all nodes into one bag.
        decomp = nx.Graph()
        decomp.add_node(frozenset(G.nodes))
        return decomp

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
    decomp = tree_decomp(gp, heuristic)

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

    decomp = tree_decomp(G, min_degree_heuristic)
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
