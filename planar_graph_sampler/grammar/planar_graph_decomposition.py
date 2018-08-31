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

import networkx as nx

from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import *
from framework.decomposition_grammar import AliasSampler, DecompositionGrammar

from planar_graph_sampler.grammar.one_connected_decomposition import one_connected_graph_grammar


def bij_connected_comps(components):
    """Set of connected planar graphs (possibly derived) to nx.PlanarEmbedding."""
    res = nx.PlanarEmbedding()
    for g in components:
        g = g.underive_all()
        g = g.to_planar_embedding()
        res = nx.PlanarEmbedding(nx.compose(res, g))
    return res


class PlanarGraphBuilder(DefaultBuilder):
    def product(self, lhs, rhs):
        # Treat products like sets.
        rhs.append(lhs)
        return rhs


def planar_graph_grammar():
    """Constructs the grammar for planar graphs.

    Returns
    -------
    DecompositionGrammar
        The grammar for sampling from G, G_dx and G_dx_dx.
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
<<<<<<< Updated upstream
    grammar.set_builder(['G', 'G_dx', 'G_dx_dx'], PlanarGraphBuilder())
=======
<<<<<<< Updated upstream
=======
    grammar.set_builder(['G', 'G_dx', 'G_dx_dx'], PlanarGraphBuilder())
    grammar['R_w'].builder.grammar = grammar
    grammar['R_b'].builder.grammar = grammar
>>>>>>> Stashed changes
>>>>>>> Stashed changes

    return grammar


if __name__ == '__main__':
<<<<<<< Updated upstream
    import matplotlib.pyplot as plt
    from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n100, planar_graph_evals_n1000, \
        reference_evals
=======
<<<<<<< Updated upstream
    grammar = planar_graph_grammar()
    grammar.init()
=======
    import matplotlib.pyplot as plt
    from planar_graph_sampler.evaluations_planar_graph import *
>>>>>>> Stashed changes
>>>>>>> Stashed changes

    BoltzmannSamplerBase.oracle = EvaluationOracle(planar_graph_evals[10000])
    BoltzmannSamplerBase.debug_mode = False

    grammar = planar_graph_grammar()
    grammar.init()
    symbolic_x = 'x'
    symbolic_y = 'y'
    sampled_class = 'G_dx_dx'
    grammar.precompute_evals(sampled_class, symbolic_x, symbolic_y)

    # random.seed(0)

    while True:
<<<<<<< Updated upstream
=======
<<<<<<< Updated upstream

>>>>>>> Stashed changes
        try:
            g = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
            if g.l_size > 0:
                print(g)
                g = bij_connected_comps(g)
                nx.draw(g, pos=nx.combinatorial_embedding_to_pos(g), node_size=10, use_planar_drawer=True)
                plt.show()
        except RecursionError:
<<<<<<< Updated upstream
            print("Recursion error")
=======
            print("Recursion error occurred, continuing")
            pass
=======
        g = grammar.sample_iterative(sampled_class, symbolic_x, symbolic_y)
        if g.l_size > 0:
            g = bij_connected_comps(g)
            print(g.number_of_nodes())
            print()
            # nx.draw(g, pos=nx.combinatorial_embedding_to_pos(g), node_size=10, use_planar_drawer=True)
            # plt.show()

>>>>>>> Stashed changes
>>>>>>> Stashed changes
