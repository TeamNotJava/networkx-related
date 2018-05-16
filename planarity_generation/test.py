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
    print("Start test...")
    h1 = HalfEdge()
    h2 = HalfEdge()
    h3 = HalfEdge()
    h4 = HalfEdge()
    h5 = HalfEdge()
    h6 = HalfEdge()
    h7 = HalfEdge()
    h8 = HalfEdge()
    h9 = HalfEdge()
    h10 = HalfEdge()
    h11 = HalfEdge()
    h12 = HalfEdge()
    h13 = HalfEdge()
    h14 = HalfEdge()
    h15 = HalfEdge()

    h1.opposite = None
    h1.next = h2
    h1.prior = h3
    h1.color = 0
    h1.node_nr = 0
    h2.opposite = h4
    h2.next = h3
    h2.prior = h1
    h2.color = 0
    h2.node_nr = 0
    h3.opposite = h7
    h3.next = h1
    h3.prior = h2
    h3.node_nr = 0
    h3.color = 0
    h4.opposite = h2
    h4.next = h5
    h4.prior = h6
    h4.color = 1
    h4.node_nr = 1
    h5.opposite = h10
    h5.next = h6
    h5.prior = h4
    h5.color = 1
    h5.node_nr = 1
    h6.opposite = h13
    h6.next = h4
    h6.prior = h5
    h6.color = 1
    h6.node_nr = 1
    h7.opposite = h3
    h7.next = h8
    h7.prior = h9
    h7.color = 1
    h7.node_nr = 2
    h8.opposite = None
    h8.next = h9
    h8.prior = h7
    h8.color = 1
    h8.node_nr = 2
    h9.opposite = None
    h9.next = h7
    h9.prior = h8
    h9.color = 1
    h9.node_nr = 2
    h10.opposite = h5
    h10.next = h11
    h10.prior = h12
    h10.color = 0
    h10.node_nr = 3
    h11.opposite = None
    h11.next = h12
    h11.prior = h10
    h11.color = 0
    h11.node_nr = 3
    h12.opposite = None
    h12.next = h10
    h12.prior = h11
    h12.color = 0
    h12.node_nr = 3
    h13.opposite = h6
    h13.next = h14
    h13.prior = h15
    h13.color = 0
    h13.node_nr = 4
    h14.opposite = None
    h14.next = h15
    h14.prior = h13
    h14.color = 0
    h14.node_nr = 4
    h15.opposite = None
    h15.next = h13
    h15.prior = h14
    h15.color = 0
    h15.node_nr = 4


    tree = binary_tree.BinaryTreeSampler().binary_tree_sampler()
    c = Closure()
    c.btree_to_planar_map(tree)
    # G = c.half_edges_to_graph(h1)
    # nx.draw(G)
    # plt.show()

    # hexagon = [HalfEdge() for i in range(12)]
    # init_half_edge = c.construct_hexagon(hexagon, 0)

    # G = c.half_edges_to_graph(init_half_edge)
    # nx.draw(G)
    # plt.show()

    



if __name__ == "__main__":
    test()
