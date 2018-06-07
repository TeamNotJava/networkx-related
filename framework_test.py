# -*- coding: utf-8 -*-
import argparse
import logging
from collections import deque

from framework.bijections.closure import Closure
from framework.bijections.primal_map import PrimalMap
from framework.bijections.whitney_3map_to_3graph import WhitneyBijection
from framework.binary_tree_decomposition import binary_tree_grammar
from framework.decomposition_grammar import *
from framework.evaluation_oracle import EvaluationOracle
from framework.evaluations_planar_graph import planar_graph_evals


def other_test():
    # some shortcuts to make the grammar more readable
    Z = ZeroAtomSampler()
    L = LAtomSampler()
    U = UAtomSampler()

    Tree = AliasSampler('Tree')
    Bla = AliasSampler('Bla')
    Blub = AliasSampler('Blub')
    Blob = AliasSampler('Blob')

    test_grammar = DecompositionGrammar()
    test_grammar.add_rules({

        # tree is either a leaf or inner node with two children which are trees
        'Tree': L + Tree * L * Blub,
        'Blub': USubsSampler(Bla, Blob),
        'Blob': L + U + Z,
        'Bla': LSubsSampler(Blub, Blob),

    })
    test_grammar.init()

    other_test_oracle = EvaluationOracle({
        'x0': 0.4999749994,
        'y0': 1.0,  # this is not needed here
        'Tree(x0,y0)': 0.99005
    })

    # inject the oracle into the samplers
    BoltzmannSampler.oracle = other_test_oracle

    print(test_grammar.recursive_rules)
    print()

    print(test_grammar.collect_oracle_queries('Bla', 'x', 'y'))

    # for key in test_grammar.get_rules():
    # print(test_grammar.collect_oracle_queries(key, 'x', 'y'))

    # sizes = [test_grammar.sample('Tree', 'x0', 'y0').get_l_size() for _ in range(1000)]
    # sum(sizes) / len(sizes)


def binary_tree_test():
    binary_tree_test_oracle = EvaluationOracle({
        'x': 0.0127,
        'y': 1.0,
        # 'R_b_as(x,y)': 1,
        # 'R_w_as(x,y)': 1,
        'R_w(x,y)': 0.9,
        'R_b(x,y)': 0.9,
        # 'R_b_head(x,y)': 0.000001,
        # 'R_w_head(x,y)': 0.9
    })

    # BoltzmannSampler.oracle = binary_tree_test_oracle
    BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals)
    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'
    [print(query) for query in sorted(binary_tree_grammar.collect_oracle_queries('K', symbolic_x, symbolic_y))]
    tree = binary_tree_grammar.sample('K', symbolic_x, symbolic_y)
    print(tree)
    print("Black Nodes: {}".format(tree.get_attribute('numblacknodes')))
    print("White Nodes: {}".format(tree.get_attribute('numwhitenodes')))
    print("Total Nodes: {}".format(tree.get_attribute('numtotal')))

    # [print(query) for query in sorted(binary_tree_grammar.collect_oracle_queries('K_dx', 'x', 'y'))]
    # tree2 = binary_tree_grammar.sample('K_dx', 'x', 'y')
    # print(tree2)
    # print("Black Nodes: {}".format(tree2.get_base_class_object().get_attribute('numblacknodes')))
    # print("White Nodes: {}".format(tree2.get_base_class_object().get_attribute('numwhitenodes')))
    # print("Total Nodes: {}".format(tree2.get_base_class_object().get_attribute('numtotal')))

    return tree


def pretty_print_tree(tree):
    tree.pretty()


def plot_binary_tree(tree):
    import networkx as nx
    import matplotlib.pyplot as plt

    stack = deque([tree])
    G = nx.empty_graph(tree._id + 1)

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


def closure_test():
    c = Closure()
    init_half_edge = c.test_closure()
    return c, init_half_edge


def plot_closure(closure, init_half_edge):
    import networkx as nx
    import matplotlib.pyplot as plt

    G = closure.half_edges_to_graph(init_half_edge)
    nx.draw(G)
    plt.show()


def irreducible_dissection_test():
    from framework.irreducible_dissection_decomposition import irreducible_dissection_grammar

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'

    BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals)
    irreducible_dissection_grammar.init()

    dissection = irreducible_dissection_grammar.sample('J', symbolic_x, symbolic_y)
    print(dissection)
    return dissection

    # admissibe_dissection_dx = irreducible_dissection_grammar.sample('J_a_dx', symbolic_x, symbolic_y)
    # print(admissibe_dissection_dx)

def plot_dissection(dissection):
    import networkx as nx
    import matplotlib.pyplot as plt

    G = Closure().half_edges_to_graph(dissection)
    nx.draw(G)
    plt.show()

# Run the primal map test.
def primal_map_test():
    # Check the outputs with the comments next to print instruction
    PrimalMap().test_primal_map()


# Run the whitney bijection test.
def whiney_bijection_test():
    # Check the outputs with the comments next to print instruction
    WhitneyBijection().test_whitney_bijection()


def main():
    argparser = argparse.ArgumentParser(description='Test stuff')
    argparser.add_argument('-d', dest='loglevel', action='store_const', const=logging.DEBUG, help='Print Debug info')
    argparser.add_argument('-b', '--binary-tree', action='store_true', help='Run the binary_tree_test function')
    argparser.add_argument('--plot', action='store_true', help='Plot the binary_tree_test function result')
    argparser.add_argument('--print', action='store_true', help='print the binary_tree_test function result')
    argparser.add_argument('--other', action='store_true', help='Run the other_test function')
    argparser.add_argument('--closure', action='store_true', help='Run the closure_test function')
    argparser.add_argument('--irdi', action='store_true', help='Run the irreducible_dissection_test function')

    argparser.add_argument('--primal_map', action='store_true', help='Run the primal_map_test function')
    argparser.add_argument('--whitney_bijection', action='store_true', help='Run the whitney_bijection_test function')

    args = argparser.parse_args()

    logging.basicConfig(level=args.loglevel)

    if args.binary_tree:
        tree = binary_tree_test()
        if args.print:
            plot_binary_tree(tree)
        if args.plot:
            plot_binary_tree(tree)

    if args.other:
        other_test()

    if args.closure:
        (i, j) = closure_test()
        if args.plot:
            plot_closure(i, j)
    if args.irdi:
        dissection = irreducible_dissection_test()
        if args.plot:
            plot_dissection(dissection)

    if args.primal_map:
        primal_map_test()

    if args.whitney_bijection:
        whiney_bijection_test()


if __name__ == '__main__':
    main()
