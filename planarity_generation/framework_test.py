# -*- coding: utf-8 -*-
from framework.samplers.generic_samplers import *
from framework.decomposition_grammar import DecompositionGrammar
from framework.evaluation_oracle import Oracle
from framework.binary_tree_decomposition import binary_tree_grammar
# some shortcuts to make the grammar more readable
Z = ZeroAtom()
L = LAtom()
U = UAtom()
Bij = Bijection

Tree = Alias('Tree')

test_grammar = DecompositionGrammar()
test_grammar.add_rules({

    # this is just for testing
    # usual binary tree
    # T = (1 + T)² * Z_L
    'Tree': (Z + Tree) * (Z + Tree) * L,

})

# inject the oracle into the samplers
BoltzmannSampler.oracle = Oracle()#
BoltzmannSampler.active_grammar = test_grammar


print(test_grammar.sample('Tree', 'x0', 'y0'))

class BinaryTreeOracle(Oracle):
    def __init__(self):
        self.evaluations = {
            'x': 0.249875,
            'y': 1.0,
            'R_b_as(x,y)': 0.5,
            'R_w_as(x,y)': 0.5
        }



BoltzmannSampler.oracle = BinaryTreeOracle()
BoltzmannSampler.active_grammar = binary_tree_grammar
print(binary_tree_grammar.sample('K_dy', 'x', 'y'))