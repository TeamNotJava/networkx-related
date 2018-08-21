# -*- coding: utf-8 -*-
#    Copyright (C) 2018 by
#    Marta Grobelna <marta.grobelna@rwth-aachen.de>
#    Petre Petrov <petrepp4@gmail.com>
#    Rudi Floren <rudi.floren@gmail.com>
#    Tobias Winkler <tobias.winkler1@rwth-aachen.de>
#    All rights reserved.
#    BSD license.
#
# Authors:  Marta Grobelna <marta.grobelna@rwth-aachen.de>
#           Petre Petrov <petrepp4@gmail.com>
#           Rudi Floren <rudi.floren@gmail.com>
#           Tobias Winkler <tobias.winkler1@rwth-aachen.de>

from timeit import default_timer as timer

from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.generic_samplers import *
from framework.generic_classes import DummyClass
from framework.class_builder import DummyBuilder
from framework.generic_samplers import BoltzmannSamplerBase
from framework.utils import bern

from planar_graph_sampler.evaluations_planar_graph import *

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


# identity function
def id(x):
    return x


### binary trees ###

K_dy = AliasSampler('K_dy')
K_dx = AliasSampler('K_dx')
R_b_as = AliasSampler('R_b_as')
R_w_as = AliasSampler('R_w_as')
R_b_head = AliasSampler('R_b_head')
R_w_head = AliasSampler('R_w_head')
R_b = AliasSampler('R_b')
R_w = AliasSampler('R_w')
K = AliasSampler('K')

binary_tree_rules = {
    'K': Bij(
        Rej(K_dy, lambda gamma: bern(2 / (gamma.u_size() + 1))),
        lambda gamma: DummyClass(gamma.l_size(), gamma.u_size() + 1)  # u size increases by 1 due to underive
    ),
    'K_dx': DxFromDy(K_dy, alpha_l_u=2 / 3),
    'K_dy': R_b_as + R_w_as,
    'R_b_as': (R_w * L * U) + (U * L * R_w) + (R_w * L * R_w),
    'R_w_as': (R_b_head * U) + (U * R_b_head) + R_b ** 2,
    'R_b_head': (R_w_head * L * U * U) + (U * U * L * R_w_head) + (R_w_head * L * R_w_head),
    'R_w_head': U + (R_b * U) + (U * R_b) + R_b ** 2,
    'R_b': (U + R_w) * L * (U + R_w),
    'R_w': (U + R_b) * (U + R_b)
}

### dissections ###

I = AliasSampler('I')
I_dx = AliasSampler('I_dx')
J = AliasSampler('J')
J_dx = AliasSampler('J_dx')
J_a = AliasSampler('J_a')
J_a_dx = AliasSampler('J_a_dx')


def admissible_approx(dissection):
    # a dissection with 5 or less inner faces (tree with <=5 leaves) can't be admissible
    # because there is an internal path with 3 edges from any outer black node to its opposite white node
    return dissection.u_size() > 5


irreducible_dissection_rules = {
    'I': K,
    'I_dx': K_dx,
    'J': 3 * L * U * I,  # 1 of the 3 outer black nodes count and the outer face counts
    'J_dx': (3 * U * I) + (3 * L * U * I_dx),
    'J_a': Rej(J, admissible_approx),
    'J_a_dx': Trans(J_dx, admissible_approx),
}

### 3-connected maps/graphs ###

G_3_arrow = AliasSampler('G_3_arrow')
G_3_arrow_dy = AliasSampler('G_3_arrow_dy')
G_3_arrow_dx = AliasSampler('G_3_arrow_dx')
M_3_arrow = AliasSampler('M_3_arrow')
M_3_arrow_dx = AliasSampler('M_3_arrow_dx')

three_connected_rules = {
    'M_3_arrow': J_a,  # add root edge + primal map (preserves all sizes)
    'M_3_arrow_dx': J_a_dx,
    'G_3_arrow': Trans(M_3_arrow, id,  # identity transformation
                       eval_transform=lambda evl, x, y: 0.5 * evl),  # see 4.1.9.
    'G_3_arrow_dx': Trans(M_3_arrow_dx, id,  # identity transformation
                          eval_transform=lambda evl, x, y: 0.5 * evl),
    'G_3_arrow_dy': DyFromDx(G_3_arrow_dx, alpha_u_l=3)  # _alpha_u_l = 3, see 5.3.3.
}

### networks ###

D = AliasSampler('D')
S = AliasSampler('S')
P = AliasSampler('P')
H = AliasSampler('H')

D_dx = AliasSampler('D_dx')
S_dx = AliasSampler('S_dx')
P_dx = AliasSampler('P_dx')
H_dx = AliasSampler('H_dx')

network_rules = {
    'D': U + S + P + H,
    'S': (U + P + H) * L * D,
    'P': U * Set(1, S + H) + Set(2, S + H),
    'H': USubs(G_3_arrow, D),

    'D_dx': S_dx + P_dx + H_dx,
    'S_dx': (P_dx + H_dx) * L * D + (U + P + H) * (D + L * D_dx),
    'P_dx': U * (S_dx + H_dx) * Set(0, S + H) + (S_dx + H_dx) * Set(1, S + H),
    'H_dx': USubs(G_3_arrow_dx, D) + D_dx * USubs(G_3_arrow_dy, D)
}

### 2-connected planar graphs ###

G_2_arrow = AliasSampler('G_2_arrow')
G_2_arrow_dy = AliasSampler('G_2_arrow_dy')
G_2_arrow_dx = AliasSampler('G_2_arrow_dx')

G_2_dx = AliasSampler('G_2_dx')
G_2_dx_dx = AliasSampler('G_2_dx_dx')
G_2_dy = AliasSampler('G_2_dy')
G_2_dy_dx = AliasSampler('G_2_dy_dx')
G_2_dx_dy = AliasSampler('G_2_dx_dy')
F = AliasSampler('F')
F_dx = AliasSampler('F_dx')

two_connected_rules = {
    'G_2_arrow': Trans(Z + D, id,  # I think maybe sometimes the u-size can decrese by one
                       # if there is already the root edge present.
                       eval_transform=lambda evl, x, y: evl / (1 + BoltzmannSamplerBase.oracle.get(y))),  # see 5.5
    'F': L ** 2 * G_2_arrow,
    'G_2_dy': Trans(F, id,
                    eval_transform=lambda evl, x, y: 0.5 * evl),
    'G_2_dx': DxFromDy(G_2_dy, alpha_l_u=2.0),  # see p. 26

    'G_2_arrow_dx': Trans(D_dx, id,
                          eval_transform=lambda evl, x, y: evl / (1 + BoltzmannSamplerBase.oracle.get(y))),
    'F_dx': L ** 2 * G_2_arrow_dx + 2 * L * G_2_arrow,  # notice that 2 * L = L + L
    'G_2_dy_dx': Trans(F_dx, id,
                       eval_transform=lambda evl, x, y: 0.5 * evl),
    'G_2_dx_dy': G_2_dy_dx,
    'G_2_dx_dx': DxFromDy(G_2_dx_dy, alpha_l_u=1.0)  # see 5.5
}

### connected planar graphs ###

G_1 = AliasSampler('G_1')
G_1_dx = AliasSampler('G_1_dx')
G_1_dx_dx = AliasSampler('G_1_dx_dx')

connected_rules = {
    'G_1_dx': Set(0, LSubs(G_2_dx, L * G_1_dx)),
    'G_1_dx_dx': (G_1_dx + L * G_1_dx_dx) * (LSubs(G_2_dx_dx, L * G_1_dx)) * G_1_dx,
    'G_1': Rej(G_1_dx, lambda g: bern(1 / (g.l_size() + 1)))  # see lemma 15
}

### planar graphs ###

G = AliasSampler('G')
G_dx = AliasSampler('G_dx')

planar_graphs_rules = {
    'G': Set(0, G_1),
    'G_dx': G_1_dx * G,
    'G_dx_dx': G_1_dx_dx * G + G_1_dx * G_dx
}

if __name__ == "__main__":
    start_main = timer()
    grammar = DecompositionGrammar()
    grammar.add_rules(binary_tree_rules)
    grammar.add_rules(irreducible_dissection_rules)
    grammar.add_rules(three_connected_rules)
    grammar.add_rules(network_rules)
    grammar.add_rules(two_connected_rules)
    grammar.add_rules(connected_rules)
    grammar.add_rules(planar_graphs_rules)
    grammar.init()
    # todo make this work
    grammar.set_builder(builder=DummyBuilder())

    oracles = {
        '100': {'oracle': planar_graph_evals_n100, 'size': 100},
        '1000': {'oracle': planar_graph_evals_n1000, 'size': 1000},
        '1000m2': {'oracle': planar_graph_evals_n1000_mu2, 'size': 1000},
    }
    oracle = '1000'
    BoltzmannSamplerBase.oracle = EvaluationOracle(oracles[oracle]['oracle'])
    end_main = timer()

    #symbolic_x = 'x*G_1_dx(x,y)'
    # symbolic_y = 'D(x*G_1_dx(x,y),y)'
    symbolic_x = 'x'
    symbolic_y = 'y'

    sampled_class = 'G_dx_dx'

    # print("Recursive rules:")
    # [print(rule) for rule in grammar.get_recursive_rules()]
    # print()

    print("Needed oracle queries:")
    [print(query) for query in sorted(grammar.collect_oracle_queries(sampled_class, symbolic_x, symbolic_y))]
    print()

    samples = 100000

    sampled_objects = []
    first_hit = None
    first_near_hit = None
    first_near_near_hit = None
    hits = 0
    near_hits = 0
    near_near_hits = 0
    start_sample = timer()
    recErrorCounter = 0
    for i in range(samples):
        try:
            dummy = grammar.sample_dummy(sampled_class, symbolic_x, symbolic_y)
        except RecursionError:
            recErrorCounter += 1
            pass
        wanted_size = oracles[oracle]['size']
        if (dummy.l_size() is wanted_size):
            if first_hit is None:
                first_hit = i
                first_hit_time = timer()
            hits += 1
            print("exact after {0}".format(i))
            print("exact after {0}s".format(timer() - start_sample))
        if (dummy.l_size() >= wanted_size - (0.1 * wanted_size) and dummy.l_size() <= wanted_size + (
                0.1 * wanted_size)):
            if first_near_hit is None:
                first_near_hit = i
                first_near_hit_time = timer()
            near_hits += 1
            print("size +-10% after {0}".format(i))
            print("size +-10% after {0}s".format(timer() - start_sample))
        if (dummy.l_size() >= wanted_size - (0.05 * wanted_size) and dummy.l_size() <= wanted_size + (
                0.05 * wanted_size)):
            if first_near_hit is None:
                first_near_near_hit = i
                first_near_near_hit_time = timer()
            near_near_hits += 1
            print("size +-5% after {0}".format(i))
            print("size +-5% after {0}s".format(timer() - start_sample))
        sampled_objects.append(dummy)

    end_sample = timer()

    sum_l_sizes = sum([dummy.l_size() for dummy in sampled_objects])
    print("average l-size: " + str(sum_l_sizes / samples))
    sum_u_sizes = sum([dummy.u_size() for dummy in sampled_objects])
    print("average u-size: " + str(sum_u_sizes / samples))

    print("max l-size: " + str(max([dummy.l_size() for dummy in sampled_objects])))
    print("max u-size: " + str(max([dummy.u_size() for dummy in sampled_objects])))
    print("First hit of wanted size {0}: {1}".format(oracles[oracle]['size'], first_hit))
    print("First hit of wanted size {0} +- 10%: {1}".format(oracles[oracle]['size'], first_near_hit))
    print("First hit of wanted size {0} +- 5%: {1}".format(oracles[oracle]['size'], first_near_near_hit))

    print("Max Rec. errors {}".format(recErrorCounter))
    print("Timing:")
    print("Oracle setup {}s".format(end_main - start_main))
    print("Intermediate {}s".format(start_sample - end_main))
    print("Sampling {}s".format(end_sample - start_sample))
    if first_hit:
        print("Time to size {}: {}s".format(oracles[oracle]['size'], first_hit_time - start_sample))

    if first_near_hit:
        print("Time to size {0} +- 10%: {1}s".format(oracles[oracle]['size'], first_near_hit_time - start_sample))
        print("Amount of +- 10% hits: {}".format(near_hits))
    if first_near_near_hit:
        print("Time to size {0} +- 5%: {1}s".format(oracles[oracle]['size'], first_near_near_hit_time - start_sample))
        print("Amount of +- 5% hits: {}".format(near_near_hits))
