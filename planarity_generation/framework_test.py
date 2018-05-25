# -*- coding: utf-8 -*-
from framework.samplers.generic_samplers import *
from framework.decomposition_grammar import *

# some shortcuts to make the grammar more readable
class Oracle:
    # these values are for size 100
    evaluations = {
        'x0': 0.4999749994,
        'y0': 1.0,  # this is not needed here
        'Tree(x0,y0)': 0.99005
    }

    def get(self, query_string):
        # print(query_string)
        if query_string in self.evaluations:
            return self.evaluations[query_string]
        else:
            return 0.5


# some shortcuts to make the grammar more readable
Z = ZeroAtom()
L = LAtom()
U = UAtom()

Tree = Alias('Tree')
Bla = Alias('Bla')
Blub = Alias('Blub')
Blob = Alias('Blob')

test_grammar = DecompositionGrammar()
test_grammar.add_rules({

    # tree is either a leaf or inner node with two children which are trees
    'Tree': L + Tree * L * Blub,
    'Blub': USubs(Bla, Blob),
    'Blob': L + U + Z,
    'Bla': LSubs(Blub, Blob),


})

# inject the oracle into the samplers
BoltzmannSampler.oracle = Oracle()
Alias.active_grammar = test_grammar

print(test_grammar.recursive_rules)
print()

print(test_grammar.collect_oracle_queries('Bla', 'x', 'y'))

#for key in test_grammar.get_rules():
    #print(test_grammar.collect_oracle_queries(key, 'x', 'y'))

# sizes = [test_grammar.sample('Tree', 'x0', 'y0').get_l_size() for _ in range(1000)]
# sum(sizes) / len(sizes)