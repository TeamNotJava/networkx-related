from framework.generic_samplers import *
import sys


class AliasSampler(BoltzmannSampler):
    """
    I have decided to put the Alias sampler here because it is so closely linked to the grammar
    An alias sampler is a sampler defined by a rule in a decomposition grammar.
    The rule can contain the same alias sampler itself.
    This allows to implement recursive decompositions.
    """

    grammar_not_initialized_error_msg = ": you have to set the grammar this Alias sampler belongs to before using it"

    def __init__(self, alias, grammar=None):
        super().__init__()
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

    def get_eval(self, x, y):
        if self.grammar is None:
            sys.exit(self.alias + self.grammar_not_initialized_error_msg)
        if self.is_recursive():
            return self.oracle.get(self.oracle_query_string(x, y))
        else:
            return self.grammar.get_rule(self.alias).get_eval(x, y)

    def sample(self, x, y):
        if self.grammar is None:
            sys.exit(self.alias + self.grammar_not_initialized_error_msg)
        return self.grammar.get_rule(self.alias).sample(x, y)

    def sample_dummy(self, x, y):
        if self.grammar is None:
            sys.exit(self.alias + self.grammar_not_initialized_error_msg)
        return self.grammar.get_rule(self.alias).sample_dummy(x, y)


class DecompositionGrammar:
    """
    Represents a decomposition grammar as a collection of several rules.
    """

    def __init__(self, rules=None):
        if rules is None:
            rules = {}
        self.rules = rules
        self.recursive_rules = None

    def init(self):
        """
        Initializes the grammar. May take some seconds.
        :return:
        """

        # Initialize the alias samplers (set their referenced grammar to this grammar).
        self.set_active_grammar()
        # Find out which rules are recursive.
        self.find_recursive_rules()
        # Automatically set target class labels of transformation samplers where possible.
        self.infer_target_class_labels()
        # Precompute evals.
        # todo

    def set_active_grammar(self):
        def apply_to_each(sampler):
            if isinstance(sampler, AliasSampler):
                sampler.grammar = self

        for alias in self.rules:
            v = self.DFSVisitor(apply_to_each)
            self.rules[alias].accept(v)

    def find_recursive_rules(self):
        recursive_rules = []
        for alias in self.rules:
            sampler = self.rules[alias]

            def apply_to_each(sampler):
                if isinstance(sampler, AliasSampler) and sampler.sampled_class() == alias:
                    return alias

            v = self.DFSVisitor(apply_to_each)
            sampler.accept(v)
            if v.get_result():
                recursive_rules += v.get_result()
        # Duplicates might occur, so return a set.
        self.recursive_rules = set(recursive_rules)

    def infer_target_class_labels(self):
        # Just looks if the top sampler of a rule is a transformation sampler and this case
        # automatically sets the label of the target class.
        for alias in self.rules:
            sampler = self.rules[alias]
            while isinstance(sampler, BijectionSampler):
                sampler = sampler.get_children()[0]
            if isinstance(sampler, TransformationSampler):
                sampler.set_target_class_label(alias)

    def set_builder(self, rules=None, builder=DefaultBuilder):
        if rules is None:
            rules = self.rules.keys()
        v = self.SetBuilderVisitor(builder)
        for alias in rules:
            self.get_rule(alias).accept(v)

    def add_rule(self, alias, sampler):
        self.rules[alias] = sampler

    def add_rules(self, rules):
        # Merges the dictionaries, second has higher priority.
        self.rules = {**self.rules, **rules}

    def get_rules(self):
        return self.rules

    def get_rule(self, alias):
        return self.rules[alias]

    def get_recursive_rules(self):
        if self.recursive_rules is None:
            sys.exit("You have to initialize the grammar first. Call init(top_rule) after adding all your rules.")
        return self.recursive_rules

    def is_recursive_rule(self, key):
        if self.recursive_rules is None:
            sys.exit("You have to initialize the grammar first. Call init(top_rule) after adding all your rules.")
        return key in self.recursive_rules

    def collect_oracle_queries(self, alias, x, y):
        if alias not in self.rules:
            sys.exit(alias + ": is not a rule in the grammar")
        visitor = self.CollectOracleQueriesVisitor(x, y)
        self.rules[alias].accept(visitor)
        return visitor.result

    def sample(self, alias, x, y):
        """
        Samples from the rule identified by the key 'alias'.
        :param alias:
        :param x:
        :param y:
        :return:
        """
        if alias not in self.rules:
            sys.exit(alias + ": is not a rule in the grammar")
        return self.rules[alias].sample(x, y)

    def sample_dummy(self, alias, x, y):
        # TODO solve with builders
        """
        Samples a dummy from the rule identified by the key 'alias'.
        :param alias:
        :param x:
        :param y:
        :return:
        """
        if alias not in self.rules:
            sys.exit(alias + ": is not a rule in the grammar")
        return self.rules[alias].sample_dummy(x, y)

    # Visitors

    class DFSVisitor:
        """
        Traverses the given sampler hierarchy with a DFS.
        """

        def __init__(self, f):
            self.f = f
            self.result = []
            self.seen_alias_samplers = []

        def visit(self, sampler):
            # Apply the function to the current sampler.
            r = self.f(sampler)
            # Append the return value to the result list if any.
            if r is not None:
                self.result.append(r)
            if isinstance(sampler, AliasSampler):
                if sampler.alias in self.seen_alias_samplers:
                    # Don't recurse into the alias sampler because we have already seen it.
                    return False
                else:
                    self.seen_alias_samplers.append(sampler.alias)
                    # Recurse further down.
                    return True

        def get_result(self):
            return self.result

    class SetBuilderVisitor:
        """
        Sets builders until hitting an AliasSampler.
        """

        def __init__(self, builder):
            self.builder = builder

        def visit(self, sampler):

            if isinstance(sampler, AliasSampler):
                # Don't recurse into the alias samplers.
                return False
            else:
                # Otherwise set the given builder.
                sampler.set_builder(self.builder)

    class PrecomputeEvaluationsVisitor:
        """
        Precomputes evaluations for the sampler in the given hierarchy.
        """

        def __init__(self):
            pass

        def visit(self, sampler):
            pass

    class CollectOracleQueriesVisitor:
        """
        Predicts which oracle queries will be needed when sampling from the grammar.
        This might still be a bit buggy but its not crucial for the correctness of the samplers.
        """

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

            if isinstance(sampler, AliasSampler):
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
