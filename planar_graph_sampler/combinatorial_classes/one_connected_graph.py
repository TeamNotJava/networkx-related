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

from planar_graph_sampler.grammar.grammar_utils import Counter
from planar_graph_sampler.combinatorial_classes.half_edge_graph import HalfEdgeGraph
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge


class OneConnectedPlanarGraph(HalfEdgeGraph):
    """
    A graph in half-edge representation which is guaranteed to be planar and connected.
    """

    def __init__(self, half_edge=None):
        if half_edge is None:
            half_edge = HalfEdge(self_consistent=True)
            half_edge.node_nr = next(Counter())
        super(OneConnectedPlanarGraph, self).__init__(half_edge)

    @property
    def is_consistent(self):
        return self.is_planar and super(OneConnectedPlanarGraph, self).is_consistent

    def __str__(self):
        return "Connected planar graph (l: {}, u: {})".format(self.number_of_nodes, self.number_of_edges)
