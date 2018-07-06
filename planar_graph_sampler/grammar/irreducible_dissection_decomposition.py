import logging
from random import choice
import networkx as nx

from framework.generic_samplers import *
from framework.generic_classes import CombinatorialClass
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.evaluation_oracle import EvaluationOracle

from planar_graph_sampler.bijections.closure import Closure
from planar_graph_sampler.grammar.binary_tree_decomposition import binary_tree_grammar
from planar_graph_sampler.rejections.admissibility_check import check_admissibility
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100


class RootedIrreducibleDissection(CombinatorialClass):
    """
    Bicolored irreducible dissection of the hexagon that carries a root.
    # TODO probably should be returned from closure directly
    """

    def __init__(self, root_edge):
        self.root_edge = root_edge

    def random_rooted_edge(self):
        color_black = 0
        color_white = 1
        possible_roots = []
        edge = self.root_edge
        visited = [edge.node_nr]
        # There is no way visited should be larger than 6 because we have a hexagon
        while len(visited) <= 6:
            if edge.is_hexagonal:
                if edge.color is color_black and edge.opposite is not None and (edge not in possible_roots):
                    logging.debug("Adding edge {}".format(edge))
                    possible_roots.append(edge)

                possible_next_edge = edge.opposite.next
                logging.debug("checking edge {}".format(edge))
                while not possible_next_edge.is_hexagonal and possible_next_edge.opposite is not edge:
                    logging.debug("edge {} is not hexagonal or previous edge".format(edge))
                    possible_next_edge = possible_next_edge.next

                edge = possible_next_edge
                visited.append(edge.node_nr)
                logging.debug("Visited {}".format(visited))
            else:
                edge = edge.next

        logging.debug("Possible routed edges {}".format(possible_roots))

        # Choose random element from possible_roots
        rooted_edge = choice(possible_roots)

        self.root_edge = rooted_edge

    def to_networkx_graph(self):
        # TODO does not handle graphs with just one node correctly
        res = self.root_edge.to_networkx_graph()
        return res

    def plot(self):
        G = self.to_networkx_graph()
        colors = []
        for x in nx.get_node_attributes(G, 'color').values():
            if x is 'black':
                colors.append('#333333')
            elif x is 'white':
                colors.append('#999999')
        nx.draw(G, with_labels=True, node_color=colors)

    def get_u_size(self):
        raise NotImplementedError

    def get_l_size(self):
        raise NotImplementedError

    def u_atoms(self):
        raise NotImplementedError

    def l_atoms(self):
        raise NotImplementedError

    def replace_u_atoms(self, sampler, x, y):
        raise NotImplementedError

    def replace_l_atoms(self, sampler, x, y):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


def closure(binary_tree):
    """To be used as bijection in the grammar.

    :param binary_tree: The binary tree of l-derived binary tree to be closed
    :return: The closure/l-derived cLosure of the tree/l-derived tree
    """
    c = Closure()
    half_edge = c.closure(binary_tree)
    return RootedIrreducibleDissection(half_edge)


def add_random_root_edge(decomp):
    """From ((L, U), HalfEdge) to RootedIrreducibleDissection
    """
    diss = decomp.second
    diss.random_rooted_edge()
    return diss


def add_random_root_edge_dx(decomp):
    """From (U, HalfEdge) or ((L, U), HalfEdge) to RootedIrreducibleDissection
    """
    pass
    # todo I think we don't need it


def rej_admiss(root_edge):
    """Check if no internal 3 path exists from the root vertex to the opposite site vertex,
    to avoid 4 cycles
    """
    return check_admissibility(root_edge)


def rej_admiss_dx(decomp):
    """Check if no internal 3 path exists from the root vertex to the opposite site vertex,
    to avoid 4 cycles
    """
    return check_admissibility(decomp)


def irreducible_dissection_grammar():
    """
    Builds the dissection grammar. Must still be initialized with init().

    :return:
    """

    # Some shorthands to keep the grammar readable.
    L = LAtomSampler
    U = UAtomSampler
    K = AliasSampler('K')
    K_dx = AliasSampler('K_dx')
    I = AliasSampler('I')
    I_dx = AliasSampler('I_dx')
    J = AliasSampler('J')
    J_dx = AliasSampler('J_dx')
    Bij = BijectionSampler
    Rej = RejectionSampler

    grammar = DecompositionGrammar()
    # This grammar depends on the binary tree grammar so we add it.
    grammar.add_rules(binary_tree_grammar().get_rules())

    grammar.add_rules({

        'I': Bij(K, closure),

        'I_dx': Bij(K_dx, closure),

        'J': Bij(3*L()*U()*I, add_random_root_edge),

        'J_dx': Bij(3*U()*I + 3*L()*U()*I_dx, add_random_root_edge),

        'J_a': Rej(J, rej_admiss),

        'J_a_dx': Rej(J_dx, rej_admiss_dx),

    })
    return grammar


if __name__ == "__main__":
    grammar = irreducible_dissection_grammar()
    grammar.init()

    BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'

    sampled_class = 'I'

    diss = grammar.sample(sampled_class, symbolic_x, symbolic_y)
    import matplotlib.pyplot as plt
    diss.plot()
    plt.show()
