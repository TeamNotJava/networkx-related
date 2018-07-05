from framework import BinaryTree
from framework.combinatorial_classes.binary_tree import Leaf
from framework.combinatorial_classes.class_builder import CombinatorialClassBuilder


class WhiteRootedBinaryTreeBuilder(CombinatorialClassBuilder):
    """
    Builds white-rooted binary trees (rules 'R_w', 'R_w_head', 'R_w_as').
    """

    def __init__(self):
        # White rooted trees get odd node numbers.
        self.node_nr = 1

    def u_atom(self):
        return Leaf()

    def product(self, lhs, rhs):
        res = BinaryTree('white')
        res.set_root_node_nr(self.node_nr)
        self.node_nr += 2
        res.add_left_child(lhs)
        res.add_right_child(rhs)
        return res


class BlackRootedBinaryTreeBuilder(CombinatorialClassBuilder):
    """
    Builds black-rooted binary trees (rules 'R_b', 'R_b_head', 'R_b_as').
    """

    def __init__(self):
        # Black rooted trees get even node numbers.
        self.node_nr = 0

    def l_atom(self):
        res = BinaryTree('black')
        res.set_root_node_nr(self.node_nr)
        self.node_nr += 2
        return res

    def u_atom(self):
        return Leaf()

    def product(self, lhs, rhs):
        res = None
        if lhs.is_leaf():
            # rhs is not a leaf.
            assert rhs.is_black_rooted()
            rhs.add_left_child(lhs)
            res = rhs
        elif rhs.is_leaf():
            # lhs is not a leaf.
            res = self.product(rhs, lhs).flip()
        elif lhs.is_white_rooted() and rhs.is_black_rooted():
            # Both are not leaves.
            rhs.add_left_child(lhs)
            res = rhs
        elif rhs.is_white_rooted() and lhs.is_black_rooted():
            res = self.product(rhs, lhs).flip()

        if res is None:
            print()
        assert res is not None
        assert res.get_root_color() is 'black'
        return res
