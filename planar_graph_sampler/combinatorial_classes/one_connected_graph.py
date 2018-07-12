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

from framework.generic_classes import CombinatorialClass
from framework.utils import Counter
from planar_graph_sampler.combinatorial_classes.half_edge_graph import HalfEdgeGraph
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge

counter = Counter()

class OneConnectedPlanarGraph(HalfEdgeGraph):

    def __init__(self, half_edge=None):
        if half_edge is None:
            half_edge = HalfEdge(self_consistent=True)
            half_edge.node_nr = next(counter)
        super().__init__(half_edge)
