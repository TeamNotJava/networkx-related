

class DecompositionGrammar:
    def __init__(self):
        self.rules = {}

    def add_rule(self, alias, combinatorial_class):
        self.rules[alias] = combinatorial_class

    def add_rules(self, rules):
        # merges the dictionaries, second has higher priority
        self.rules = {**self.rules, **rules}

    # samples from the rule identified by "alias"
    def sample(self, alias, x, y):
        assert alias in self.rules
        # inject this grammar into the sampler
        #BoltzmannSampler.active_grammar = self
        result = self.rules[alias].sample(x, y)
        #BoltzmannSampler.active_grammar = None
        return result
