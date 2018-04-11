#!/usr/bin/env python

import networkx as nx
import cProfile

from exact_algorithm import exact_tree_width
from unoptimized_heuristic import tree_width_from_decomp,tree_decomp,min_degree_heuristic

# Number of nodes on which to run the test
N = 12
# Edge creation probability
P = 0.3
TEST_EXACT = True
TEST_APPROXIMATE = True

"""
Hint to the rough dimensions of values N and P:
The tests from http://web.eecs.utk.edu/~cphillip/cs594_spring2015_projects/treewidth.pdf
only test up to random graphs with 20 nodes and 67 edges.
N=20 and P=0.3 lead approximately to such a graph.

"""

def main():
    # Generate a random graph G
    G = nx.fast_gnp_random_graph(N, P, directed=False)
    old_component = None
    # Connect all components
    for current_component in nx.connected_components(G):
        if old_component is not None:
            G.add_edge(next(iter(old_component)), next(iter(current_component)))
        old_component = current_component

    print("Generated graph: ")
    print("Number nodes: ", G.number_of_nodes())
    print("Number edges: ", G.number_of_edges())
    print("Graph6 Format: ")
    print(nx.to_graph6_bytes(G, header=False).decode('utf-8'))




    if TEST_APPROXIMATE:
        # Initialize Profiler
        pr = cProfile.Profile()
        # Calculate the upper bound to the treewidth
        decomp = pr.runcall(tree_decomp, G, min_degree_heuristic)
        tree_width = pr.runcall(tree_width_from_decomp, decomp)

        print("Approximate Treewidth: ", tree_width)

        # Print profiler statistics
        pr.print_stats(sort="cumtime")

    if TEST_EXACT:
        # Initialize Profiler
        pr = cProfile.Profile()
        # Calculate the exact treewidth
        tree_width = pr.runcall(exact_tree_width, G)

        print("Exact Treewidth: ", tree_width)

        # Print profiler statistics
        pr.print_stats(sort="cumtime")

if __name__ == '__main__':
    main()
