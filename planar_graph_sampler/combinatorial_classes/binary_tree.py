import networkx as nx
from framework.generic_classes import CombinatorialClass

from planar_graph_sampler.combinatorial_classes.halfedge import ClosureHalfEdge


class BinaryTree(ClosureHalfEdge):
    """
    Represents a bicolored binary tree in half-edge representation.
    """

    def __init__(self, root_color):
        super(BinaryTree, self).__init__(self_consistent=True)
        self.color = root_color
        self.black_nodes_count = 0
        self.white_nodes_count = 0
        # The root leaf does not count.
        self.leaves_count = 0
        if root_color == 'black':
            self.black_nodes_count = 1
        elif root_color == 'white':
            self.white_nodes_count = 1

    def flip(self):
        """
        Flips the children.
        :return:
        """
        deg = self.degree()
        assert deg <= 3
        # Both children present:
        if deg == 3:
            self.invert()
        # Otherwise don't do anything.
        return self

    def add_left_child(self, other):
        """
        Adds left child to the root.
        Only works if the tree does not have two children yet.
        :param other:
        :return:
        """
        assert self.degree() < 3
        # Add new half edge to root.
        new = ClosureHalfEdge()
        new.color = self.get_root_color()
        new.node_nr = self.node_nr
        self.insert_after(new)
        if not other.is_leaf():
            assert other.opposite is None
            assert other.color is not self.color
            new.opposite = other
            other.opposite = new
            self.black_nodes_count += other.black_nodes_count
            self.white_nodes_count += other.white_nodes_count
            self.leaves_count += other.leaves_count
        else:
            # Other is a leaf.
            self.leaves_count += 1

    def add_right_child(self, other):
        """
        Adds right child to the root.
        Only works if the tree does not have two children yet.
        :param other:
        :return:
        """
        self.add_left_child(other)
        self.flip()

    def get_root_color(self):
        return self.color

    def is_white_rooted(self):
        return self.get_root_color() is 'white'

    def is_black_rooted(self):
        return self.get_root_color() is 'black'

    def set_root_node_nr(self, node_nr):
        for h in self.incident_half_edges():
            h.node_nr = node_nr

    def is_leaf(self):
        return False

    def get_u_size(self):
        return self.leaves_count

    def get_l_size(self):
        return self.black_nodes_count


class Leaf(CombinatorialClass):
    """
    Represents a leaf of a binary tree.
    Doesn't hold any data.
    """

    def is_leaf(self):
        return True

    def get_u_size(self):
        return 1

    def get_l_size(self):
        return 0
