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
import sys

class HalfEdge:
    """
    Generic class for half edge representation of a combinatorial planar embedding.
    # TODO Maybe create a subclass for the binary tree specific stuff (color, is_hexagonal, ...)
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
        # Number of inner edges following after the stem
        self.number_proximate_inner_edges = 0
        # Color that indicates what color the incident node has (0 - black, 1 -white)
        self.color = None
        # Node the half-edge is  assigned to
        self.node_nr = -1
        # Indicates if the half-edge belongs to the hexagon
        self.is_hexagonal = False
        # Indicates if the half-edge is an edge added by the complete closure
        self.added_by_comp_clsr = False

    # Inserts a half that follows this half edge in ccw order.
    def insert_after(self, new=None):
        if new is None:
            new = HalfEdge()
        old_next = self.next
        self.next = new
        new.prior = self
        new.next = old_next
        old_next.prior = new

    def insert_before(self, new=None):
        # TODO check correctness
        if new is None:
            new = HalfEdge()
        new = HalfEdge()
        old_prior = self.prior
        self.prior = new
        new.next = self
        new.prior = old_prior
        old_prior.next = new

    # Inverts order.
    def invert(self):
        # TODO check correctness
        for h in self.incident_half_edges():
            # Swap pointers.
            h.next, h.prior = h.prior, h.next

    # Number of outgoing half edges of the incident node.
    def degree(self):
        return len(self.incident_half_edges())

    def incident_half_edges(self):
        res = [self]
        curr = self
        while curr.next is not self:
            res += [curr.next]
            curr = curr.next
        return res

    # Represents a half-edge as a tuple (index, node_nr, opposite, next, prior, color, number_proximate)
    def __repr__(self):
        repr = '('
        repr = repr + str(id(self))
        repr = repr + ", \t"

        repr = repr + str(id(self))
        repr = repr + ", \t"

        repr = repr + str(self.node_nr)
        repr = repr + ", \t"

        if self.opposite is None:
            repr = repr + "None"
        else:
            repr = repr + str(id(self.opposite))
        repr = repr + ", \t"

        if self.next is None:
            repr = repr + "None"
        else:
            repr = repr + str(id(self.next))
        repr = repr + ", \t"

        if self.prior is None:
            repr = repr + "None"
        else:
            repr = repr + str(id(self.prior))
        if self.color is None:
            repr = repr + ", \tNone"
        else:
            repr = repr + ", \t" + self.color
        repr = repr + ", "
        repr = repr + str(self.number_proximate_inner_edges)
        if not self.is_hexagonal:
            repr = repr + ", \tNOT hexagonal"
        else:
            repr = repr + ", \thexagonal"

        if not self.added_by_comp_clsr:
            repr = repr + ", \tNOT added by clsr"
        else:
            repr = repr + ", \tadded by clsr"

        repr = repr + ')'

        return repr

    # Returns a list with half-edges
    def list_half_edges(self, edge_list):
        edge_list.append(self)
        current_half_edge = self
        assert (current_half_edge is not None)
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

    # Returns the half_edge with the highest index in the graph
    def get_max_half_edge(self):
        edge_list = self.list_half_edges([])
        max_id = -1
        max_half_edge = None
        for x in edge_list:
            if id(x) > max_id:
                max_id = id(x)
                max_half_edge = x
        return max_half_edge

    # Returns the half-edge with the smallest index in the graph
    def get_min_half_edge(self):
        half_edge_list = self.list_half_edges([])
        min_half_edge = None
        for edge in half_edge_list:
            if min_half_edge is None and edge.opposite is None:
                min_half_edge = edge
            elif min_half_edge is not None and edge.opposite is None and id(edge) < id(min_half_edge):
                min_half_edge = edge
        return min_half_edge

    # Returns the highest node number of the graph
    def get_max_node_nr(self):
        edge_list = self.list_half_edges([])
        max_node = -1
        max_edge = None
        for x in edge_list:
            if x.node_nr > max_node:
                max_node = x.node_nr
                max_edge = x
        return max_edge

    # Returns the half_edge with the smallest node number
    def get_min_node_nr(self):
        edge_list = self.list_half_edges([])
        min_node = float('inf')
        min_edge = None
        for x in edge_list:
            if x.node_nr < min_node:
                min_node = x.node_nr
                min_edge = x
        return min_edge

    # Returns the highest index in a graph
    def get_max_half_edge_index(self):
        return self.get_max_half_edge().index

    # Returns the smallest index in a graph
    def get_min_half_edge_index(self):
        return self.get_min_half_edge().index

    # Returns the number of nodes in the graph
    def get_number_of_nodes(self):
        edge_list = self.list_half_edges([])
        nodes = []
        for edge in edge_list:
            if edge.node_nr not in nodes:
                nodes.append(edge.node_nr)
        return len(nodes)

    # Returns the number of edges (NOT half-edges!) in the graph
    def get_number_of_edges(self):
        edge_list = self.list_half_edges([])
        num_edges = 0
        for edge in edge_list:
            if edge.opposite is not None:
                num_edges += 1
                edge_list.remove(edge.opposite)
        return num_edges

    # Returns a dictionary of nodes. The key is node number and the value is a list of
    # half-edges belonging to the node number
    def get_node_list(self):
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

    # Adds two new half_edges, one on the side of the current half-edge (left half-edge)
    # and the other on the side of the right half-edge. The right half-edge is
    # needed to get the correct node numbers, colors, etc. for the new opposite
    # half-edge
    #:param rigth_half_edge: next half-edge to the new half-e
    def add_new_edge(self, rigth_half_edge):
        new_half_edge_1 = HalfEdge()
        new_half_edge_2 = HalfEdge()
        index = self.get_max_half_edge().index + 1

        new_half_edge_1.opposite = new_half_edge_2
        new_half_edge_2.opposite = new_half_edge_1

        # Setup the first new half edge
        new_half_edge_1.color = self.color
        new_half_edge_1.node_nr = self.node_nr
        new_half_edge_1.index = index
        new_half_edge_1.next = self.next
        new_half_edge_1.prior = self
        self.next.prior = new_half_edge_1
        self.next = new_half_edge_1

        # Setup the second new half edge
        new_half_edge_2.color = rigth_half_edge.color
        new_half_edge_2.node_nr = rigth_half_edge.node_nr
        new_half_edge_2.index = index
        new_half_edge_2.next = rigth_half_edge.next
        new_half_edge_2.prior = rigth_half_edge
        rigth_half_edge.next.prior = new_half_edge_2
        rigth_half_edge.next = new_half_edge_2

    # Transforms a list of planar map half-edged into a networkx graph
    def to_networkx_graph(self):
        half_edge_list = self.list_half_edges([])

        # Remove all unpaired half-edges
        half_edge_list = [x for x in half_edge_list if not x.opposite is None]
        G = nx.Graph()
        while len(half_edge_list) > 0:
            half_edge = half_edge_list.pop()
            G.add_edge(half_edge.node_nr, half_edge.opposite.node_nr)
            G.nodes[half_edge.node_nr]['color'] = half_edge.color
            # TODO this sometimes caused adjacent nodes with the same color. why?
            # half_edge_list.remove(half_edge.opposite)
        return G
