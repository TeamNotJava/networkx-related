from framework.decomposition_grammar import Alias
from framework.samplers.generic_samplers import *
from .decomposition_grammar import DecompositionGrammar

L = LAtom()
U = UAtom()

K_dy = Alias('K_dy')
R_b_as = Alias('R_b_as')
R_w_as = Alias('R_w_as')
R_b_head = Alias('R_b_head')
R_w_head = Alias('R_w_head')
R_b = Alias('R_b')
R_w = Alias('R_w')

class BinaryTree():
    _id = 0

    def __init__(self, left, right, **kwargs):
        self.left = left
        self.right = right
        self.attributes = kwargs
        self._id = BinaryTree._id
        BinaryTree._id += 1

    def get_attribute(self, key):
        return self.attributes[key]

    def get_attributes(self):
        return self.attributes

    def __repr__(self):
        repr = '['
        if self.left is None:
            repr += '0'
        else:
            repr += str(self.left)

        if 'color' in self.attributes:
            if self.attributes['color'] is 'white':
                repr += 'w'
            if self.attributes['color'] is 'black':
                repr += 'b'
                
        if self.right is None:
            repr += '0'
        else:
            repr += str(self.right)
        repr += ']'
        return repr

    
    def pretty(self, indent='', direction='updown'):
        label = "{0} ({1})".format(self._id, self.get_attribute('color'))
        if type(self.right) is BinaryTree:
            next_indent = '{0}{1}{2}'.format(indent, ' ' if 'up' in direction else '│', ' ' * len(label))
            self.right.pretty(next_indent, direction='up')
        else:
            print('{0}{1}{2}┌-'.format(indent, ' ' if 'up' in direction else '│', ' ' * len(label)))

        if direction == 'up': start_shape = '┌'
        elif direction == 'down': start_shape = '└'
        elif direction == 'updown': start_shape = ' '
        else: start_shape = '├'


        print('{0}{1}{2}{3}'.format(indent, start_shape, label, '┤'))

        if type(self.left) is BinaryTree:
            next_indent = '{0}{1}{2}'.format(indent, ' ' if 'down' in direction else '│', ' ' * len(label))
            self.left.pretty(next_indent, direction='down')
        else:
            print('{0}{1}{2}└-'.format(indent, ' ' if 'down' in direction else '│', ' ' * len(label)))



def decomp_to_binary_tree_b_3(decomp):
    print("b_3")
    print(type(decomp.first))
    print(type(decomp.second))
    print(decomp)
    numblacknodes = 1
    numwhitenodes = 0
    numtotal = 1
    if type(decomp.first.first) is UAtomClass:
        left = None
    else:
        left = decomp.first.first
        if left:
            numblacknodes += left.get_attribute('numblacknodes')
            numwhitenodes += left.get_attribute('numwhitenodes')
            numtotal += left.get_attribute('numtotal')
    
    if type(decomp.second) is UAtomClass:
        right = None
    else:
        right = decomp.second
        if right:
            numblacknodes += right.get_attribute('numblacknodes')
            numwhitenodes += right.get_attribute('numwhitenodes')
            numtotal += right.get_attribute('numtotal')

    tree = BinaryTree(left, right, 
        color='black', 
        numtotal=numtotal, 
        numblacknodes=numblacknodes, 
        numwhitenodes=numwhitenodes
    )
    print(tree)
    return tree

def decomp_to_binary_tree_b_4(decomp):
    print("b_4")
    print(type(decomp.first))
    print(type(decomp.second))
    print(decomp)

    numblacknodes = 1
    numwhitenodes = 0
    numtotal = 1

    #(((X,L),U),U)
    if type(decomp.second) is UAtomClass and type(decomp.first.second) is UAtomClass:
        print("#(((X,L),U),U)")
        left = decomp.first.first.first
        if left:
            numblacknodes += left.get_attribute('numblacknodes')
            numwhitenodes += left.get_attribute('numwhitenodes')
            numtotal += left.get_attribute('numtotal')

        numwhitenodes += 1
        numtotal += 1
        right = BinaryTree(None, None, color='white')
            
    #(((U,U),L),X)
    elif type(decomp.first.first) is ProdClass and type(decomp.first.first.first) is UAtomClass and type(decomp.first.first.second) is UAtomClass:
        print("#(((U,U),L),X)")
        numwhitenodes += 1
        numtotal += 1
        left = BinaryTree(None, None, color='white')

        right = decomp.second
        if right:
            numblacknodes += right.get_attribute('numblacknodes')
            numwhitenodes += right.get_attribute('numwhitenodes')
            numtotal += right.get_attribute('numtotal')
    #((X,L),X)
    else:
        print("#((X,L),X)")
        print(decomp)
        right = decomp.second
        if right:
            numblacknodes += right.get_attribute('numblacknodes')
            numwhitenodes += right.get_attribute('numwhitenodes')
            numtotal += right.get_attribute('numtotal')

        left = decomp.first.first
        if left:
            numblacknodes += left.get_attribute('numblacknodes')
            numwhitenodes += left.get_attribute('numwhitenodes')
            numtotal += left.get_attribute('numtotal')
        

    tree = BinaryTree(left, right,
        color='black', 
        numtotal=numtotal, 
        numblacknodes=numblacknodes, 
        numwhitenodes=numwhitenodes
    )
    print(tree)
    return tree
    
def decomp_to_binary_tree_w_2(decomp):
    print("w_2")
    print(type(decomp.first))
    print(type(decomp.second))
    print(decomp)

    numblacknodes = 0
    numwhitenodes = 1
    numtotal = 1

    if type(decomp.first) is UAtomClass:
        left = None
    else:
        left = decomp.first
        if left:
            numblacknodes += left.get_attribute('numblacknodes')
            numwhitenodes += left.get_attribute('numwhitenodes')
            numtotal += left.get_attribute('numtotal')

    if type(decomp.second) is UAtomClass:
        right = None
    else:
        right = decomp.second
        if right:
            numblacknodes += right.get_attribute('numblacknodes')
            numwhitenodes += right.get_attribute('numwhitenodes')
            numtotal += right.get_attribute('numtotal')
    tree = BinaryTree(left, right, 
        color='white',
        numtotal=numtotal, 
        numblacknodes=numblacknodes, 
        numwhitenodes=numwhitenodes
    )
    print(tree)
    return tree

def decomp_to_binary_tree_w_1_2(decomp):
    """Creates either a white rooted tree with a left or a right None subtree
    or returns a None
    """
    if type(decomp) is UAtomClass:
        return None

    print("w_1_2")
    print(type(decomp.first))
    print(type(decomp.second))
    print(decomp)
    numblacknodes = 1
    numwhitenodes = 0
    numtotal = 1
    if type(decomp.first) is UAtomClass:
        left = None
    else:
        left = decomp.first
        if left:
            numblacknodes += left.get_attribute('numblacknodes')
            numwhitenodes += left.get_attribute('numwhitenodes')
            numtotal += left.get_attribute('numtotal')

    if type(decomp.second) is UAtomClass:
        right = None
    else:
        right = decomp.second
        if right:
            numblacknodes += right.get_attribute('numblacknodes')
            numwhitenodes += right.get_attribute('numwhitenodes')
            numtotal += right.get_attribute('numtotal')

    tree = BinaryTree(left, right, 
        color='white',
        numtotal=numtotal, 
        numblacknodes=numblacknodes, 
        numwhitenodes=numwhitenodes
    )
    print(tree)
    return tree

binary_tree_grammar = DecompositionGrammar()
binary_tree_grammar.add_rules({
    'K_dy': R_b_as + R_w_as,
    'R_b_as': Bijection((R_w * L * U) + (U * L * R_w) + (R_w * L * R_w), decomp_to_binary_tree_b_3),
    'R_w_as': Bijection((R_b_head * U) + (U * R_b_head) + (R_b * R_b), decomp_to_binary_tree_w_2),
    'R_b_head': Bijection((R_w_head * L * U * U) + (U * U * L * R_w_head) + (R_w_head * L * R_w_head), decomp_to_binary_tree_b_4),
    'R_w_head': Bijection(U + (R_b * U) + (U * R_b) + (R_b * R_b), decomp_to_binary_tree_w_1_2),
    'R_b': Bijection((U + R_w) * L * (U + R_w), decomp_to_binary_tree_b_3),
    'R_w': Bijection((U + R_b) * (U + R_b), decomp_to_binary_tree_w_2)
})