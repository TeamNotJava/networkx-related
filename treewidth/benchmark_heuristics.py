#!/usr/bin/env python

import networkx as nx
import time
import math

from unoptimized_heuristic import tree_width_from_decomp,tree_decomp,min_degree_heuristic,minimum_fill_in_heuristic


# Test setup
TEST_P = [0.1, 0.01]
TEST_NODE_NUMS = [int(math.exp(0.1*i)) for i in range(1, 60)]
TEST_HEURISTICS = {
    'min_degree': min_degree_heuristic,
    'min_fill_in': minimum_fill_in_heuristic
}


def main():
    for p in TEST_P:
        for n in TEST_NODE_NUMS:
            # Generate a random graph G
            G = nx.fast_gnp_random_graph(n, p, directed=False)
            results = "p={:<4} n={:>4}".format(p,n)
            tree_decomp_list = []
            for heuristic in TEST_HEURISTICS:
                start_time = time.time()
                decomp = tree_decomp(G, TEST_HEURISTICS[heuristic])
                tree_width = tree_width_from_decomp(decomp)
                tree_decomp_list.append(tree_width)
                duration = time.time() - start_time
                results += "     {}: treewidth={:>4} time={:>8.5f}".format(heuristic,tree_width, duration)
            tree_diff = tree_decomp_list[0] - tree_decomp_list[1]
            if tree_diff != 0:
                if tree_diff > 0:
                    results += "\033[92m {} Lower tree decomp \033[0m".format(tree_diff)
                else:
                    results += "\033[91m {} Higher tree decomp \033[0m".format(-tree_diff)
            print(results)


if __name__ == '__main__':
    main()
