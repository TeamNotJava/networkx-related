from boltzman_sampler import *
from boltzman_sampler.halfedge import HalfEdge
from boltzman_sampler.closure import Closure


import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

def plot_binary_tree():
    # print(binary_tree.binary_tree_sampler(10))
    tree = binary_tree.BinaryTreeSampler().binary_tree(10)
    colors = []
    for x in nx.get_node_attributes(tree, 'color').values():
        if x is 'black':
            colors.append('#222222')
        else:
            colors.append('#DDDDDD')


    nx.draw(tree, node_color=colors)
    plt.show()

def test():
    tree = binary_tree.BinaryTreeSampler().binary_tree_sampler()
    c = Closure()

    init_half_edge = c.test_closure()
    # G = c.half_edges_to_graph(init_half_edge)
    # nx.draw(G)
    # plt.show()


if __name__ == "__main__":
    test()
