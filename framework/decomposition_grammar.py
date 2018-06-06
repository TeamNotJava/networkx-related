from .samplers.generic_samplers import *
import sys


# I have decided to put the Alias sampler here because it is so closely linked to the grammar
# An alias sampler is a sampler defined by a rule in a decomposition grammar.
# The rule can contain the same alias sampler itself.
# This allows to implement recursive decompositions.
class Alias(BoltzmannSampler):
    grammar_not_initialized_error_msg = ": you have to set the grammar this Alias sampler belongs to before using it"

    def __init__(self, alias, grammar=None):
        self.alias = alias
        self.grammar = grammar

    def get_children(self):
        if self.grammar is None:
            sys.exit(self.alias + self.grammar_not_initialized_error_msg)
        return [self.grammar.get_rule(self.alias)]

    # here we let the visitor decide if he wants to recurse further down into the children
    # kind of ugly but needed to avoid infinite recursion
    # alternative: let the Alias sampler itself decide that
    def accept(self, visitor):
        visitor_wants_to_go_on = visitor.visit(self)
        if visitor_wants_to_go_on:
            for child in self.get_children():
                child.accept(visitor)

    def sampled_class(self):
        return self.alias

    def is_recursive(self):
        # Am I a recursive?
        return self.grammar.is_recursive_rule(self.alias)

    def oracle_query_string(self, x: str, y: str):
        if self.grammar is None:
            sys.exit(self.alias + self.grammar_not_initialized_error_msg)
        if self.is_recursive():
            return self.alias + '(' + x + ',' + y + ')'
        else:
            return self.grammar.get_rule(self.alias).oracle_query_string(x, y)

    def get_all_oracle_queries(self, x, y):
        if self.grammar is None:
            sys.exit(self.alias + self.grammar_not_initialized_error_msg)
        if self.grammar.is_recursive_rule(self.alias):
            return [self.oracle_query_string(x, y)]
        else:
            return self.grammar.get_rule(self.alias).get_all_oracle_queries(x, y)

    def get_eval(self, x, y):
        if self.grammar is None:
            sys.exit(self.alias + self.grammar_not_initialized_error_msg)
        if self.grammar.is_recursive_rule(self.alias):
            return self.oracle.get(self.oracle_query_string(x, y))
        else:
            return self.grammar.get_rule(self.alias).get_eval(x, y)

    def sample(self, x, y):
        if self.grammar is None:
            sys.exit(self.alias + self.grammar_not_initialized_error_msg)
        return self.grammar.get_rule(self.alias).sample(x, y)


class DecompositionGrammar:
    def __init__(self, rules={}):
        self.rules = rules
        self.recursive_rules = None

    def add_rule(self, alias, sampler):
        self.rules[alias] = sampler

    def add_rules(self, rules):
        # merges the dictionaries, second has higher priority
        self.rules = {**self.rules, **rules}

    def get_rules(self):
        return self.rules

    def get_rule(self, alias):
        return self.rules[alias]

    def get_recursive_rules(self):
        if self.recursive_rules is None:
            sys.exit("You have to initialize the grammar first. Call init() after adding all your rules.")
        return self.recursive_rules

    def is_recursive_rule(self, key):
        if self.recursive_rules is None:
            sys.exit("You have to initialize the grammar first. Call init() after adding all your rules.")
        return key in self.recursive_rules

    def collect_oracle_queries(self, alias, x, y):
        if alias not in self.rules:
            sys.exit(alias + ": is not a rule in the grammar")
        visitor = self.CollectOracleQueriesVisitor(x, y)
        self.rules[alias].accept(visitor)
        return visitor.result

    def infer_target_class_labels(self):
        # just looks if the top sampler of a rule is a transformation sampler and this case
        # automatically sets the label of the target class
        for alias in self.rules:
            sampler = self.rules[alias]
            while isinstance(sampler, BijectionSampler):
                sampler = sampler.get_children()[0]
            if isinstance(sampler, TransformationSampler):
                sampler.set_target_class_label(alias)

    # samples from the rule identified by the key "alias"
    def sample(self, alias, x, y):
        if alias not in self.rules:
            sys.exit(alias + ": is not a rule in the grammar")
        return self.rules[alias].sample(x, y)

    def init(self):
        # initialize the alias samplers (set their referenced grammar to this grammar)
        visitor = self.SetActiveGrammarVisitor(self)
        for alias in self.rules:
            # print(alias)
            self.rules[alias].accept(visitor)
        # find out which rules are recursive
        self.recursive_rules = set()
        for alias in self.rules:
            visitor = self.FindRecursiveRulesVisitor()
            self.rules[alias].accept(visitor)
            self.recursive_rules |= set(visitor.get_result())
        # automatically set target class labels of transformation sampler where possible
        self.infer_target_class_labels()

    ### visitors ###

    # sets the grammar in all Alias samplers participating in the given grammar
    class SetActiveGrammarVisitor:
        def __init__(self, grammar):
            self.grammar = grammar

        def visit(self, sampler):
            if isinstance(sampler, Alias):
                sampler.grammar = self.grammar
                visitor_wants_to_go_on = False
                return visitor_wants_to_go_on

    # determines which rules are recursive
    class FindRecursiveRulesVisitor:
        def __init__(self):
            self.seen_alias_samplers = []
            self.result = []
            self.stack = []

        def get_result(self):
            return self.result

        def visit(self, sampler):
            if self.stack and self.stack[-1][0] == sampler:
                _, old_state = self.stack.pop()
                self.seen_alias_samplers = old_state
            # at binary samplers the path branches
            if isinstance(sampler, BinarySampler):
                # the visitor goes into the left child first
                # so when we get to the right child later we can now and restore state
                # here the list has to be copied
                self.stack.append((sampler.rhs, list(self.seen_alias_samplers)))
            if isinstance(sampler, Alias):
                if sampler.alias in self.seen_alias_samplers:
                    # if we see it for the second time then we know it's recursive
                    self.result.append(sampler.alias)
                    # return False in order to not recurse down forever
                    visitor_wants_to_go_on = False
                    return visitor_wants_to_go_on
                else:
                    self.seen_alias_samplers.append(sampler.alias)
                    visitor_wants_to_go_on = True
                    return visitor_wants_to_go_on

    # predicts which oracle queries will be made when sampling from the grammar
    class CollectOracleQueriesVisitor:
        def __init__(self, x_0, y_0):
            self.seen_alias_samplers = []
            self.result = set()
            self.x = x_0
            self.y = y_0
            self.stack_x = []
            self.stack_y = []

        def get_result(self):
            return self.result

        def visit(self, sampler):

            if self.stack_x and self.stack_x[-1][0] == sampler:
                _, x = self.stack_x.pop()
                self.x = x

            if self.stack_y and self.stack_y[-1][0] == sampler:
                _, y = self.stack_y.pop()
                self.y = y

            if isinstance(sampler, LAtomSampler) or isinstance(sampler, UAtomSampler):
                self.result.add(sampler.oracle_query_string(self.x, self.y))

            if isinstance(sampler, LSubsSampler):
                self.stack_x.append((sampler.rhs, self.x))
                self.x = sampler.rhs.oracle_query_string(self.x, self.y)

            if isinstance(sampler, USubsSampler):
                self.stack_y.append((sampler.rhs, self.y))
                self.y = sampler.rhs.oracle_query_string(self.x, self.y)

            if isinstance(sampler, TransformationSampler) and not isinstance(sampler, BijectionSampler):
                if sampler.eval_transform is None:
                    self.result.add(sampler.oracle_query_string(self.x, self.y))
                # otherwise the sampler has an eval_transform function and does not directly query the oracle

            if isinstance(sampler, Alias):
                if sampler.alias in self.seen_alias_samplers:
                    if sampler.is_recursive():
                        # i'm not very confident about this
                        self.result.add(sampler.oracle_query_string(self.x, self.y))
                    visitor_wants_to_go_on = False
                    return visitor_wants_to_go_on
                else:
                    self.seen_alias_samplers.append(sampler.alias)
                    visitor_wants_to_go_on = True
                    return visitor_wants_to_go_on
