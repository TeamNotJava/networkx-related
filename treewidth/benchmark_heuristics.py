#!/usr/bin/env python

import networkx as nx
import time
import math

from unoptimized_heuristic import tree_width_from_decomp,tree_decomp,min_degree_heuristic,minimum_fill_in_heuristic

# Test setup
TEST_P = [0.1, 0.01]
TEST_NODE_NUMS = [ int(math.exp(0.1*i)) for i in range(1,50) ]
TEST_HEURISTICS = {
    'min_degree': min_degree_heuristic,
    'min_fill_in': minimum_fill_in_heuristic
}


def main():
    for p in TEST_P:
        for n in TEST_NODE_NUMS:
            # Generate a random graph G
            G = nx.fast_gnp_random_graph(n, p, directed=False)
            results = ""
            for heuristic in TEST_HEURISTICS:
                start_time = time.time()
                decomp = tree_decomp(G, TEST_HEURISTICS[heuristic])
                tree_width = tree_width_from_decomp(decomp)
                duration = time.time() - start_time
                results += "\t{}:\ttreewidth={}\ttime={:0.4f}".format(heuristic,tree_width, duration)
            print("p={}\tn={}".format(p,n) + results)


if __name__ == '__main__':
    main()
