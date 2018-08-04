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

import random as rn

from framework.utils import nth
from planar_graph_sampler.combinatorial_classes.half_edge_graph import HalfEdgeGraph


class Network(HalfEdgeGraph):
    """
    Represents a network.

    A network is a connected planar graph with to distinguished vertices (the 0-pole and the inf-pole) which is
    guaranteed to be 2-connected upon linking the poles.
    """

    def __init__(self, half_edge, is_linked, l_size=None, u_size=None):
        assert half_edge.opposite is not None
        super(Network, self).__init__(half_edge)
        self.is_linked = is_linked
        if l_size is None:
            l_size = self.number_of_nodes - 2
        self._l_size = l_size
        if u_size is None:
            u_size = self.number_of_edges - (not is_linked)
        self._u_size = u_size
        # assert self.is_consistent  # quite expensive assertion

    @property
    def is_consistent(self):
        super_ok = super(Network, self).is_consistent
        # Only the linked networks are 2-connected.
        is_two_connected = True #not self.is_linked or self.is_connected(2)
        return all([super_ok, is_two_connected])

    @property
    def is_link_graph(self):
        """Returns true iff this is the link graph (= u-atom)."""
        return self.number_of_nodes == 2

    @property
    def zero_pole(self):
        """Returns the half-edge between zero-pole and inf-pole."""
        return self.half_edge

    @property
    def inf_pole(self):
        """Returns the half-edge between inf-pole and zero-pole."""
        return self.half_edge.opposite

    # CombinatorialClass interface.

    @property
    def u_size(self):
        """Number of edges."""
        return self._u_size

    @property
    def l_size(self):
        """Number of vertices not counting the poles."""
        return self._l_size

    def random_u_atom(self):
        rand_index = rn.randrange(self.u_size())
        return nth(self.u_atoms(), rand_index)

    def random_l_atom(self):
        rand_index = rn.randrange(self.l_size())
        return nth(self.l_atoms(), rand_index)

    def __str__(self):
        return "Network (l: {}, u: {})".format(self.l_size, self.u_size)

    # Networkx related functionality.

    def to_networkx_graph(self, include_unpaired=False):
        g = super(Network, self).to_networkx_graph(include_unpaired=include_unpaired)
        if not self.is_linked:
            link = self.half_edge
            g.remove_edge(link.node_nr, link.opposite.node_nr)
        return g
