# -*- coding: utf-8 -*-
from framework.samplers.generic_samplers import *
from framework.decomposition_grammar import *
from framework.evaluation_oracle import Oracle
from framework.binary_tree_decomposition import binary_tree_grammar
from collections import deque

import argparse
import logging, sys

# some shortcuts to make the grammar more readable
class TestOracle(Oracle):
    # these values are for size 100
    evaluations = {
        'x0': 0.4999749994,
        'y0': 1.0,  # this is not needed here
        'Tree(x0,y0)': 0.99005
    }

    def get(self, query_string):
        # print(query_string)
        if query_string in self.evaluations:
            return self.evaluations[query_string]
        else:
            return 0.5


def other_test():
    # some shortcuts to make the grammar more readable
    Z = ZeroAtom()
    L = LAtom()
    U = UAtom()

    Tree = Alias('Tree')
    Bla = Alias('Bla')
    Blub = Alias('Blub')
    Blob = Alias('Blob')

    test_grammar = DecompositionGrammar()
    test_grammar.add_rules({

        # tree is either a leaf or inner node with two children which are trees
        'Tree': L + Tree * L * Blub,
        'Blub': USubs(Bla, Blob),
        'Blob': L + U + Z,
        'Bla': LSubs(Blub, Blob),


    })

    # inject the oracle into the samplers
    BoltzmannSampler.oracle = TestOracle()
    Alias.active_grammar = test_grammar

    print(test_grammar.recursive_rules)
    print()

    print(test_grammar.collect_oracle_queries('Bla', 'x', 'y'))

    #for key in test_grammar.get_rules():
        #print(test_grammar.collect_oracle_queries(key, 'x', 'y'))

    # sizes = [test_grammar.sample('Tree', 'x0', 'y0').get_l_size() for _ in range(1000)]
    # sum(sizes) / len(sizes)

def binary_tree_test():

    class BinaryTreeOracle(Oracle):
        def __init__(self):
            self.evaluations = {
                'x': 0.0149875,
                'y': 1.0,
                'R_b_as(x,y)': 1,
                'R_w_as(x,y)': 1,
                'R_w(x,y)': 0.9,
                'R_b(x,y)': 0.9,
                'R_b_head(x,y)': 0.000001,
                'R_w_head(x,y)': 0.9
            }



    BoltzmannSampler.oracle = BinaryTreeOracle()
    BoltzmannSampler.active_grammar = binary_tree_grammar
    tree = binary_tree_grammar.sample('K_dy', 'x', 'y')
    print(tree)
    tree.pretty()
    print("Black Nodes: {}".format(tree.get_attribute('numblacknodes')))
    print("White Nodes: {}".format(tree.get_attribute('numwhitenodes')))
    print("Total Nodes: {}".format(tree.get_attribute('numtotal')))

    return tree



def plot_binary_tree(tree):
    import networkx as nx
    import numpy as np
    import matplotlib.pyplot as plt

    stack = deque([tree])
    G=nx.empty_graph(tree._id+1)

    while stack:
        node = stack.pop()
        label_node = node._id
        G.nodes[label_node]['color'] = node.get_attribute('color')
        if node.left is not None:
            left = node.left
            stack.append(left)
            label_left = left._id
            G.add_edge(label_node, label_left)
        if node.right is not None:
            right = node.right
            stack.append(right)
            label_right = right._id
            G.add_edge(label_node, label_right)

    colors = []
    for x in nx.get_node_attributes(G, 'color').values():
        if x is 'black':
            colors.append('#222222')
        else:
            colors.append('#DDDDDD')


    nx.draw(G, node_color=colors)
    plt.show()

def main():
    argparser = argparse.ArgumentParser(description='Test stuff')
    argparser.add_argument('-d', dest='loglevel', action='store_const',const=logging.DEBUG, help='Print Debug info')
    argparser.add_argument('-b', '--binary-tree', action='store_true', help='Run the binary_tree_test function')
    argparser.add_argument('--plot', action='store_true', help='Plot the binary_tree_test function result')
    argparser.add_argument('--other', action='store_true', help='Run the other_test function')
    
    args = argparser.parse_args()

    logging.basicConfig(level=args.loglevel)

    if args.binary_tree:
        tree = binary_tree_test()
        if args.plot:
            plot_binary_tree(tree)

    if args.other:
        other_test()
    
    


if __name__ == '__main__':
    main()
