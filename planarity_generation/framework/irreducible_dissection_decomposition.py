from framework.decomposition_grammar import Alias
from framework.binary_tree_decomposition import binary_tree_grammar
from framework.samplers.generic_samplers import *
from .decomposition_grammar import DecompositionGrammar
from framework.utils import bern
from framework.bijections.closure import Closure
import logging

L = LAtom()
U = UAtom()
K = Alias('K')
K_dx = Alias('K_dx')
I = Alias('I')
I_dx = Alias('I_dx')
J = Alias('J')
J_dx = Alias('J_dx')

class RootedIrreducibleDissection(CombinatorialClass):
    def __init__(self, dissection):
        self.base_object = dissection
        self.root_edge = dissection

def bij_closure(decomp):
    return Closure().closure(decomp)

def bij_closure_dx(decomp):
    return Closure().closure(decomp.get_base_object())

def bij_j(decomp):
    """From ((L, U), HalfEdge) to RootedIrreducibleDissection
    """
    possible_roots = []
    visited = []
    edge = decomp.second
    while True:
        if edge.is_hexagonal:
            if edge.is_black and edge.opposite is not None and (edge not in visited):
                possible_roots.append(edge)

            possible_next_edge = edge.opposite.next
            while not possible_next_edge.is_hexagonal and possible_next_edge.opposite not in visited:
                possible_next_edge = possible_next_edge.next
            
            edge = possible_next_edge
            visited.append(edge)
        else:
            edge = edge.next

    # Choose random element from possible_roots

    return RootedIrreducibleDissection(edge)

def bij_j_dx(decomp):
    return decomp

def rej_admiss(decomp):
    return True

def rej_admiss_dx(decomp):
    return True


irreducible_dissection_grammar = DecompositionGrammar()
irreducible_dissection_grammar.add_rules(binary_tree_grammar.get_rules())
irreducible_dissection_grammar.add_rules({
    'I': Bijection(K, bij_closure),
    'I_dx': Bijection(K_dx, bij_closure_dx),
    'J': Bijection((L + L + L) * U * I, bij_j),
    'J_dx': Bijection(((L + L + L) * I) + ((L + L + L) * U + I_dx), bij_j_dx),
    'J_a': Rejection(J, rej_admiss, 'J_a'),
    'J_a_dx': Rejection(J_dx, rej_admiss_dx, 'J_a')
})
irreducible_dissection_grammar.init()