from framework.decomposition_grammar import AliasSampler
from framework.irreducible_dissection_decomposition import irreducible_dissection_grammar
from framework.samplers.generic_samplers import *
from .decomposition_grammar import DecompositionGrammar
from framework.bijections.primal_map import primal_map
from framework.bijections.whitney_3map_to_3graph import whitney
import logging

L = LAtomSampler()
U = UAtomSampler()
J_a = AliasSampler('J_a')
J_a_dx = AliasSampler('J_a_dx')
M_3_arrow = AliasSampler('M_3_arrow')
M_3_arrow_dx = AliasSampler('M_3_arrow_dx')
G_3_arrow = AliasSampler('G_3_arrow')
G_3_arrow_dx = AliasSampler('G_3_arrow_dx')
G_3_arrow_dy = AliasSampler('G_3_arrow_dy')
Bij = BijectionSampler
Trans = TransformationSampler
DyFromDx = UDerFromLDerSampler


def bij_primal(decomp):
    return primal_map(decomp)

def bij_primal_dx(decomp):
    logging.error('Primal bijection bound to grammer')
    raise NotImplementedError

def bij_whitney(decomp):
    return whitney(decomp)

def bij_whitney_dx(decomp):
    logging.error('Whitney bijection bound to grammer')
    raise NotImplementedError

three_connected_graph_grammar = DecompositionGrammar()
three_connected_graph_grammar.add_rules(irreducible_dissection_grammar.get_rules())
three_connected_graph_grammar.add_rules({
    'M_3_arrow': Bij(J_a, bij_primal),
    'M_3_arrow_dx': Bij(J_a_dx, bij_primal_dx),
    'G_3_arrow': Trans(M_3_arrow, bij_whitney,
                       eval_transform=lambda evl, x, y: 0.5 * evl),  # see 4.1.9.
    'G_3_arrow_dx': Trans(M_3_arrow_dx, bij_whitney_dx,
                          eval_transform=lambda evl, x, y: 0.5 * evl),
    'G_3_arrow_dy': DyFromDx(G_3_arrow_dx, alpha_u_l=3)  # alpha_u_l = 3, see 5.3.3.
})
three_connected_graph_grammar.init()
