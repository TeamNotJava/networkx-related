from framework.decomposition_grammar import Alias
from framework.irreducible_dissection_decomposition import irreducible_dissection_grammar
from framework.samplers.generic_samplers import *
from .decomposition_grammar import DecompositionGrammar
from framework.utils import bern
from framework.bijections.closure import Closure
from random import choice
import logging

L = LAtomSampler()
U = UAtomSampler()
J_a = Alias('J_a')
J_a_dx = Alias('J_a_dx')
M_3_arrow = Alias('M_3_arrow')
M_3_arrow_dx = Alias('M_3_arrow_dx')
G_3_arrow = Alias('G_3_arrow')
G_3_arrow_dx = Alias('G_3_arrow_dx')
G_3_arrow_dy = Alias('G_3_arrow_dy')
Bij = BijectionSampler
DyFromDx = UDerFromLDerSampler


def bij_primal(decomp):
    logging.error('Primal bijection bound to grammer')
    raise NotImplementedError

def bij_primal_dx(decomp):
    logging.error('Primal bijection bound to grammer')
    raise NotImplementedError

def bij_whitney(decomp):
    logging.error('Whitney bijection bound to grammer')
    raise NotImplementedError

def bij_whitney_dx(decomp):
    logging.error('Whitney bijection bound to grammer')
    raise NotImplementedError

three_connected_graph_grammar = DecompositionGrammar()
three_connected_graph_grammar.add_rules(irreducible_dissection_grammar.get_rules())
three_connected_graph_grammar.add_rules({
    'M_3_arrow': Bij(J_a, bij_primal),
    'M_3_arrow_dx': Bij(J_a_dx, bij_primal_dx),
    'G_3_arrow': Bij(M_3_arrow, bij_whitney),
    'G_3_arrow_dx': Bij(M_3_arrow_dx, bij_whitney_dx),
    'G_3_arrow_dy': DyFromDx(G_3_arrow_dx, 3),
})
three_connected_graph_grammar.init()