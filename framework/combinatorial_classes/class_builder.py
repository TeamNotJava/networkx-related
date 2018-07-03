from .generic_classes import *
from .binary_tree import BinaryTree, Leaf


class CombinatorialClassBuilder:
    """
    Interface for objects that build combinatorial classes.
    """

    def zero_atom(self):
        raise NotImplementedError

    def l_atom(self):
        raise NotImplementedError

    def u_atom(self):
        raise NotImplementedError

    def product(self, lhs, rhs):
        raise NotImplementedError

    def set(self, elements):
        raise NotImplementedError


class DefaultCombinatorialClassBuilder(CombinatorialClassBuilder):
    """
    Builds the generic objects.
    """

    def zero_atom(self):
        return ZeroAtomClass()

    def l_atom(self):
        return LAtomClass()

    def u_atom(self):
        return UAtomClass()

    def product(self, lhs, rhs):
        return ProdClass(lhs, rhs)

    def set(self, elements):
        return SetClass(elements)

class BinaryTreeBuilder(CombinatorialClassBuilder):
    """
    Builds bicolored binary trees.
    """
    def __init__(self):
        super(BinaryTreeBuilder).__init__()
        self.numblacknodes = 0
        self.numwhitenodes = 0
        self.numleafs = 0

    def zero_atom(self):
        return ZeroAtomClass()

    def l_atom(self):
        self.numblacknodes += 1
        tree = BinaryTree(Leaf, Leaf,
            color='black',
            numblacknodes=self.numblacknodes,
            numwhitenodes=self.numwhitenodes,
            numleafs=self.numleafs
            )
        return tree

    def u_atom(self):
        #TODO Make sure we are non-root
        self.numleafs += 1
        return Leaf

    def product(self, lhs, rhs):
        print("lhs: {}".format(lhs))
        print("rhs: {}".format(rhs))
        if isinstance(lhs, Leaf) and isinstance(rhs, Leaf):
            self.numwhitenodes += 1
            whitenode = BinaryTree(None, None,
                      color='white',
                      numblacknodes=self.numblacknodes,
                      numwhitenodes=self.numwhitenodes,
                      numleafs=self.numleafs
                      )
            return whitenode
        elif isinstance(lhs, Leaf) and isinstance(rhs, BinaryTree):
            if rhs.get_attribute('color') is 'white':
                #TODO generate blacktree(lhs, rhs)
                pass
            else:
                #TODO generate whitetree(lhs, rhs)
                pass
        elif isinstance(lhs, BinaryTree) and isinstance(rhs, Leaf):
            if lhs.get_attribute('color') is 'white':
                #TODO generate blacktree(lhs, rhs)
                pass
            else:
                #TODO generate whitetree(lhs, rhs)
                pass
        elif isinstance(lhs, BinaryTree) and isinstance(rhs, BinaryTree):
            assert lhs.get_attribute('color') == rhs.get_attribute('color') is 'white'
            if lhs.get_attribute('color') is 'white' and rhs.get_attribute('color') is 'white':
                #TODO generate blacktree(lhs, rhs)
                pass
            elif lhs.get_attribute('color') is 'black' and rhs.get_attribute('color') is 'black':
                #TODO can we get rid of this because auf the assert? The assert can be optimized out.
                #TODO generate whitetree(lhs, rhs)
                pass
            else:
                raise Exception()

    def set(self, elements):
        #TODO
        pass
    