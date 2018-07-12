from framework.class_builder import CombinatorialClassBuilder
from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import *
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.utils import Counter
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge
from planar_graph_sampler.combinatorial_classes.two_connected_graph import EdgeRootedTwoConnectedPlanarGraph, \
    UDerivedTwoConnectedPlanarGraph, LDerivedTwoConnectedPlanarGraph, ULDerivedTwoConnectedPlanarGraph, \
    BiLDerivedTwoConnectedPlanarGraph
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals_n1000, planar_graph_evals_n100

from planar_graph_sampler.grammar.network_decomposition import network_grammar
from planar_graph_sampler.combinatorial_classes import UDerivedClass


def to_G_2_dy(decomp):
    return UDerivedTwoConnectedPlanarGraph(decomp.second.get_half_edge())

def to_G_2_dx(g_2_dy):
    return LDerivedTwoConnectedPlanarGraph(g_2_dy.get_half_edge())

def to_G_2_dx_dx(g_2_dy):
    return BiLDerivedTwoConnectedPlanarGraph(g_2_dy.get_half_edge())

def to_G_2_dx_dy(decomp):
    return ULDerivedTwoConnectedPlanarGraph(decomp.second.get_half_edge())


class ZeroAtomGraphBuilder(CombinatorialClassBuilder):
    def __init__(self):
        self.counter = Counter()

    def zero_atom(self):
        root_half_edge = HalfEdge(self_consistent=True)
        root_half_edge.node_nr = next(self.counter)
        root_half_edge_opposite = HalfEdge(self_consistent=True)
        root_half_edge_opposite.node_nr = next(self.counter)
        root_half_edge.opposite = root_half_edge_opposite
        root_half_edge_opposite.opposite = root_half_edge
        return EdgeRootedTwoConnectedPlanarGraph(root_half_edge)


def two_connected_graph_grammar():
    """

    :return:
    """

    Z = ZeroAtomSampler
    L = LAtomSampler
    D = AliasSampler('D')
    D_dx = AliasSampler('D_dx')
    F = AliasSampler('F')
    F_dx = AliasSampler('F_dx')
    G_2_dy = AliasSampler('G_2_dy')
    G_2_dy_dx = AliasSampler('G_2_dy_dx')
    G_2_dx_dy = AliasSampler('G_2_dx_dy')
    G_2_arrow = AliasSampler('G_2_arrow')
    G_2_arrow_dx = AliasSampler('G_2_arrow_dx')
    Trans = TransformationSampler
    Bij = BijectionSampler
    DxFromDy = LDerFromUDerSampler

    grammar = DecompositionGrammar()
    grammar.add_rules(network_grammar().get_rules())

    grammar.add_rules({

        # two connected

        'G_2_arrow': Trans(Z() + D,
                           eval_transform=lambda evl, x, y: evl / (1 + BoltzmannSampler.oracle.get(y))),  # see 5.5

        'F': Bij(L() ** 2 * G_2_arrow, to_G_2_dy),

        'G_2_dy': Trans(F, eval_transform=lambda evl, x, y: 0.5 * evl),

        'G_2_dx': Bij(DxFromDy(G_2_dy, alpha_l_u=2.0), to_G_2_dx),  # see p. 26

        # l-derived two connected

        'G_2_arrow_dx': Trans(D_dx, eval_transform=lambda evl, x, y: evl / (1 + BoltzmannSampler.oracle.get(y))),

        'F_dx': Bij(L() ** 2 * G_2_arrow_dx + 2 * L() * G_2_arrow, to_G_2_dx_dy),

        'G_2_dy_dx': Trans(F_dx, eval_transform=lambda evl, x, y: 0.5 * evl),

        'G_2_dx_dy': G_2_dy_dx,

        'G_2_dx_dx': Bij(DxFromDy(G_2_dx_dy, alpha_l_u=1.0), to_G_2_dx_dx)  # see 5.5

    })
    grammar.set_builder(['G_2_arrow'], ZeroAtomGraphBuilder())

    return grammar


if __name__ == '__main__':
    grammar = two_connected_graph_grammar()
    grammar.init()

    BoltzmannSampler.oracle = EvaluationOracle(planar_graph_evals_n100)
    BoltzmannSampler.debug_mode = False

    symbolic_x = 'x*G_1_dx(x,y)'
    symbolic_y = 'y'

    sampled_class = 'G_2_dx_dx'

    while True:
        try:
            g = grammar.sample(sampled_class, symbolic_x, symbolic_y)
        except RecursionError:
            pass
        if g.get_l_size() > 10:
            print(g)
            assert g.is_consistent()

            import matplotlib.pyplot as plt

            g.plot(with_labels=False)
            plt.show()
