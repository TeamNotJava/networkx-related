from .samplers.generic_samplers import *


# I have decided to put the Alias sampler here because it is so closely linked to the grammar
# An alias sampler is a sampler defined by a rule in a decomposition grammar.
# The rule can contain the same alias sampler itself.
# This allows to implement recursive decompositions.
class Alias(BoltzmannSampler):
    # attention, this is static
    active_grammar = None

    def __init__(self, alias):
        self.alias = alias

    def get_children(self):
        return [self.active_grammar.get_rule(self.alias)]

    # here we let the visitor decide if he wants to recurse further down into the children
    # kind of ugly but needed to avoid infinite recursion
    # alternative: ...
    def accept(self, visitor):
        visitor_wants_to_go_on = visitor.visit(self)
        if visitor_wants_to_go_on:
            for child in self.get_children():
                child.accept(visitor)

    def sampled_class(self):
        return self.alias

    def oracle_query_string(self, x: str, y: str):
        # Am I a recursive?
        if self.active_grammar.is_recursive_rule(self.alias):
            return self.alias + '(' + x + ',' + y + ')'
        else:
            return self.active_grammar.get_rule(self.alias).oracle_query_string(x, y)

    def get_all_oracle_queries(self, x, y):
        if self.active_grammar.is_recursive_rule(self.alias):
            return [self.oracle_query_string(x, y)]
        else:
            return self.active_grammar.get_rule(self.alias).get_all_oracle_queries(x, y)

    def get_eval(self, x, y):
        if self.active_grammar.is_recursive_rule(self.alias):
            return self.oracle.get(self.oracle_query_string(x, y))
        else:
            return self.active_grammar.get_rule(self.alias).get_eval(x, y)

    def sample(self, x, y):
        return self.active_grammar.get_rule(self.alias).sample(x, y)


class DecompositionGrammar:
    def __init__(self):
        self.rules = {}
        self.recursive_rules = []

    def add_rule(self, alias, combinatorial_class):
        self.rules[alias] = combinatorial_class
        self.find_recursive_rules()

    def add_rules(self, rules):
        # merges the dictionaries, second has higher priority
        self.rules = {**self.rules, **rules}
        self.find_recursive_rules()

    def get_rules(self):
        return self.rules

    def get_rule(self, key):
        return self.rules[key]

    def find_recursive_rules(self):
        ## !!! ugly
        Alias.active_grammar = self
        ###
        self.recursive_rules = []
        for key in self.rules:
            visitor = self.RecursiveRuleVisitor()
            Alias(key).accept(visitor)
            if key in visitor.recursive_rules:
                self.recursive_rules.append(key)

    def is_recursive_rule(self, key):
        return key in self.recursive_rules

    def collect_oracle_queries(self, key, x, y):
        visitor = self.CollectOracleQueriesVisitor(x, y)
        Alias(key).accept(visitor)
        return visitor.result

    # samples from the rule identified by the key "alias"
    def sample(self, alias, x, y):
        return Alias(alias).sample(x, y)

    class CollectOracleQueriesVisitor:
        def __init__(self, x_0, y_0):
            self.seen_alias_samplers = []
            self.result = set([])
            self.x = x_0
            self.y = y_0
            self.stack_x = []
            self.stack_y = []

        def visit(self, sampler):

            if self.stack_x and self.stack_x[len(self.stack_x) - 1][0] == sampler:
                _, x = self.stack_x.pop()
                self.x = x

            if self.stack_y and self.stack_y[len(self.stack_y) - 1][0] == sampler:
                _, y = self.stack_y.pop()
                self.y = y

            if isinstance(sampler, LAtom) or isinstance(sampler, UAtom):
                self.result.add(sampler.oracle_query_string(self.x, self.y))
            if isinstance(sampler, LSubs):
                self.stack_x.append((sampler.rhs, self.x))
                self.x = sampler.rhs.oracle_query_string(self.x, self.y)
            if isinstance(sampler, USubs):
                self.stack_y.append((sampler.rhs, self.y))
                self.y = sampler.rhs.oracle_query_string(self.x, self.y)
            if isinstance(sampler, LDerFromUDer):
                self.result.add(sampler.oracle_query_string(self.x, self.y))
            if isinstance(sampler, UDerFromLDer):
                self.result.add(sampler.oracle_query_string(self.x, self.y))
            if isinstance(sampler, Transformation):
                self.result.add(sampler.oracle_query_string(self.x, self.y))
            if isinstance(sampler, Alias):
                if sampler.alias in self.seen_alias_samplers:
                    self.result.add(sampler.oracle_query_string(self.x, self.y))
                    visitor_wants_to_go_on = False
                    return visitor_wants_to_go_on
                else:
                    self.seen_alias_samplers.append(sampler.alias)
                    visitor_wants_to_go_on = True
                    return visitor_wants_to_go_on

    class RecursiveRuleVisitor:
        def __init__(self):
            self.seen_alias_samplers = []
            self.recursive_rules = []

        def visit(self, sampler):
            if isinstance(sampler, Alias):
                if sampler.alias in self.seen_alias_samplers:
                    # if we see it for the second time then we know it's recursive
                    self.recursive_rules.append(sampler.alias)
                    # return False in order to not recurse down forever
                    visitor_wants_to_go_on = False
                    return visitor_wants_to_go_on
                else:
                    self.seen_alias_samplers.append(sampler.alias)
                    visitor_wants_to_go_on = True
                    return visitor_wants_to_go_on
