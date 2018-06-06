from framework.decomposition_grammar import AliasSampler
from framework.three_connected_graph_decomposition import three_connected_graph_grammar
from framework.samplers.generic_samplers import *
from .decomposition_grammar import DecompositionGrammar
from framework.utils import bern
from framework.bijections.closure import Closure
from random import choice
import logging

Z = ZeroAtomSampler()
L = LAtomSampler()
U = UAtomSampler()
G_3_arrow = AliasSampler('G_3_arrow')
G_3_arrow_dx = AliasSampler('G_3_arrow_dx')
G_3_arrow_dy = AliasSampler('G_3_arrow_dy')
Link = AliasSampler('Link')
D = AliasSampler('D')
D_dx = AliasSampler('D_dx')
S = AliasSampler('S')
S_dx = AliasSampler('S_dx')
P = AliasSampler('P')
P_dx = AliasSampler('P_dx')
H = AliasSampler('H')
H_dx = AliasSampler('H_dx')
F = AliasSampler('F')
F_dx = AliasSampler('F_dx')
G_2_dy = AliasSampler('G_2_dy')
G_2_dy_dx = AliasSampler('G_2_dy_dx')
G_2_arrow = AliasSampler('G_2_arrow')
G_2_arrow_dx = AliasSampler('G_2_arrow_dx')
Bij = BijectionSampler
DyFromDx = UDerFromLDerSampler
Trans = TransformationSampler


def bij_u_atom_to_network(decomp):
    raise NotImplementedError

def bij_s_decomp_to_network(decomp):
    raise NotImplementedError

def bij_p_decomp1_to_network(decomp):
    raise NotImplementedError

def bij_p_decomp2_to_network(decomp):
    raise NotImplementedError

def bij_g_3_arrow_to_network(decomp):
    raise NotImplementedError

def add_root_edge(decomp):
    raise NotImplementedError

def forget_direction_of_root_edge(decomp):
    raise NotImplementedError

two_connected_graph_grammar = DecompositionGrammar()
two_connected_graph_grammar.add_rules(three_connected_graph_grammar.get_rules())
two_connected_graph_grammar.add_rules({
    # networks
    'Link': Bij(U, bij_u_atom_to_network),  # introduce this just for readability
    'D': Link + S + P + H,
    'S': Bij((Link + P + H) * L * D, bij_s_decomp_to_network),
    'P': Bij((Link * SetSampler(1, S + H)), bij_p_decomp1_to_network) + Bij(SetSampler(2, S + H), bij_p_decomp2_to_network),
    'H': Bij(USubsSampler(G_3_arrow, D), bij_g_3_arrow_to_network),

    # l-derived networks
    'D_dx': S_dx + P_dx + H_dx,
    'S_dx': (P_dx + H_dx) * L * D + (U + P + H) * (D + L + D_dx), # todo bijection
    'P_dx': U * (S_dx + H_dx) * SetSampler(0, S + H) + (S_dx + H_dx) * SetSampler(1, S + H), # todo bijection
    'H_dx': USubsSampler(G_3_arrow_dx, D) + D_dx * USubsSampler(G_3_arrow_dy, D_dx),

    # 2 connected planar graphs
    'G_2_arrow': Trans(Z + D, add_root_edge, 'G_2_arrow'), # have to pass target class label to transformation sampler
    'F': L * L * G_2_arrow,
    'G_2_dy': Trans(F, forget_direction_of_root_edge, 'G_2_dy'),
    'G_2_dx': LDerFromUDerSampler(G_2_dy, 2.0),  # see p. 26

    # l-derived 2 connected planar graphs
    'G_2_arrow_dx': Trans(D_dx, add_root_edge, 'G_2_arrow_dx'),
    'F_dx': L * L * G_2_arrow_dx + (L + L) * G_2_arrow, # notice that 2 * L = L + L
    'G_2_dy_dx': Trans(F_dx, forget_direction_of_root_edge, 'G_2_dy_dx'),
    'G_2_dx_dx': LDerFromUDerSampler(G_2_dy_dx, 1.0),  # see 5.5 # todo here we have to somehow convert dy_dx to dx_dy before calling LDerFromUDer
})
two_connected_graph_grammar.init()