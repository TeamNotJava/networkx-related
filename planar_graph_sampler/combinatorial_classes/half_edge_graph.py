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

import random

import networkx as nx

from framework.generic_classes import CombinatorialClass

from planar_graph_sampler.grammar.grammar_utils import Counter
from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge


class HalfEdgeGraph(CombinatorialClass):
    """
    Base class for all different flavours of graphs that show up in the decomposition:
    Bicolored binary trees, bicolored dissections, 3-connected maps, networks, 2-connected maps, 1-connected maps.

    Combinatorically, this simply represents the class of undirected graphs with labelled vertices and unlabelled edges,
    i.e. the l-size is the number of vertices and the u-size is the number of edges.

    Parameters
    ----------
    half_edge: HalfEdge
        A half-edge in the graph.
    """

    __slots__ = 'half_edge'

    def __init__(self, half_edge):
        self.half_edge = half_edge

    # @property
    # def half_edge(self):
    #     """Returns the underlying half-edge for direct manipulation."""
    #     return self._half_edge

    @property
    def number_of_nodes(self):
        """Number of nodes in the graph."""
        return self.half_edge.get_number_of_nodes()

    @property
    def number_of_edges(self):
        """Number of edges in the graph."""
        return self.half_edge.get_number_of_edges()

    @property
    def number_of_half_edges(self):
        """Number of half-edges in the graph."""
        return len(self.half_edge.get_all_half_edges(include_unpaired=True, include_opp=True))

    def random_node_half_edge(self):
        """Returns a half-edge incident to a node chosen uniformly at random.

        This is not the same as choosing a random half-edge!
        """
        nodes = self.half_edge.node_dict()
        random_node = random.choice(list(nodes.keys()))
        return nodes[random_node][0]

    @property
    def is_consistent(self):
        """Checks invariants (for debugging)."""
        return self._check_node_nr() #and self._check_no_double_edges()
        # TODO make more checks here

    def _check_node_nr(self, visited=None):
        """Checks node_nr consistency."""
        if visited is None:
            visited = set()
        curr = self.half_edge
        visited.add(curr)
        incident = curr.incident_half_edges()
        if len(set([he.node_nr for he in incident])) > 1:
            return False
        for he in incident:
            if he.opposite is not None and he.opposite not in visited:
                if not HalfEdgeGraph(he.opposite)._check_node_nr(visited):
                    return False
        return True

    def _check_no_double_edges(self):
        # TODO
        return True

    # CombinatorialClass interface.

    @property
    def u_size(self):
        return self.number_of_edges

    @property
    def l_size(self):
        return self.number_of_nodes

    def u_atoms(self):
        raise NotImplementedError

    def l_atoms(self):
        raise NotImplementedError

    def replace_u_atoms(self, sampler, x, y, exceptions=None):
        """Maybe it's not so stupid to actually implement this here ... (same for l_subs)"""
        raise NotImplementedError

    def replace_l_atoms(self, sampler, x, y, exceptions=None):
        raise NotImplementedError

    def __str__(self):
        return "HalfEdgeGraph (Nodes: {}, Edges: {})".format(self.number_of_nodes, self.number_of_edges)

    # Networkx related functionality.

    @property
    def is_tree(self):
        return nx.is_tree(self.to_networkx_graph())

    @property
    def is_planar(self):
        return nx.check_planarity(self.to_networkx_graph())

    def is_connected(self, k=1):
        """
        Checks if the graph is k-connected.

        Parameters
        ----------
        k: int, optional (default=1)
            Check for k-connectivity.

        Returns
        -------
        bool
            True iff the graph is k-connected.
        """
        # TODO Check if this works the way intended.
        connectivity_dict = nx.k_components(self.to_networkx_graph())
        return len(connectivity_dict[k][0]) == self.number_of_nodes

    def to_planar_embedding(self):
        """Converts to nx.PlanarEmbedding.

        Returns
        -------
        PlanarEmbedding
        """
        nodes = self.half_edge.node_dict()
        embedding = nx.PlanarEmbedding()
        # Loop over all nodes in the graph (node_nr).
        for node in nodes:
            embedding.add_node(node)
            # Loop over all half-edges incident the the current node, in ccw order around the node.
            reference_neighbour = None
            for he in nodes[node]:
                if he.opposite is None:
                    continue
                embedding.add_half_edge_ccw(node, he.opposite.node_nr, reference_neighbour)
                reference_neighbour = he.opposite.node_nr
        return embedding

    def to_networkx_graph(self, include_unpaired=False):
        """Transforms the graph into a networkx graph.

        Parameters
        ----------
        include_unpaired: bool, optional (default=False)
            Includes half-edges that do not have an opposite.
            In this case, a new node is created and connected to the unpaired half-edge.
        """
        # Get the counter in case we have to create nodes for unpaired half-edges.
        counter = Counter()
        # If this graph consists of only one unpaired half-edge we interpret this as the one-node graph.
        if self.half_edge.is_trivial:
            G = nx.Graph()
            if self.half_edge.node_nr is None:
                self.half_edge.node_nr = next(counter)
            G.add_node(self.half_edge.node_nr)
            return G
        # Get all edges (one half-edge per edge).
        half_edges = self.half_edge.get_all_half_edges(include_opp=False, include_unpaired=include_unpaired)
        G = nx.Graph()
        while len(half_edges) > 0:
            half_edge = half_edges.pop()
            if half_edge.opposite is not None:
                G.add_edge(half_edge.node_nr, half_edge.opposite.node_nr)
            else:
                G.add_edge(half_edge.node_nr, next(counter))
        # G = nx.relabel.convert_node_labels_to_integers(G)
        return G

    def plot(self, **kwargs):
        """Plots the graph.

        Parameters
        ----------
        G: networkx.Graph


        """
        G = None
        with_labels = False
        use_planar_drawer = False
        node_size = 100
        if 'G' in kwargs:
            G = kwargs['G']
        if 'with_labels' in kwargs:
            with_labels = kwargs['with_labels']
        if 'use_planar_drawer' in kwargs:
            use_planar_drawer = kwargs['use_planar_drawer']
        if 'node_size' in kwargs:
            node_size = kwargs['node_size']

        if G is None:
            G = self.to_networkx_graph()
        # Generate planar embedding or use default algorithm.
        pos = None
        if use_planar_drawer:
            emb = self.to_planar_embedding()
            pos = nx.combinatorial_embedding_to_pos(emb, fully_triangulate=False)
        # Take color attributes on the nodes into account.
        colors = nx.get_node_attributes(G, 'color').values()
        if len(colors) == G.number_of_nodes():
            nx.draw(G, pos=pos, with_labels=with_labels, node_color=list(colors), node_size=node_size)
        else:
            nx.draw(G, pos=pos, with_labels=with_labels, node_size=node_size)


def color_scale(hex_str, factor):
    """Scales a hex string by ``factor``. Returns scaled hex string."""
    hex_str = hex_str.strip('#')
    if factor < 0 or len(hex_str) != 6:
        return hex_str
    r, g, b = int(hex_str[:2], 16), int(hex_str[2:4], 16), int(hex_str[4:], 16)

    def clamp(val, min=0, max=255):
        if val < min:
            return min
        if val > max:
            return max
        return int(val)

    r = clamp(r * factor)
    g = clamp(g * factor)
    b = clamp(b * factor)

    return "#%02x%02x%02x" % (r, g, b)
