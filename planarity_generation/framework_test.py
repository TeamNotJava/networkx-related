from framework.samplers.generic_samplers import *
from framework.decomposition_grammar import DecompositionGrammar
from framework.evaluation_oracle import Oracle

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
