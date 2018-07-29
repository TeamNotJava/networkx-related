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

from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import *
from framework.decomposition_grammar import AliasSampler, DecompositionGrammar
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100

from planar_graph_sampler.grammar.one_connected_decomposition import one_connected_graph_grammar


def planar_graph_grammar():
    """

    """

    # Some shortcuts to make the grammar more readable.
    G_1 = AliasSampler('G_1')
    G_1_dx = AliasSampler('G_1_dx')
    G_1_dx_dx = AliasSampler('G_1_dx_dx')

    G = AliasSampler('G')
    G_dx = AliasSampler('G_dx')

    grammar = DecompositionGrammar()
    grammar.rules = one_connected_graph_grammar().rules
    grammar.rules = {

        # planar graphs

        'G': SetSampler(0, G_1),

        'G_dx': G_1_dx * G,

        'G_dx_dx': G_1_dx_dx * G + G_1_dx * G_dx,

    }

    return grammar


if __name__ == '__main__':
    grammar = planar_graph_grammar()
    grammar.init()

    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals_n100)
    BoltzmannSamplerBase.debug_mode = False

    symbolic_x = 'x'
    symbolic_y = 'y'

    sampled_class = 'G_dx_dx'

    try:
        print(BoltzmannSamplerBase.oracle.get_expected_l_size(sampled_class, symbolic_x, symbolic_y))
    except BoltzmannFrameworkError:
        pass

    while True:

        try:
            g = grammar.sample(sampled_class, symbolic_x, symbolic_y)
            if g.l_size > 90:
                print(g.l_size)

        except RecursionError:
            print("Recursion error occurred, continuing")
            pass
