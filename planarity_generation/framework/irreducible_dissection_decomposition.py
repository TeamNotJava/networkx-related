from framework.decomposition_grammar import Alias
from framework.binary_tree_decomposition import binary_tree_grammar
from framework.samplers.generic_samplers import *
from .decomposition_grammar import DecompositionGrammar
from framework.utils import bern
from framework.bijections.closure import Closure
from random import choice
import logging

L = LAtomSampler()
U = UAtomSampler()
K = Alias('K')
K_dx = Alias('K_dx')
I = Alias('I')
I_dx = Alias('I_dx')
J = Alias('J')
J_dx = Alias('J_dx')
color_black = 0
color_white = 1
Bij = BijectionSampler
Rej = RejectionSampler


class RootedIrreducibleDissection(CombinatorialClass):
    def __init__(self, dissection):
        self.base_object = dissection
        self.root_edge = dissection

    def __str__(self):
        return str(self.base_object) + '->' + str(self.root_edge)


def bij_closure(decomp):
    return Closure().closure(decomp)


def bij_closure_dx(decomp):
    return Closure().closure(decomp.get_base_class_object())


def random_rooted_edge(half_edge_ptr):
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


def bij_j(decomp):
    """From ((L, U), HalfEdge) to RootedIrreducibleDissection
    """
    rooted_edge = random_rooted_edge(decomp.second)

    return RootedIrreducibleDissection(rooted_edge)


def bij_j_dx(decomp):
    """From (L, HalfEdge) or ((L, U), HalfEdge) to RootedIrreducibleDissection
    """
    rooted_edge = random_rooted_edge(decomp.second)

    return RootedIrreducibleDissection(rooted_edge)


def rej_admiss(decomp):
    return True


def rej_admiss_dx(decomp):
    return True


irreducible_dissection_grammar = DecompositionGrammar()
irreducible_dissection_grammar.add_rules(binary_tree_grammar.get_rules())
irreducible_dissection_grammar.add_rules({
    'I': Bij(K, bij_closure),
    'I_dx': Bij(K_dx, bij_closure_dx),
    'J': Bij((L + L + L) * U * I, bij_j),
    'J_dx': Bij(((L + L + L) * I) + ((L + L + L) * U * I_dx), bij_j_dx),
    'J_a': Rej(J, rej_admiss, 'J_a'),
    'J_a_dx': Rej(J_dx, rej_admiss_dx, 'J_a')
})
irreducible_dissection_grammar.init()
