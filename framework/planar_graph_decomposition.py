from .decomposition_grammar import AliasSampler
from .samplers.generic_samplers import *
from .samplers.special_samplers import SpecialSampler1, SpecialSampler2, \
    EdgeRootedThreeConnectedPlanarGraphSampler, LDerThreeConnectedPlanarGraphSampler
from .decomposition_grammar import DecompositionGrammar
from .bijections.networks import *
from .bijections.two_connected import *

# some shortcuts to make the grammar more readable
Z = ZeroAtomSampler()
L = LAtomSampler()
U = UAtomSampler()
Bij = BijectionSampler
Trans = TransformationSampler

Link = AliasSampler('Link')
D = AliasSampler('D')
S = AliasSampler('S')
P = AliasSampler('P')
H = AliasSampler('H')

D_dx = AliasSampler('D_dx')
S_dx = AliasSampler('S_dx')
P_dx = AliasSampler('P_dx')
H_dx = AliasSampler('H_dx')

G_3_arrow = AliasSampler('G_3_arrow')
G_3_arrow_dy = AliasSampler('G_3_arrow_dy')
G_3_arrow_dx = AliasSampler('G_3_arrow_dx')

G_2_arrow = AliasSampler('G_2_arrow')
G_2_arrow_dy = AliasSampler('G_2_arrow_dy')
G_2_arrow_dx = AliasSampler('G_2_arrow_dx')

G_2_dx = AliasSampler('G_2_dx')
G_2_dx_dx = AliasSampler('G_2_dx_dx')
G_2_dy = AliasSampler('G_2_dy')
G_2_dy_dx = AliasSampler('G_2_dy_dx')
F = AliasSampler('F')
F_dx = AliasSampler('F_dx')

G_1 = AliasSampler('G_1')
G_1_dx = AliasSampler('G_1_dx')
G_1_dx_dx = AliasSampler('G_1_dx_dx')

G = AliasSampler('G')
G_dx = AliasSampler('G_dx')

planar_graph_grammar = DecompositionGrammar()
#planar_graph_grammar.add_rules(BinaryTreeGrammar.get_rules())
planar_graph_grammar.add_rules({
    # notice that "+" and "*" of the samplers is left-associative.

    # 3 connected planar graphs
    # here we use dummy samplers at the moment
    #'G_3_arrow': EdgeRootedThreeConnectedPlanarGraphSampler(),
    #"G_3_arrow'": LDerThreeConnectedPlanarGraphSampler(),
    #'G_3_arrow_dy': UDerFromLDer(LDerThreeConnectedPlanarGraphSampler(), 3.0),  # for this 3.0 see 5.3.3.

    'G_3_arrow': Z,
    'G_3_arrow_dx': Z,
    'G_3_arrow_dy': Z,

    # networks
    'Link': Bij(U, u_atom_to_network),  # introduce this just for readability
    'D': Link + S + P + H,
    'S': Bij((Link + P + H) * L * D, s_decomp_to_network),
    'P': Bij((Link * SetSampler(1, S + H)), p_decomp1_to_network) + Bij(SetSampler(2, S + H), p_decomp2_to_network),
    'H': Bij(USubsSampler(G_3_arrow, D), g_3_arrow_to_network),

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

    # 1 connected planar graphs
    'G_1_dx': SetSampler(0, LSubsSampler(G_2_dx, L * G_1_dx)),
    'G_1_dx_dx': (G_1_dx + L * G_1_dx_dx) * (LSubsSampler(G_2_dx_dx, L * G_1_dx)) * G_1_dx,
    'G_1': RejectionSampler(G_1_dx, lambda g: bern(1 / (g.get_l_size() + 1)), 'G_1'), #lemma 15

    # planar graphs
    'G': SetSampler(0, G_1),
    'G_dx': G_1_dx * G,
    'G_dx_dx': G_1_dx_dx * G + G_1_dx * G_dx,

})

# then sample a planar graph from this grammar using
# planar_graph_grammar.sample("G_dx_dx''")
