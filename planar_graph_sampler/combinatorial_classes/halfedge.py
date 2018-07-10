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
    Generic class for half edge representation of a combinatorial planar embedding.
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

    def get_l_size(self):
        return self.get_number_of_nodes()

    def get_u_size(self):
        return self.get_number_of_edges()


    def insert_after(self, new=None):
        """
        Inserts a half that follows this half edge in ccw order.
        :param new:
        :return:
        """
        if new is None:
            new = HalfEdge()
        new.node_nr = self.node_nr
        old_next = self.next
        self.next = new
        new.prior = self
        new.next = old_next
        old_next.prior = new

    def insert_before(self, new=None):
        """

        :param new:
        :return:
        """
        if new is None:
            new = HalfEdge()
        new.node_nr = self.node_nr
        old_prior = self.prior
        self.prior = new
        new.next = self
        new.prior = old_prior
        old_prior.next = new

    def invert(self):
        """
        Inverts order.
        :return:
        """
        for h in self.incident_half_edges():
            # Swap pointers.
            h.next, h.prior = h.prior, h.next

    def degree(self):
        """
        Number of outgoing half edges of the incident node.
        :return:
        """
        return len(self.incident_half_edges())

    def incident_half_edges(self):
        """

        :return:
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
        """
        Represents a half-edge as a tuple (index, node_nr, opposite, next, prior)
        :return:
        """
        repr = "(edge_id: {0}\tnode_nr: {1}\topposite_id: {2}\tnext: {3}\tprior: {4})".format(
            id(self), self.node_nr, id(self.opposite), id(self.next), id(self.prior))
        return repr

    def list_half_edges(self, edge_list=None):
        """
        Returns a list with half-edges.
        :param edge_list:
        :return:
        """
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

    def get_all_half_edges(self, edge_set=None, include_opp=True, include_unpaired=True):
        """

        :param edge_set:
        :param include_opp:
        :param include_unpaired:
        :return:
        """
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
        """
        Returns the number of nodes in the graph.
        :return:
        """
        edge_list = self.get_all_half_edges()
        nodes = set()
        for edge in edge_list:
            if edge.node_nr not in nodes:
                nodes.add(edge.node_nr)
        return len(nodes)

    def get_number_of_edges(self):
        """
        Returns the number of edges (NOT half-edges!) in the graph.
        :return:
        """
        # TODO implement without altering the list while iteration
        #edge_list = self.list_half_edges([])
        #num_edges = 0
        #for edge in edge_list:
        #    # Check if half-edge is a 'real' edge.
        #    if edge.opposite is not None:
        #        num_edges += 1
        #        # Don't count twice.
        #        edge_list.remove(edge.opposite)
        #return num_edges
        return len(self.get_all_half_edges(include_opp=False, include_unpaired=False))

    def get_node_list(self):
        """
        Returns a dictionary of nodes. The key is node number and the value is a list of
        half-edges belonging to the node number.
        :return:
        """
        edge_list = self.list_half_edges([])
        node_list = {}
        for edge in edge_list:
            if edge.node_nr in node_list:
                half_edges = node_list[edge.node_nr]
                half_edges.append(edge)
                node_list[edge.node_nr] = half_edges
            else:
                node_list[edge.node_nr] = [edge]
        return node_list



    def to_networkx_graph(self):
        """
        Transforms a list of planar map half-edged into a networkx graph.
        :return:
        """
        half_edge_list = self.list_half_edges([])

        # Remove all unpaired half-edges
        half_edge_list = [x for x in half_edge_list if not x.opposite is None]
        G = nx.Graph()
        while len(half_edge_list) > 0:
            half_edge = half_edge_list.pop()
            G.add_edge(half_edge.node_nr, half_edge.opposite.node_nr)
        return G

    def plot(self):
        """

        :param colors:
        :return:
        """
        G = self.to_networkx_graph()
        nx.draw(G, with_labels=True)


class ClosureHalfEdge(HalfEdge):
    """
    Half-edges with additional attributes needed in the closure.
    """

    def __init__(self, self_consistent=False):
        super().__init__(self_consistent)
        # Number of inner edges following after the stem
        self.number_proximate_inner_edges = 0
        # Color that indicates what color the incident node has (0 - black, 1 -white)
        self.color = None
        # Indicates if the half-edge belongs to the hexagon
        self.is_hexagonal = False
        # Indicates if the half-edge is an edge added by the complete closure
        self.added_by_comp_clsr = False
    
    def __repr__(self):
        """
        Represents a half-edge as a tuple (index, node_nr, opposite, next, prior, color, number_proximate)
        :return:
        """
        repr = "(edge_id: {0}\tnode_nr: {1}\topposite_id: {2}\tnext: {3}\tprior: {4}\tcolor: {5}\tinner_edges: {6}\thex: {7}\tadded by clsr: {8})".format(
            id(self), self.node_nr, id(self.opposite), id(self.next), id(self.prior), self.color,
            self.number_proximate_inner_edges, self.is_hexagonal, self.added_by_comp_clsr)
        return repr

    # TODO Get rid of this basically duplicated code from superclass.

    def to_networkx_graph(self):
        """
        Transforms a list of planar map half-edged into a networkx graph.
        :return:
        """
        half_edge_list = self.list_half_edges([])
        # Remove all unpaired half-edges
        half_edge_list = [x for x in half_edge_list if not x.opposite is None]
        G = nx.Graph()
        while len(half_edge_list) > 0:
            half_edge = half_edge_list.pop()
            G.add_edge(half_edge.node_nr, half_edge.opposite.node_nr)
            G.nodes[half_edge.node_nr]['color'] = half_edge.color
            G.nodes[half_edge.node_nr]['is_hexagonal'] = half_edge.is_hexagonal
        return G

    def plot(self):
        """
        # TODO plot hexagonal nodes in different color or similar.
        :return:
        """
        G = self.to_networkx_graph()
        colors = []
        for x in nx.get_node_attributes(G, 'color').values():
            if x is 'black':
                colors.append('#333333')
            if x is 'white':
                colors.append('#999999')
        nx.draw(G, with_labels=True, node_color=colors)
    
    # Adds the fresh half edge to the closure between the prior and the next half-edge
    def add_to_closure(self, prior_half_edge, next_half_edge, opposite_half_edge):
        self.opposite = opposite_half_edge
        opposite_half_edge.opposite = self
        self.color = prior_half_edge.color
        self.node_nr = prior_half_edge.node_nr
        self.added_by_comp_clsr = True
        self.prior = prior_half_edge
        prior_half_edge.next = self
        self.next = next_half_edge
        next_half_edge.prior = self
