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

from framework.generic_classes import CombinatorialClass


class HalfEdge(CombinatorialClass):
    """
    Generic class for half-edge representation of a combinatorial planar embedding.

    Parameters
    ----------
    self_consistent: bool
        Makes a consistent one-node/zero-edge graph.
    """

    def __init__(self, self_consistent=False):
        # Contains the opposite half-edge
        self.opposite = None
        # Contains the next half-edge in ccw order around the incident node
        self.next = None
        if self_consistent:
            self.next = self
        # Contains the prior half-edge in cw order around the incident node
        self.prior = None
        if self_consistent:
            self.prior = self
        # Node the half-edge is  assigned to
        self.node_nr = -1

    @property
    def l_size(self):
        return self.get_number_of_nodes()

    @property
    def u_size(self):
        return self.get_number_of_edges()

    @property
    def is_trivial(self):
        return self.next == self and self.opposite is None

    def insert_after(self, new=None):
        """Inserts a half-edge that follows this half-edge in ccw order."""
        if new is None:
            new = HalfEdge()
        new.node_nr = self.node_nr
        old_next = self.next
        self.next = new
        new.prior = self
        new.next = old_next
        old_next.prior = new
        return new

    def insert_before(self, new=None):
        """Inserts a half-edge that follows this half-edge in cw order."""
        if new is None:
            new = HalfEdge()
        new.node_nr = self.node_nr
        old_prior = self.prior
        self.prior = new
        new.next = self
        new.prior = old_prior
        old_prior.next = new
        return new

    def remove(self):
        """Removes the half-edge and and its connections.

        There is no a half-edge which has connection to it after the removal.
        """
        # Connect corresponding next and prior half edges.
        self._connect_next_and_prior()
        # Clear the half edge object.
        self.clear()

    def _connect_next_and_prior(self):
        self.next.prior = self.prior
        self.prior.next = self.next

    def clear(self):
        """Clear all the half_edge connections and data from it."""
        self.opposite = None
        self.prior = None
        self.next = None
        self.node_nr = -1

    def insert_all(self, other):
        """Inserts the given half-edge and all its incident half-edge after this half-edge."""
        # Set node numbers.
        for he in other.incident_half_edges():
            he.node_nr = self.node_nr
        other_degree = other.degree()
        old_degree = self.degree()
        old_next = self.next
        self.next = other
        old_other_prior = other.prior
        other.prior = self
        old_next.prior = old_other_prior
        old_other_prior.next = old_next
        assert self.degree() == other_degree + old_degree

    def invert(self):
        """Inverts order."""
        for h in self.incident_half_edges():
            # Swap pointers.
            h.next, h.prior = h.prior, h.next

    def degree(self):
        """Number of outgoing half edges of the incident node."""
        return len(self.incident_half_edges())

    def incident_half_edges(self):
        """Returns all half-edges incident to this half-edge, including itself.

        Two half-edges are incident if they start in the same vertex.
        """
        res = [self]
        curr = self
        while curr.next is not self:
            res += [curr.next]
            curr = curr.next
        return res

    def set_node_nr(self, node_nr):
        for he in self.incident_half_edges():
            he.node_nr = node_nr

    # TODO hack hack
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        """Represents a half-edge as a tuple (index, node_nr, opposite, next, prior)."""
        repr = "(edge_id: {0}\tnode_nr: {1}\topposite_id: {2}\tnext: {3}\tprior: {4})".format(
            id(self), self.node_nr, id(self.opposite), id(self.next), id(self.prior))
        return repr

    def list_half_edges(self, edge_list=None):
        """Returns a list with half-edges."""
        # TODO Deprecated?
        if edge_list is None:
            edge_list = []
        edge_list.append(self)
        current_half_edge = self
        while True:
            if current_half_edge.next is not None:
                current_half_edge = current_half_edge.next
                if current_half_edge is not self and current_half_edge not in edge_list:
                    edge_list.append(current_half_edge)
                    if current_half_edge.opposite is not None:
                        if current_half_edge.opposite not in edge_list:
                            current_half_edge.opposite.list_half_edges(edge_list)
                else:
                    break
            else:
                break
        return edge_list

    def node_dict(self, res=None):
        """Returns a dictionary that maps nodes to a list of half-edges in ccw order around the node."""
        if res is None:
            res = {}
        node_nr = self.node_nr
        if node_nr in res:
            # Current node was already visited.
            return res
        incident = self.incident_half_edges()
        res[node_nr] = incident
        for he in incident:
            if he.opposite is not None:
                res = he.opposite.node_dict(res)
        return res

    def get_all_half_edges(self, edge_set=None, include_opp=True, include_unpaired=True):
        """The half-edge on which this was first called is guaranteed to be in the result when include_opp is False."""
        if edge_set is None:
            edge_set = set()
        for he in self.incident_half_edges():
            if he not in edge_set:
                if he.opposite is None and include_unpaired:
                    edge_set.add(he)
                elif include_opp or (he.opposite is not None and he.opposite not in edge_set):
                    edge_set.add(he)
                    if he.opposite is not None:
                        he.opposite.get_all_half_edges(edge_set, include_opp, include_unpaired)
        return edge_set

    def get_number_of_nodes(self):
        """Returns the number of nodes in the graph."""
        edge_list = self.get_all_half_edges()
        nodes = set()
        for edge in edge_list:
            nodes.add(edge.node_nr)
        return len(nodes)

    def get_number_of_edges(self):
        """Returns the number of edges (NOT half-edges!) in the graph."""
        return len(self.get_all_half_edges(include_opp=False, include_unpaired=False))

    def get_node_list(self):
        # TODO probably replace by method that also gives right order of half edges
        """Returns a dictionary of nodes.

        The key is node number and the value is a list of half-edges belonging to the node number.
        """
        edge_list = self.get_all_half_edges()
        node_list = {}
        for edge in edge_list:
            if edge.node_nr in node_list:
                half_edges = node_list[edge.node_nr]
                half_edges.append(edge)
                node_list[edge.node_nr] = half_edges
            else:
                node_list[edge.node_nr] = [edge]
        return node_list


class ClosureHalfEdge(HalfEdge):
    """
    Half-edges with additional attributes needed in the closure.
    """

    def __init__(self, self_consistent=False):
        super(ClosureHalfEdge, self).__init__(self_consistent)
        # Number of inner edges following after the stem.
        self.number_proximate_inner_edges = 0
        # Color that indicates what color the incident node has (0 - black, 1 -white).
        self.color = None
        # Indicates if the half-edge belongs to the hexagon.
        self.is_hexagonal = False
        # Indicates if the half-edge is an edge added by the complete closure.
        self.added_by_comp_clsr = False

    def __repr__(self):
        """Represents a half-edge as a tuple (index, node_nr, opposite, next, prior, color, number_proximate)"""
        repr = "(edge_id: {0}\tnode_nr: {1}\topposite_id: {2}\tnext: {3}\tprior: {4}\tcolor: {5}\tinner_edges: {6}\thex: {7}\tadded by clsr: {8})".format(
            id(self), self.node_nr, id(self.opposite), id(self.next), id(self.prior), self.color,
            self.number_proximate_inner_edges, self.is_hexagonal, self.added_by_comp_clsr)
        return repr

    # Adds the fresh half edge to the closure between the prior and the next half-edge
    # def add_to_closure(self, prior_half_edge, next_half_edge, opposite_half_edge, compl_closure):
    #     self.opposite = opposite_half_edge
    #     opposite_half_edge.opposite = self
    #     self.color = prior_half_edge.color
    #     self.node_nr = prior_half_edge.node_nr
    #     self.added_by_comp_clsr = compl_closure
    #     self.prior = prior_half_edge
    #     prior_half_edge.next = self
    #     self.next = next_half_edge
    #     next_half_edge.prior = self

    def add_to_closure(self, opposite_half_edge, compl_closure, new=None):
        self.insert_after(new)
        new.color = self.color
        new.added_by_comp_clsr = compl_closure
        new.opposite = opposite_half_edge
        opposite_half_edge.opposite = new
