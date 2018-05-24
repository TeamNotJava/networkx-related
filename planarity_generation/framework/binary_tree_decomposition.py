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

    def __init__(self, left, right):
        self.left = left
        self.right = right

def decomp_to_binary_tree_b(decomp):
    print('test: '+decomp[0])
    return BinaryTree(None, None)

def decomp_to_binary_tree_w(decomp):
    print('test: '+decomp[0])
    return BinaryTree(None, None)

binary_tree_grammar = DecompositionGrammar()
binary_tree_grammar.add_rules({
    'K_dy': R_b_as + R_w_as,
    'R_b_as': (R_w * L + U) + (U + L + R_w) + (L * R_w * R_w),
    'R_w_as': (R_b_head * U) + (U * R_b_head) + (R_b * R_b),
    'R_b_head': (R_w_head * L * U * U) + (U * U * L * R_w_head) + (R_w_head * L * R_w_head),
    'R_w_head': U * (R_b * U) + (U * R_b) + (R_b * R_b),
    'R_b': Bijection((U + R_w) * L * (U + R_w), decomp_to_binary_tree_b),
    'R_w': Bijection((U + R_b) * (U + R_b), decomp_to_binary_tree_w)
})