from framework.samplers.generic_samplers import *
from framework.samplers.special_samplers import SpecialSampler1, SpecialSampler2, \
    EdgeRootedThreeConnectedPlanarGraphSampler, LDerThreeConnectedPlanarGraphSampler
from .decomposition_grammar import DecompositionGrammar
from .bijections.networks import *

# some shortcuts to make the grammar more readable
Z = ZeroAtom()
L = LAtom()
U = UAtom()
Bij = Bijection

Link = Alias('Link')
D = Alias('D')
S = Alias('S')
P = Alias('P')
H = Alias('H')

D_dx = Alias('D_dx')
S_dx = Alias('S_dx')
P_dx = Alias('P_dx')
H_dx = Alias('H_dx')

G_3_arrow = Alias('G_3_arrow')
G_3_arrow_dy = Alias('G_3_arrow_dy')
G_3_arrow_dx = Alias('G_3_arrow_dx')

G_2_arrow = Alias('G_2_arrow')
G_2_arrow_dy = Alias('G_2_arrow_dy')
G_2_arrow_dx = Alias('G_2_arrow_dx')

G_2_dx = Alias('G_2_dx')
G_2_dx_dx = Alias('G_2_dx_dx')
G_2_dy = Alias('G_2_dy')
G_2_dy_dx = Alias('G_2_dy_dx')
F = Alias('F')
F_dx = Alias('F_dx')

G_1 = Alias('G_1')
G_1_dx = Alias('G_1_dx')
G_1_dx_dx = Alias('G_1_dx_dx')

G = Alias('G')
G_dx = Alias('G_dx')

planar_graph_grammar = DecompositionGrammar()
planar_graph_grammar.add_rules({
    # notice that "+" and "*" of the samplers is left-associative.

    # 3 connected planar graphs
    # here we use dummy samplers at the moment
    'G_3_arrow': EdgeRootedThreeConnectedPlanarGraphSampler(),
    "G_3_arrow'": LDerThreeConnectedPlanarGraphSampler(),
    'G_3_arrow_dy': UDerFromLDer(LDerThreeConnectedPlanarGraphSampler(), 3.0),  # for this 3.0 see 5.3.3.

    # networks
    'Link': Bij(U, u_atom_to_network),  # introduce this just for readability
    'D': Link + S + P + H,
    'S': Bij((Link + P + H) * L * D, s_decomp_to_network),
    'P': Bij((Link * Set(1, S + H)), p_decomp1_to_network) + Bij(Set(2, S + H), p_decomp2_to_network),
    'H': Bij(USubs(G_3_arrow, D), g_3_arrow_to_network),

    # l-derived networks
    'D_dx': S_dx + P_dx + H_dx,
    'S_dx': (P_dx + H_dx) * L * D + (U + P + H) * (D + L + D_dx), # todo bijection
    'P_dx': U * (S_dx + H_dx) * Set(0, S + H) + (S_dx + H_dx) * Set(1, S + H), # todo bijection
    'H_dx': USubs(G_3_arrow_dx, D) + D_dx * USubs(G_3_arrow_dy, D_dx),

    # 2 connected planar graphs
    'G_2_arrow': SpecialSampler1(Z + D),
    'F': L * L * G_2_arrow,
    'G_2_dy': SpecialSampler2(F),
    'G_2_dx': LDerFromUDer(G_2_dy, 2.0),  # see p. 26

    # l-derived 2 connected planar graphs
    'G_2_arrow_dx': SpecialSampler1(D_dx),
    'F_dx': L * L * G_2_arrow_dx + (L + L) * G_2_arrow, # notice that 2 * L = L + L
    'G_2_dy_dx': SpecialSampler2(F_dx),
    'G_2_dx_dx': LDerFromUDer(G_2_dy_dx, 1.0),  # see 5.5 # todo here we have to somehow convert dy_dx to dx_dy before calling LDerFromUDer

    # 1 connected planar graphs
    'G_1_dx': Set(0, LSubs(G_2_dx, L * G_1_dx)),
    'G_1_dx_dx': (G_1_dx + L * G_1_dx_dx) * (LSubs(G_2_dx_dx, L * G_1_dx)) * G_1_dx,

    # planar graphs
    'G': Set(0, G_1),
    'G_dx': G_1_dx * G,
    'G_dx_dx': G_1_dx_dx * G + G_1_dx * G_dx,

})

# then sample a planar graph from this grammar using
# planar_graph_grammar.sample("G''")
