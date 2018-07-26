import networkx as nx
from framework.generic_classes import CombinatorialClass
from planar_graph_sampler.combinatorial_classes.half_edge_graph import HalfEdgeGraph

from planar_graph_sampler.combinatorial_classes.halfedge import ClosureHalfEdge


class BinaryTree(HalfEdgeGraph):
    """
    Represents a bicolored binary tree in half-edge representation.
    """

    def __init__(self, root_color, root_half_edge=None):
        if root_half_edge is None:
            root_half_edge = ClosureHalfEdge(self_consistent=True)
            root_half_edge.color = root_color
        super().__init__(root_half_edge)
        self.black_nodes_count = 0
        self.white_nodes_count = 0
        # The root leaf does not count.
        self.leaves_count = 0
        if root_color == 'black':
            self.black_nodes_count = 1
        elif root_color == 'white':
            self.white_nodes_count = 1

    def is_consistent(self):
        """
        Checks invariants (for debugging).
        :return:
        """
        super_ok = super().is_consistent()
        node_count_ok = self.number_of_nodes() == self.black_nodes_count + self.white_nodes_count
        leaf_count_ok = self.leaves_count + 1 == self.number_of_nodes() + 2
        is_tree = self.is_tree()
        return super_ok and node_count_ok and leaf_count_ok and is_tree

    def flip(self):
        """
        Flips the children.
        :return:
        """
        deg = self.half_edge.degree()
        assert deg <= 3
        # Both children present:
        if deg == 3:
            self.half_edge.invert()
        # Otherwise don't do anything.
        return self

    def add_left_child(self, other):
        """
        Adds left child to the root.
        Only works if the tree does not have two children yet and the child root has the correct color.
        :param other:
        :return:
        """
        assert self.half_edge.degree() < 3
        # Add new half edge to root.
        new = ClosureHalfEdge()
        new.color = self.get_root_color()
        new.node_nr = self.half_edge.node_nr
        self.half_edge.insert_after(new)
        if not other.is_leaf():
            assert other.get_half_edge().opposite is None
            assert other.get_half_edge().color is not self.half_edge.color
            new.opposite = other.get_half_edge()
            other.get_half_edge().opposite = new
            self.black_nodes_count += other.black_nodes_count
            self.white_nodes_count += other.white_nodes_count
            self.leaves_count += other.leaves_count
        else:
            # Other is a leaf.
            self.leaves_count += 1

    def add_right_child(self, other):
        """
        Adds right child to the root.
        Only works if the tree does not have two children yet and the child root has the correct color.
        :param other:
        :return:
        """
        self.add_left_child(other)
        self.flip()

    def get_root_color(self):
        return self.half_edge.color

    def is_white_rooted(self):
        return self.get_root_color() is 'white'

    def is_black_rooted(self):
        return self.get_root_color() is 'black'

    def set_root_node_nr(self, node_nr):
        for h in self.half_edge.incident_half_edges():
            h.node_nr = node_nr

    def is_leaf(self):
        return False

    def u_size(self):
        return self.leaves_count

    def l_size(self):
        return self.black_nodes_count

    def to_networkx_graph(self, include_unpaired=True):
        # Get dict of nodes.
        nodes = self.half_edge.get_node_list()
        # Include the leaves as well.
        G = super().to_networkx_graph(include_unpaired=include_unpaired)
        for v in G:
            if v not in nodes:
                # v is a leaf.
                G.nodes[v]['color'] = '#229922'
            else:
                col = nodes[v][0].color
                G.nodes[v]['color'] = '#333333' if col is 'black' else '#999999' if col is 'white' else '#990000'
        return G


class Leaf(CombinatorialClass):
    """
    Represents a leaf of a binary tree.
    Doesn't hold any data.
    """

    def is_leaf(self):
        return True

    def u_size(self):
        return 1

    def l_size(self):
        return 0
