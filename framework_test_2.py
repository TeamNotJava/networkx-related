from framework.planar_graph_decomposition import *

class Oracle:
    # todo fill it with the evaluations
    def __init__(self):
        self.evaluations = {

        }

    def get(self, query_string):
        #try:
        return self.evaluations[query_string]
        #except(KeyError):
         #   print('Oracle key missing: {}'.format(query_string))
        #    return 0.5

oracle = Oracle()

print("recursive rules:")
print(planar_graph_grammar.recursive_rules)
print()

queries = planar_graph_grammar.collect_oracle_queries('G_dx_dx', 'x', 'y')
print("needed oracle queries:")
for query in sorted(queries):
    print(query)
    # add dummy entry to oracle just for testing
    oracle.evaluations[query] = 0.5

BoltzmannSampler.oracle = oracle
planar_graph_grammar.sample('G_dx_dx', 'x', 'y')