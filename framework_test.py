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
from framework.evaluations_planar_graph import planar_graph_evals_n100


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
        'x': 0.0475080992953792,
        'y': 1.0,
        # 'R_b_as(x,y)': 1,
        # 'R_w_as(x,y)': 1,
        'R_w(x,y)': 1,
        'R_b(x,y)': 1,
        # 'R_b_head(x,y)': 0.000001,
        # 'R_w_head(x,y)': 0.9
    })

    BoltzmannSampler.oracle = binary_tree_test_oracle
    # BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)
    symbolic_x = 'x'
    symbolic_y = 'y'
    [print(query) for query in sorted(binary_tree_grammar.collect_oracle_queries('K_dy', symbolic_x, symbolic_y))]
    tree = binary_tree_grammar.sample('K_dy', symbolic_x, symbolic_y)
    print(tree)
    print("Black Nodes: {}".format(tree.get_base_class_object().get_attribute('numblacknodes')))
    print("White Nodes: {}".format(tree.get_base_class_object().get_attribute('numwhitenodes')))
    print("Total Nodes: {}".format(tree.get_base_class_object().get_attribute('numtotal')))

    # [print(query) for query in sorted(binary_tree_grammar.collect_oracle_queries('K_dx', 'x', 'y'))]
    # tree2 = binary_tree_grammar.sample('K_dx', 'x', 'y')
    # print(tree2)
    # print("Black Nodes: {}".format(tree2.get_base_class_object().get_attribute('numblacknodes')))
    # print("White Nodes: {}".format(tree2.get_base_class_object().get_attribute('numwhitenodes')))
    # print("Total Nodes: {}".format(tree2.get_base_class_object().get_attribute('numtotal')))

    return tree.get_base_class_object()


def pretty_print_tree(tree):
    tree.pretty()


def plot_binary_tree(tree):
    import networkx as nx
    import matplotlib.pyplot as plt

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
    


def binary_tree_test_V2():
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

    BoltzmannSampler.oracle = binary_tree_test_oracle
    # BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)
    symbolic_x = 'x'
    symbolic_y = 'y'
   # [print(query) for query in sorted(binary_tree_grammar.collect_oracle_queries('K_dy', symbolic_x, symbolic_y))]
    tree = binary_tree_grammar.sample('K_dy', symbolic_x, symbolic_y)
   # print(tree)
    print(tree.get_base_class_object().get_attribute('numblacknodes'),end="\t")
    print(tree.get_base_class_object().get_attribute('numwhitenodes'),end="\t")
    print(tree.get_base_class_object().get_attribute('numtotal'),end="\t")
    return tree.get_base_class_object()

def closure_test():
    c = Closure()
    tree = binary_tree_test_V2()
    init_half_edge = c.closure(tree)
    return c, tree, init_half_edge


def plot_closure(closure, tree, init_half_edge, graphviz=False):
    import networkx as nx
    import matplotlib.pyplot as plt
    
    G = init_half_edge.to_networkx_graph()
    colors = []
    for x in nx.get_node_attributes(G, 'color').values():
        if x is 'black':
            colors.append('#333333')
        elif x is 'white':
            colors.append('#999999')
    if graphviz:
        # nx.nx_agraph.write_dot(G, "C:\\Users\\Valkum\\py.dot")
        nx.draw(G, nx.nx_agraph.graphviz_layout(G, prog='neato', args='-Gstart=self -Gepsilon=.0000001'), with_labels=True, node_color=colors)
    else:
        nx.draw(G, with_labels=True, node_color=colors)

def save_closure(closure, tree, init_half_edge, path):
    import networkx as nx
    G = init_half_edge.to_networkx_graph()
    # nx.nx_agraph.write_dot(G, path)
    nx.readwrite.gexf.write_gexf(G, path)
    


def irreducible_dissection_test():
    from framework.irreducible_dissection_decomposition import irreducible_dissection_grammar

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'

    BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)
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
    argparser.add_argument('--gephi', action='store', help='save as gephi file to path')
    argparser.add_argument('--other', action='store_true', help='Run the other_test function')
    argparser.add_argument('--closure', action='store_true', help='Run the closure_test function')
    argparser.add_argument('--irdi', action='store_true', help='Run the irreducible_dissection_test function')
    argparser.add_argument('--graphviz', action='store_true', help='Use Graphviz layout')

    argparser.add_argument('--primal_map', action='store_true', help='Run the primal_map_test function')
    argparser.add_argument('--whitney_bijection', action='store_true', help='Run the whitney_bijection_test function')

    args = argparser.parse_args()

    logging.basicConfig(level=args.loglevel)

    if args.binary_tree:
        tree = binary_tree_test()
        if args.print:
            pretty_print_tree(tree)
        if args.plot:
            import matplotlib.pyplot as plt
            plot_binary_tree(tree)
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
            plot_binary_tree(tree)
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

if __name__ == '__main__':
    main()
