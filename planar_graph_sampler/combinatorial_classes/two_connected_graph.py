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

from planar_graph_sampler.combinatorial_classes.half_edge_graph import HalfEdgeGraph
from planar_graph_sampler.combinatorial_classes.one_connected_graph import OneConnectedPlanarGraph


class TwoConnectedPlanarGraph(HalfEdgeGraph):
    """
    A two-connected planar graph in half-edge representation.
    """

    def __init__(self, half_edge):
        super(TwoConnectedPlanarGraph, self).__init__(half_edge)

    @property
    def is_consistent(self):
        super_ok = super(TwoConnectedPlanarGraph, self).is_consistent
        # TODO
        two_connected = True #self.is_connected(2)
        planar = self.is_planar
        return all([super_ok, two_connected, planar])

    # CombinatorialClass interface.

    def random_l_atom(self):
        return self.random_node_half_edge()

    def l_atoms(self):
        return iter([half_edge_list[0] for half_edge_list in self.half_edge.node_dict().values()])
        # return iter(self.half_edge.get_node_list().keys())

    def replace_l_atoms(self, sampler, x, y, exceptions=None):
        nodes = self.half_edge.node_dict()
        # Sample a graph and merge it with all remaining nodes.
        for node in nodes:
            if node in [he.node_nr for he in exceptions]:
                continue
            # Sampler is for L * G_1_dx
            plug_in = sampler.sample(x, y).second.marked_atom # base_class_object.half_edge
            if not plug_in.is_trivial:
                # Get an arbitrary half-edge incident to the current node.
                he = nodes[node][0]
                he.insert_all(plug_in)
        return OneConnectedPlanarGraph(self.half_edge)

    def __str__(self):
        return "2-connected planar graph (l: {}, u: {})".format(self.number_of_nodes, self.number_of_edges)


class EdgeRootedTwoConnectedPlanarGraph(TwoConnectedPlanarGraph):

    def __init__(self, root_half_edge):
        super(EdgeRootedTwoConnectedPlanarGraph, self).__init__(root_half_edge)

    @property
    def u_size(self):
        return super(EdgeRootedTwoConnectedPlanarGraph, self).u_size - 1

    @property
    def l_size(self):
        return super(EdgeRootedTwoConnectedPlanarGraph, self).l_size - 2
