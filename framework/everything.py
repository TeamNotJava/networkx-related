from framework.bijections.networks import *
from framework.bijections.two_connected import *
from framework.bijections.primal_map import primal_map
from framework.bijections.whitney_3map_to_3graph import whitney
from framework.binary_tree_decomposition import rejection_step, decomp_to_binary_tree_b_3, decomp_to_binary_tree_b_4, decomp_to_binary_tree_w_1_2, decomp_to_binary_tree_w_2
from framework.irreducible_dissection_decomposition import *

# All references in comments in this file refer to:
# "E. Fusy: Uniform Random Sampling of Planar Graphs in Linear Time"

# some general shortcuts to make the grammar more readable
Z = ZeroAtomSampler()
L = LAtomSampler()
U = UAtomSampler()
Set = SetSampler
LSubs = LSubsSampler
USubs = USubsSampler
Bij = BijectionSampler
Rej = RejectionSampler
Trans = TransformationSampler
DxFromDy = LDerFromUDerSampler
DyFromDx = UDerFromLDerSampler

### binary trees ###

K_dy = Alias('K_dy')
R_b_as = Alias('R_b_as')
R_w_as = Alias('R_w_as')
R_b_head = Alias('R_b_head')
R_w_head = Alias('R_w_head')
R_b = Alias('R_b')
R_w = Alias('R_w')
K = Alias('K')

binary_tree_rules = {
    'K': Bij(Rej(K_dy, rejection_step), lambda dy: dy.get_base_class_object()),
    'K_dx': DxFromDy(K_dy, alpha_l_u = 2/3),
    'K_dy': Bij(R_b_as + R_w_as, lambda tree: UDerivedClass(tree)),
    'R_b_as': Bij((R_w * L * U) + (U * L * R_w) + (R_w * L * R_w), decomp_to_binary_tree_b_3),
    'R_w_as': Bij((R_b_head * U) + (U * R_b_head) + (R_b * R_b), decomp_to_binary_tree_w_2),
    'R_b_head': Bij((R_w_head * L * U * U) + (U * U * L * R_w_head) + (R_w_head * L * R_w_head),
                    decomp_to_binary_tree_b_4),
    'R_w_head': Bij(U + (R_b * U) + (U * R_b) + (R_b * R_b), decomp_to_binary_tree_w_1_2),
    'R_b': Bij((U + R_w) * L * (U + R_w), decomp_to_binary_tree_b_3),
    'R_w': Bij((U + R_b) * (U + R_b), decomp_to_binary_tree_w_2)
}

### dissections ###

K = Alias('K')
K_dx = Alias('K_dx')
I = Alias('I')
I_dx = Alias('I_dx')
J = Alias('J')
J_dx = Alias('J_dx')
J_a = Alias('J_a')
J_a_dx = Alias('J_a_dx')

irreducible_dissection_rules = {
    'I': Bij(K, bij_closure),
    'I_dx': Bij(K_dx, bij_closure_dx),
    'J': Bij((L + L + L) * U * I, bij_j),
    'J_dx': Bij(((L + L + L) * I) + ((L + L + L) * U * I_dx), bij_j_dx),
    'J_a': Rej(J, rej_admiss),
    'J_a_dx': Rej(J_dx, rej_admiss_dx)
}

### 3-connected maps/graphs ###

G_3_arrow = Alias('G_3_arrow')
G_3_arrow_dy = Alias('G_3_arrow_dy')
G_3_arrow_dx = Alias('G_3_arrow_dx')
M_3_arrow = Alias('M_3_arrow')
M_3_arrow_dx = Alias('M_3_arrow_dx')

three_connected_rules = {
    'M_3_arrow': Bij(J_a, primal_map),
    'M_3_arrow_dx': Bij(J_a_dx, primal_map),
    'G_3_arrow': Trans(M_3_arrow, whitney, lambda eval, x, y: 0.5 * eval), # see 4.1.9.
    'G_3_arrow_dx': Trans(M_3_arrow_dx, whitney, lambda eval, x, y: 0.5 * eval),
    'G_3_arrow_dy': DyFromDx(G_3_arrow_dx, alpha_u_l = 3) # alpha_u_l = 3, see 5.3.3.
}

### networks ###

Link = Alias('Link')
D = Alias('D')
S = Alias('S')
P = Alias('P')
H = Alias('H')

D_dx = Alias('D_dx')
S_dx = Alias('S_dx')
P_dx = Alias('P_dx')
H_dx = Alias('H_dx')

network_rules = {
    'Link': Bij(U, u_atom_to_network),  # introduce this just for readability
    'D': Link + S + P + H,
    'S': Bij((Link + P + H) * L * D, s_decomp_to_network),
    'P': Bij((Link * Set(1, S + H)), p_decomp1_to_network) + Bij(Set(2, S + H), p_decomp2_to_network),
    'H': Bij(USubs(G_3_arrow, D), g_3_arrow_to_network),

    'D_dx': S_dx + P_dx + H_dx,
    'S_dx': (P_dx + H_dx) * L * D + (U + P + H) * (D + L + D_dx),  # todo bijection
    'P_dx': U * (S_dx + H_dx) * Set(0, S + H) + (S_dx + H_dx) * Set(1, S + H),  # todo bijection
    'H_dx': USubs(G_3_arrow_dx, D) + D_dx * USubs(G_3_arrow_dy, D_dx)
}

### 2-connected planar graphs ###

G_2_arrow = Alias('G_2_arrow')
G_2_arrow_dy = Alias('G_2_arrow_dy')
G_2_arrow_dx = Alias('G_2_arrow_dx')

G_2_dx = Alias('G_2_dx')
G_2_dx_dx = Alias('G_2_dx_dx')
G_2_dy = Alias('G_2_dy')
G_2_dy_dx = Alias('G_2_dy_dx')
G_2_dx_dy = Alias('G_2_dx_dy')
F = Alias('F')
F_dx = Alias('F_dx')

two_connected_rules = {
    'G_2_arrow': Trans(Z + D, add_root_edge, lambda evl, x, y: evl / (1 + BoltzmannSampler.oracle.get(y))), # see 5.5
    'F': L * L * G_2_arrow,
    'G_2_dy': Trans(F, forget_direction_of_root_edge, lambda evl, x, y: 0.5 * evl),
    'G_2_dx': DxFromDy(G_2_dy, alpha_l_u = 2.0),  # see p. 26

    'G_2_arrow_dx': Trans(D_dx, add_root_edge, lambda evl, x, y: evl / (1 + BoltzmannSampler.oracle.get(y))),
    'F_dx': L * L * G_2_arrow_dx + (L + L) * G_2_arrow,  # notice that 2 * L = L + L
    'G_2_dy_dx': Trans(F_dx, forget_direction_of_root_edge, lambda evl, x, y: 0.5 * evl),
    'G_2_dx_dy': Bij(G_2_dy_dx, lambda dy_dx: dy_dx.invert_derivation_order()),
    'G_2_dx_dx': DxFromDy(G_2_dx_dy, alpha_l_u = 1.0) # see 5.5
}

### connected planar graphs ###

G_1 = Alias('G_1')
G_1_dx = Alias('G_1_dx')
G_1_dx_dx = Alias('G_1_dx_dx')

connected_rules = {
    'G_1_dx': Set(0, LSubs(G_2_dx, L * G_1_dx)),
    'G_1_dx_dx': (G_1_dx + L * G_1_dx_dx) * (LSubs(G_2_dx_dx, L * G_1_dx)) * G_1_dx,
    'G_1': Rej(G_1_dx, lambda g: bern(1 / (g.get_l_size() + 1))) # see lemma 15
}

### planar graphs ###

G = Alias('G')
G_dx = Alias('G_dx')

planar_graphs_rules = {
    'G': Set(0, G_1),
    'G_dx': G_1_dx * G,
    'G_dx_dx': G_1_dx_dx * G + G_1_dx * G_dx
}

grammar = DecompositionGrammar()
grammar.add_rules(binary_tree_rules)
grammar.add_rules(irreducible_dissection_rules)
grammar.add_rules(three_connected_rules)
grammar.add_rules(network_rules)
grammar.add_rules(two_connected_rules)
grammar.add_rules(connected_rules)
grammar.add_rules(planar_graphs_rules)
grammar.init()

print("Recursive rules:")
[print(rule) for rule in sorted(grammar.get_recursive_rules())]
print()

print("Needed oracle queries:")
[print(query) for query in sorted(grammar.collect_oracle_queries('G_dx_dx', 'x', 'y'))]
print()
