from framework.decomposition_grammar import Alias
from framework.samplers.generic_samplers import *
from .decomposition_grammar import DecompositionGrammar
from framework.utils import bern
import logging

L = LAtom()
U = UAtom()

K_dy = Alias('K_dy')
R_b_as = Alias('R_b_as')
R_w_as = Alias('R_w_as')
R_b_head = Alias('R_b_head')
R_w_head = Alias('R_w_head')
R_b = Alias('R_b')
R_w = Alias('R_w')
K = Alias('K')

class BinaryTree(CombinatorialClass):
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
    
    def get_u_size(self):
        return self.get_attribute('numleafs')
        
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
    def __str__(self):
        return self.__repr__()
    
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
    logging.debug("b_3")
    logging.debug(decomp)
    numblacknodes = 1
    numwhitenodes = 0
    numtotal = 1
    numleafs = 0
    if type(decomp.first.first) is UAtomClass:
        left = None
        numleafs += 1
    else:
        left = decomp.first.first
        if left:
            numblacknodes += left.get_attribute('numblacknodes')
            numwhitenodes += left.get_attribute('numwhitenodes')
            numtotal += left.get_attribute('numtotal')
            numleafs += left.get_attribute('numleafs')
    
    if type(decomp.second) is UAtomClass:
        right = None
        numleafs += 1
    else:
        right = decomp.second
        if right:
            numblacknodes += right.get_attribute('numblacknodes')
            numwhitenodes += right.get_attribute('numwhitenodes')
            numtotal += right.get_attribute('numtotal')
            numleafs += right.get_attribute('numleafs')

    tree = BinaryTree(left, right, 
        color='black', 
        numtotal=numtotal, 
        numblacknodes=numblacknodes, 
        numwhitenodes=numwhitenodes,
        numleafs=numleafs
    )
    logging.debug(tree)
    return tree

def decomp_to_binary_tree_b_4(decomp):
    logging.debug("b_4")
    logging.debug(decomp)

    numblacknodes = 1
    numwhitenodes = 0
    numtotal = 1
    numleafs = 0

    #(((X,L),U),U)
    if type(decomp.second) is UAtomClass and type(decomp.first.second) is UAtomClass:
        logging.debug("#(((X,L),U),U)")
        left = decomp.first.first.first
        if left:
            numblacknodes += left.get_attribute('numblacknodes')
            numwhitenodes += left.get_attribute('numwhitenodes')
            numtotal += left.get_attribute('numtotal')
            numleafs += left.get_attribute('numleafs')

        numwhitenodes += 1
        numtotal += 1
        right = BinaryTree(None, None, color='white')
        numleafs += 2
            
    #(((U,U),L),X)
    elif type(decomp.first.first) is ProdClass and type(decomp.first.first.first) is UAtomClass and type(decomp.first.first.second) is UAtomClass:
        logging.debug("#(((U,U),L),X)")
        numwhitenodes += 1
        numtotal += 1
        numleafs = 0

        left = BinaryTree(None, None, color='white')
        numleafs += 2

        right = decomp.second
        if right:
            numblacknodes += right.get_attribute('numblacknodes')
            numwhitenodes += right.get_attribute('numwhitenodes')
            numtotal += right.get_attribute('numtotal')
            numleafs += right.get_attribute('numleafs')
    #((X,L),X)
    else:
        logging.debug("#((X,L),X)")
        right = decomp.second
        if right:
            numblacknodes += right.get_attribute('numblacknodes')
            numwhitenodes += right.get_attribute('numwhitenodes')
            numtotal += right.get_attribute('numtotal')
            numleafs += right.get_attribute('numleafs')

        left = decomp.first.first
        if left:
            numblacknodes += left.get_attribute('numblacknodes')
            numwhitenodes += left.get_attribute('numwhitenodes')
            numtotal += left.get_attribute('numtotal')
            numleafs += left.get_attribute('numleafs')
        

    tree = BinaryTree(left, right,
        color='black', 
        numtotal=numtotal, 
        numblacknodes=numblacknodes, 
        numwhitenodes=numwhitenodes,
        numleafs=numleafs
    )
    logging.debug(tree)
    return tree
    
def decomp_to_binary_tree_w_2(decomp):
    logging.debug("w_2")
    logging.debug(decomp)

    numblacknodes = 0
    numwhitenodes = 1
    numtotal = 1
    numleafs = 0

    if type(decomp.first) is UAtomClass:
        left = None
        numleafs += 1
    else:
        left = decomp.first
        if left:
            numblacknodes += left.get_attribute('numblacknodes')
            numwhitenodes += left.get_attribute('numwhitenodes')
            numtotal += left.get_attribute('numtotal')
            numleafs += left.get_attribute('numleafs')

    if type(decomp.second) is UAtomClass:
        right = None
        numleafs += 1
    else:
        right = decomp.second
        if right:
            numblacknodes += right.get_attribute('numblacknodes')
            numwhitenodes += right.get_attribute('numwhitenodes')
            numtotal += right.get_attribute('numtotal')
            numleafs += right.get_attribute('numleafs')
    tree = BinaryTree(left, right, 
        color='white',
        numtotal=numtotal, 
        numblacknodes=numblacknodes, 
        numwhitenodes=numwhitenodes,
        numleafs=numleafs
    )
    logging.debug(tree)
    return tree

def decomp_to_binary_tree_w_1_2(decomp):
    """Creates either a white rooted tree with a left or a right None subtree
    or returns a None
    """
    if type(decomp) is UAtomClass:
        return None

    logging.debug("w_1_2")
    logging.debug(decomp)
    numblacknodes = 1
    numwhitenodes = 0
    numtotal = 1
    numleafs = 0
    if type(decomp.first) is UAtomClass:
        left = None
        numleafs += 1
    else:
        left = decomp.first
        if left:
            numblacknodes += left.get_attribute('numblacknodes')
            numwhitenodes += left.get_attribute('numwhitenodes')
            numtotal += left.get_attribute('numtotal')
            numleafs += left.get_attribute('numleafs')

    if type(decomp.second) is UAtomClass:
        right = None
        numleafs += 1
    else:
        right = decomp.second
        if right:
            numblacknodes += right.get_attribute('numblacknodes')
            numwhitenodes += right.get_attribute('numwhitenodes')
            numtotal += right.get_attribute('numtotal')
            numleafs += right.get_attribute('numleafs')

    tree = BinaryTree(left, right, 
        color='white',
        numtotal=numtotal, 
        numblacknodes=numblacknodes, 
        numwhitenodes=numwhitenodes,
        numleafs=numleafs
    )
    logging.debug(tree)
    return tree

class BTRejection(Transformation):
    def __init__(self, sampler, is_acceptable, target_class_label):
        # sampler is a sampler of the underlying class
        super(BTRejection, self).__init__(sampler, None, target_class_label)
        # this is a function that takes a structure and outputs true iff it matches the acceptance criteria
        self.is_acceptable = is_acceptable

    def sample(self, x, y):
        gamma = self.sampler.sample(x, y)
        while not self.is_acceptable(gamma):
            gamma = self.sampler.sample(x, y)
        return gamma

    def get_eval(self, x, y):
        return self.sampler.get_eval(x, y)/self.oracle.get(y)

def rejection_step(decomp):
    print(type(decomp))
    print(type(decomp.get_u_size()))
    return bern(2/decomp.get_u_size())

binary_tree_grammar = DecompositionGrammar()
binary_tree_grammar.add_rules({
    'G': K + U,
    'K': BTRejection(K_dy, rejection_step, 'K'),
    'K_dy': R_b_as + R_w_as,
    'R_b_as': Bijection((R_w * L * U) + (U * L * R_w) + (R_w * L * R_w), decomp_to_binary_tree_b_3),
    'R_w_as': Bijection((R_b_head * U) + (U * R_b_head) + (R_b * R_b), decomp_to_binary_tree_w_2),
    'R_b_head': Bijection((R_w_head * L * U * U) + (U * U * L * R_w_head) + (R_w_head * L * R_w_head), decomp_to_binary_tree_b_4),
    'R_w_head': Bijection(U + (R_b * U) + (U * R_b) + (R_b * R_b), decomp_to_binary_tree_w_1_2),
    'R_b': Bijection((U + R_w) * L * (U + R_w), decomp_to_binary_tree_b_3),
    'R_w': Bijection((U + R_b) * (U + R_b), decomp_to_binary_tree_w_2)
})