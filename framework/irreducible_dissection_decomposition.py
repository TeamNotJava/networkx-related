import logging
from random import choice

from .bijections.closure import Closure
from .binary_tree_decomposition import binary_tree_grammar, BinaryTree
from .decomposition_grammar import AliasSampler
from .rejections.admissibility_check import check_admissibility
from .samplers.generic_samplers import *
from .decomposition_grammar import DecompositionGrammar
from .evaluation_oracle import EvaluationOracle
from .evaluations_planar_graph import planar_graph_evals_n100


class RootedIrreducibleDissection(CombinatorialClass):
    def __init__(self, dissection, root_edge=None):
        self.base_object = dissection
        self.root_edge = root_edge

    def __str__(self):
        return str(self.base_object) + '->' + str(self.root_edge)


def closure(binary_tree):
    """To be used as bijection in the grammar.

    :param binary_tree: The binary tree of l-derived binary tree to be closed
    :return: The closure/l-derived cosure of the tree/l-derived tree
    """
    c = Closure()
    if isinstance(binary_tree, LDerivedClass):
        return c.closure(binary_tree.get_base_class_object())
    else:
        assert isinstance(binary_tree, BinaryTree)
        return c.closure(binary_tree)


def random_rooted_edge(half_edge_ptr):
    color_black = 0
    color_white = 1
    possible_roots = []
    edge = half_edge_ptr
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

    return rooted_edge


def add_random_root_edge(decomp):
    """From ((L, U), HalfEdge) to RootedIrreducibleDissection
    """
    dissection = decomp.second
    root_edge = random_rooted_edge(dissection)
    return RootedIrreducibleDissection(dissection, root_edge)


def add_random_root_edge_dx(decomp):
    """From (U, HalfEdge) or ((L, U), HalfEdge) to RootedIrreducibleDissection
    """
    pass
    # todo I think we dont need it


def rej_admiss(rooted_irred_dissection):
    """Check if no internal 3 path exists from the root vertex to the opposite site vertex,
    to avoid 4 cycles
    """
    return check_admissibility(rooted_irred_dissection.root_edge)


def rej_admiss_dx(decomp):
    """Check if no internal 3 path exists from the root vertex to the opposite site vertex,
    to avoid 4 cycles
    """
    return check_admissibility(decomp)


L = LAtomSampler()
U = UAtomSampler()

K = AliasSampler('K')
K_dx = AliasSampler('K_dx')
I = AliasSampler('I')
I_dx = AliasSampler('I_dx')
J = AliasSampler('J')
J_dx = AliasSampler('J_dx')

Bij = BijectionSampler
Rej = RejectionSampler

irreducible_dissection_grammar = DecompositionGrammar()
irreducible_dissection_grammar.add_rules(binary_tree_grammar.get_rules())
irreducible_dissection_grammar.add_rules({
    'I': Bij(K, closure),
    'I_dx': Bij(K_dx, closure),
    'J': Bij((L + L + L) * U * I, add_random_root_edge),
    'J_dx': Bij(((U + U + U) * I) + ((L + L + L) * U * I_dx), add_random_root_edge),
    'J_a': Rej(J, rej_admiss),
    'J_a_dx': Rej(J_dx, rej_admiss_dx)
})

if __name__ == "__main__":
    irreducible_dissection_grammar.init()
    BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'D(x*G_1_dx(x,y),y)'

    sampled_class = 'J_a'

    irreducible_dissection_grammar.sample(sampled_class, symbolic_x, symbolic_y)
    print("number of rejections in admissable: " + irreducible_dissection_grammar.get_rule('J_a').get_rejections_count())
