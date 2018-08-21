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
from planar_graph_sampler.combinatorial_classes.half_edge_graph import HalfEdgeGraph

from planar_graph_sampler.combinatorial_classes.halfedge import ClosureHalfEdge


class BinaryTree(HalfEdgeGraph):
    """
    Represents a bicolored binary tree in half-edge representation.

    Parameters
    ----------
    root_color: str
    root_half_edge: HalfEdge, optional (default=None)
    """

    __slots__ = 'black_nodes_count', 'white_nodes_count', 'leaves_count'

    def __init__(self, root_color, root_half_edge=None):
        if root_half_edge is None:
            root_half_edge = ClosureHalfEdge(self_consistent=True)
            root_half_edge.color = root_color
        super(BinaryTree, self).__init__(root_half_edge)
        self.black_nodes_count = 0
        self.white_nodes_count = 0
        # There is a leaf on the root pointing 'upwards'.
        self.leaves_count = 0
        if root_color == 'black':
            self.black_nodes_count = 1
        elif root_color == 'white':
            self.white_nodes_count = 1

    @property
    def is_consistent(self):
        """Checks invariants (for debugging)."""
        super_ok = super(BinaryTree, self).is_consistent
        node_count_ok = self.number_of_nodes == self.black_nodes_count + self.white_nodes_count
        leaf_count_ok = True  # self._leaves_count == self.number_of_nodes + 2
        is_tree = self.is_tree
        return super_ok and node_count_ok and leaf_count_ok and is_tree

    def flip(self):
        """Flips the children."""
        # TODO needed?
        self.half_edge.invert()
        # Otherwise don't do anything.
        return self

    def add_left_child(self, other):
        """Adds left child to the root.

        Only works if the tree does not have two children yet and the child root has the correct color.
        """
        # assert self._half_edge.degree() < 3
        # Add new half edge to root.
        new = ClosureHalfEdge()
        new.color = self.half_edge.color
        new.node_nr = self.half_edge.node_nr
        self.half_edge.insert_after(new)
        if not other.is_leaf:
            # assert other.half_edge.opposite is None
            # assert other.half_edge.color is not self._half_edge.color
            new.opposite = other.half_edge
            other.half_edge.opposite = new
            self.black_nodes_count += other.black_nodes_count
            self.white_nodes_count += other.white_nodes_count
            self.leaves_count += other.leaves_count
        else:
            # Other is a leaf.
            self.leaves_count += 1

    def add_right_child(self, other):
        """Adds right child to the root.

        Only works if the tree does not have two children yet and the child root has the correct color.
        """
        new = ClosureHalfEdge()
        new.color = self.half_edge.color
        new.node_nr = self.half_edge.node_nr
        self.half_edge.insert_before(new)
        if not other.is_leaf:
            new.opposite = other.half_edge
            other.half_edge.opposite = new
            self.black_nodes_count += other.black_nodes_count
            self.white_nodes_count += other.white_nodes_count
            self.leaves_count += other.leaves_count
        else:
            # Other is a leaf.
            self.leaves_count += 1

    @property
    def root_color(self):
        return self.half_edge.color

    @property
    def is_white_rooted(self):
        return self.root_color is 'white'

    @property
    def is_black_rooted(self):
        return self.root_color is 'black'

    # @property
    # def black_nodes_count(self):
    #     return self._black_nodes_count
    #
    # @property
    # def white_nodes_count(self):
    #     return self._white_nodes_count
    #
    # @property
    # def leaves_count(self):
    #     return self._leaves_count

    def set_root_node_nr(self, node_nr):
        for h in self.half_edge.incident():
            h.node_nr = node_nr

    @property
    def is_leaf(self):
        return False

    # CombinatorialClass interface.

    @property
    def u_size(self):
        return self.leaves_count

    @property
    def l_size(self):
        return self.black_nodes_count

    def __str__(self):
        return "Binary tree (black: {}, white: {}, leaves: {})" \
            .format(self.black_nodes_count, self.white_nodes_count, self.leaves_count)

    # Networkx related functionality.

    def to_networkx_graph(self, include_unpaired=True):
        # Get dict of nodes.
        nodes = self.half_edge.node_dict()
        # Include the leaves as well.
        G = super(BinaryTree, self).to_networkx_graph(include_unpaired=include_unpaired)
        for v in G:
            if v not in nodes:
                # v is a leaf.
                G.nodes[v]['color'] = '#229922'
            else:
                col = nodes[v][0].color
                G.nodes[v]['color'] = '#333333' if col is 'black' else '#999999' if col is 'white' else '#990000'
        return G

    def plot(self, **kwargs):
        """Plots the binary tree.

        Parameters
        ----------
        draw_leaves: bool
        """
        draw_leaves = False
        if 'draw_leaves' in kwargs:
            draw_leaves = kwargs['draw_leaves']
        kwargs['G'] = self.to_networkx_graph(include_unpaired=draw_leaves)
        super(BinaryTree, self).plot(**kwargs)


class Leaf(CombinatorialClass):
    """
    Represents a leaf of a binary tree. Doesn't hold any data.
    """

    @property
    def is_leaf(self):
        return True

    @property
    def u_size(self):
        return 1

    @property
    def l_size(self):
        return 0
