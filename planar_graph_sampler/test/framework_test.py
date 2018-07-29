# -*- coding: utf-8 -*-
#    Copyright (C) 2018 by
#    Marta Grobelna <marta.grobelna@rwth-aachen.de>
#    Petre Petrov <petrepp4@gmail.com>
#    Rudi Floren <rudi.floren@gmail.com>
#    Tobias Winkler <tobias.winkler1@rwth-aachen.de>
#    All rights reserved.
#    BSD license.
#
# Authors:  Marta Grobelna <marta.grobelna@rwth-aachen.de>
#           Petre Petrov <petrepp4@gmail.com>
#           Rudi Floren <rudi.floren@gmail.com>
#           Tobias Winkler <tobias.winkler1@rwth-aachen.de>

import argparse
import logging
from collections import deque

from framework.generic_samplers import *
from framework.decomposition_grammar import AliasSampler, DecompositionGrammar
from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import BoltzmannSamplerBase

from planar_graph_sampler.bijections.closure import Closure
from planar_graph_sampler.bijections.primal_map import PrimalMap
from planar_graph_sampler.bijections.whitney_3map_to_3graph import WhitneyBijection
from planar_graph_sampler.grammar.binary_tree_decomposition import binary_tree_grammar
from planar_graph_sampler.grammar.two_connected_decomposition import two_connected_graph_grammar
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100


def other_oldtest():
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
    BoltzmannSamplerBase.oracle = other_test_oracle

    print(test_grammar.recursive_rules)
    print()

    print(test_grammar.collect_oracle_queries('Bla', 'x', 'y'))

    # for key in test_grammar.get_rules():
    # print(test_grammar.collect_oracle_queries(key, 'x', 'y'))

    # sizes = [test_grammar.sample('Tree', 'x0', 'y0').l_size() for _ in range(1000)]
    # sum(sizes) / len(sizes)


def binary_tree_oldtest():
    binary_tree_test_oracle = EvaluationOracle({
        'x': 0.0475080992953792,
        'y': 1.0,
        # 'R_b_as(x,y)': 1,
        # 'R_w_as(x,y)': 1,
        'R_w(x,y)': 1,
        'R_b(x,y)': 1,
        # 'R_b_head(x,y)': 0.000001,
        # 'R_w_head(x,y)': 0.9
    })

    # BoltzmannSampler.oracle = binary_tree_test_oracle
    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    grammar = binary_tree_grammar()
    grammar.init()

    # symbolic_x = 'x'
    symbolic_x = 'x*G_1_dx(x,y)'
    # symbolic_y = 'y'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'

    print("Needed oracle entries:")
    [print(query) for query in sorted(grammar.collect_oracle_queries('K_dy', symbolic_x, symbolic_y))]
    tree = grammar.sample('R_b', symbolic_x, symbolic_y)

    print("Black nodes: {}".format(tree.black_nodes_count))
    print("White nodes: {}".format(tree.white_nodes_count))
    print("Total nodes: {}".format(tree.black_nodes_count + tree.white_nodes_count))
    print("Total leaves: {}".format(tree.leaves_count))

    return tree


def pretty_print_tree(tree):
    tree.pretty()


def plot_binary_tree(tree):
    import networkx as nx

    stack = deque([tree])
    G = nx.empty_graph()
    root = tree._id
    while stack:
        node = stack.pop()
        label_node = node._id

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
        G.nodes[label_node]['color'] = node.get_attribute('color')

    colors = []
    for x in nx.get_node_attributes(G, 'color').values():
        if x is 'black':
            colors.append('#333333')
        elif x is 'white':
            colors.append('#999999')
    sizes = []
    for x in G:
        if x is root:
            sizes.append(900)
        else:
            sizes.append(300)

    nx.draw(G, node_color=colors, node_size=sizes, with_labels=True)


def binary_tree_oldtest_V2():
    binary_tree_test_oracle = EvaluationOracle({
        'x': 0.0475080992953792,
        'y': 1.0,
        # 'R_b_as(x,y)': 1,
        # 'R_w_as(x,y)': 1,
        'R_w(x,y)': 1,
        'R_b(x,y)': 1,
        # 'R_b_head(x,y)': 0.000001,
        # 'R_w_head(x,y)': 0.9
    })

    BoltzmannSamplerBase.oracle = binary_tree_test_oracle
    # BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)
    grammar = binary_tree_grammar()
    grammar.init()
    symbolic_x = 'x'
    symbolic_y = 'y'
    # [print(query) for query in sorted(binary_tree_grammar.collect_oracle_queries('K_dy', symbolic_x, symbolic_y))]
    tree = grammar.sample('K_dy', symbolic_x, symbolic_y)
    # print(tree)
    print(tree.base_class_object().get_attribute('numblacknodes'), end="\t")
    print(tree.base_class_object().get_attribute('numwhitenodes'), end="\t")
    print(tree.base_class_object().get_attribute('numtotal'), end="\t")
    return tree.base_class_object()


def closure_oldtest():
    c = Closure()
    tree = binary_tree_test()
    # Do a deep copy of the tree as we want to plot it later in its original state.
    import copy
    init_half_edge = c.closure(copy.deepcopy(tree))
    c.test_partial_closure(init_half_edge)
    c.test_connections_between_half_edges(init_half_edge)
    c.test_planarity_of_embedding(init_half_edge)
    return c, tree, init_half_edge


def plot_closure(closure, tree, init_half_edge, graphviz=False):
    import networkx as nx

    G = init_half_edge.to_networkx_graph()
    colors = []
    for x in nx.get_node_attributes(G, 'color').values():
        if x is 'black':
            colors.append('#333333')
        elif x is 'white':
            colors.append('#999999')
        else:
            assert False
    if graphviz:
        # nx.nx_agraph.write_dot(G, "C:\\Users\\Valkum\\py.dot")
        nx.draw(G, nx.nx_agraph.graphviz_layout(G, prog='neato', args='-Gstart=self -Gepsilon=.0000001'),
                with_labels=True, node_color=colors)
    else:
        nx.draw(G, with_labels=True, node_color=colors)


def save_closure(closure, tree, init_half_edge, path):
    import networkx as nx
    G = init_half_edge.to_networkx_graph()
    # nx.nx_agraph.write_dot(G, path)
    nx.readwrite.gexf.write_gexf(G, path)


def irreducible_dissection_oldtest():
    from planar_graph_sampler.grammar.irreducible_dissection_decomposition import irreducible_dissection_grammar

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'

    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    grammar = irreducible_dissection_grammar()
    grammar.init()

    dissection = grammar.sample('J', symbolic_x, symbolic_y)
    print(dissection)
    return dissection

    # admissibe_dissection_dx = irreducible_dissection_grammar.sample('J_a_dx', symbolic_x, symbolic_y)
    # print(admissibe_dissection_dx)


def one_connected_oldtest():
    from planar_graph_sampler.grammar.two_connected_decomposition import two_connected_graph_grammar
    from planar_graph_sampler.bijections.block_decomposition import BlockDecomposition

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'y'

    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    grammar = two_connected_graph_grammar()
    grammar.init()

    # Create list of L-der two connected graphs
    list_l_der_two_connected = []
    for i in range(2):
        two_connected = grammar.sample('G_2_dx', symbolic_x, symbolic_y)
        list_l_der_two_connected.append(two_connected)

    decomp_worker = BlockDecomposition()
    decomp_worker.merge_set_of_l_der_two_connected_graphs(list_l_der_two_connected)


def plot_dissection(dissection):
    import networkx as nx
    import matplotlib.pyplot as plt

    G = dissection.to_networkx_graph()
    nx.draw(G)
    plt.show()


# Run the primal map test.
def primal_map_oldtest():
    # Check the outputs with the comments next to print instruction
    PrimalMap().test_primal_map()


# Run the whitney bijection test.
def whiney_bijection_oldtest():
    # Check the outputs with the comments next to print instruction
    WhitneyBijection().test_whitney_bijection()


def network_oldtest():
    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    grammar = two_connected_graph_grammar()
    grammar.init()

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'y'

    [print(query) for query in sorted(grammar.collect_oracle_queries('D', symbolic_x, symbolic_y))]
    network = grammar.sample('D', symbolic_x, symbolic_y)

    print(network.vertices_list)
    print(network.edges_list)
    print(network.root_half_edge)
    return network


def network_plot(network):
    import networkx as nx
    import matplotlib.pyplot as plt

    G = network.root_half_edge.to_networkx_graph()
    nx.draw(G, with_labels=True)
    plt.show()


def main():
    argparser = argparse.ArgumentParser(description='Test stuff')
    argparser.add_argument('-_d', dest='loglevel', action='store_const', const=logging.DEBUG, help='Print Debug info')
    argparser.add_argument('-b', '--binary-tree', action='store_true', help='Run the binary_tree_test function')
    argparser.add_argument('--plot', action='store_true', help='Plot the binary_tree_test function result')
    argparser.add_argument('--print', action='store_true', help='print the binary_tree_test function result')
    argparser.add_argument('--gephi', action='store', help='save as gephi file to path')
    argparser.add_argument('--other', action='store_true', help='Run the other_test function')
    argparser.add_argument('--closure', action='store_true', help='Run the closure_test function')
    argparser.add_argument('--irdi', action='store_true', help='Run the irreducible_dissection_test function')
    argparser.add_argument('--graphviz', action='store_true', help='Use Graphviz layout')
    argparser.add_argument('--one_connected', action='store_true', help='Run the one_connected_test_function')

    argparser.add_argument('--primal_map', action='store_true', help='Run the primal_map_test function')
    argparser.add_argument('--whitney_bijection', action='store_true', help='Run the whitney_bijection_test function')
    argparser.add_argument('--network', action='store_true', help='Run the network_test function')

    args = argparser.parse_args()

    logging.basicConfig(level=args.loglevel)

    if args.binary_tree:
        tree = binary_tree_test()
        if args.print:
            pretty_print_tree(tree)
        if args.plot:
            import matplotlib.pyplot as plt
            tree.plot()
            plt.show()

    if args.other:
        other_test()

    if args.closure:
        (i, tree, j) = closure_test()
        if args.plot:
            if args.gephi is not None:
                save_closure(i, tree, j, args.gephi)
            import matplotlib.pyplot as plt
            plt.figure(1)
            tree.plot()
            plt.figure(2)
            plot_closure(i, tree, j, graphviz=args.graphviz)
            plt.show()

    if args.irdi:
        dissection = irreducible_dissection_test()
        if args.plot:
            import matplotlib.pyplot as plt
            plot_dissection(dissection)
            plt.show()

    if args.primal_map:
        primal_map_test()

    if args.whitney_bijection:
        whiney_bijection_test()

    if args.one_connected:
        one_connected_test()

    if args.network:
        network = network_test()
        if args.plot:
            network_plot(network)


if __name__ == '__main__':
    main()
