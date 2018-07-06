import networkx as nx
from framework.generic_classes import CombinatorialClass

from planar_graph_sampler.bijections.halfedge import HalfEdge


class BinaryTree(CombinatorialClass):
    """
    Represents a bicolored binary tree in half-edge representation.
    """

    def __init__(self, root_color):
        self.root = HalfEdge(self_consistent=True)
        self.root.color = root_color

        self.black_nodes_count = 0
        self.white_nodes_count = 0
        # The root leaf does not count.
        self.leaves_count = 0
        if root_color == 'black':
            self.black_nodes_count = 1
        elif root_color == 'white':
            self.white_nodes_count = 1

    def get_root(self):
        return self.root

    # Flips the children
    def flip(self):
        deg = self.root.degree()
        assert deg <= 3
        # Both children present:
        if deg == 3:
            self.root.invert()
        # Otherwise don't do anything.
        return self

    def add_left_child(self, other):
        assert self.root.degree() < 3
        # Add new half edge to root.
        new = HalfEdge()
        new.color = self.get_root_color()
        new.node_nr = self.root.node_nr
        self.root.insert_after(new)
        if not other.is_leaf():
            other_root = other.get_root()
            assert other_root.opposite is None
            assert other_root.color is not self.root.color
            new.opposite = other_root
            other_root.opposite = new
            self.black_nodes_count += other.black_nodes_count
            self.white_nodes_count += other.white_nodes_count
            self.leaves_count += other.leaves_count
        else:
            # other is leaf
            self.leaves_count += 1

    def add_right_child(self, other):
        self.add_left_child(other)
        self.flip()

    def get_root_color(self):
        return self.root.color

    def is_white_rooted(self):
        return self.get_root_color() is 'white'

    def is_black_rooted(self):
        return self.get_root_color() is 'black'

    def set_root_node_nr(self, node_nr):
        for h in self.root.incident_half_edges():
            h.node_nr = node_nr

    def is_leaf(self):
        return False

    def get_u_size(self):
        return self.leaves_count

    def get_l_size(self):
        return self.black_nodes_count

    def to_networkx_graph(self):
        # TODO does not handle graphs with just one node correctly
        res = self.root.to_networkx_graph()
        # TODO this assertion fails since the global node nr counter.
        print(nx.is_tree(res))
        print(nx.cycle_basis(res))
        return res

    def plot(self):
        G = self.to_networkx_graph()
        colors = []
        for x in nx.get_node_attributes(G, 'color').values():
            if x is 'black':
                colors.append('#333333')
            elif x is 'white':
                colors.append('#999999')
        nx.draw(G, with_labels=True, node_color=colors)


class Leaf(CombinatorialClass):

    def is_leaf(self):
        return True

    def get_u_size(self):
        return 1

    def get_l_size(self):
        return 0
