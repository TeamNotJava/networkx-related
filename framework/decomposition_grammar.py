import warnings

from framework.class_builder import DefaultBuilder, DummyBuilder
from framework.generic_samplers import *
import sys

from framework.generic_samplers import BoltzmannSamplerBase


class AliasSampler(BoltzmannSamplerBase):
    """
    Sampler defined by a rule in a decomposition grammar.

    The rule can contain the same alias sampler itself, allowing the implementation of recursive decompositions.
    From a different point of view, an alias sampler is a non-terminal symbol in the decomposition grammar.

    Parameters
    ----------
    alias: str
    """

    def __init__(self, alias):
        super(AliasSampler, self).__init__()
        self._alias = alias
        self._grammar = None

    def _grammar_not_initialized_error_msg(self):
        return "{}: you have to set the grammar this AliasSampler belongs to before using it".format(self._alias)

    @property
    def is_recursive(self):
        """Checks if this AliasSampler belongs to a recursive rule (i.e. calls itself directly or indirectly).

        Returns
        -------
        bool
            True iff this sampler corresponds to a recursive rule in the grammar.
        """
        return self._grammar.is_recursive_rule(self._alias)

    @property
    def grammar(self):
        """Returns the grammar this alias sampler belongs to.

        Returns
        -------
        grammar: DecompositionGrammar
        """
        return self._grammar

    @grammar.setter
    def grammar(self, g):
        """Sets the grammar of this sampler.

        Parameters
        ----------
        g: DecompositionGrammar
        """
        self._grammar = g

    @property
    def sampled_class(self):
        return self._alias

    def sample(self, x, y):
        if self.grammar is None:
            raise BoltzmannFrameworkError(self._grammar_not_initialized_error_msg())
        return self.grammar[self.sampled_class].sample(x, y)

    @return_precomp
    def eval(self, x, y):
        if self.grammar is None:
            raise BoltzmannFrameworkError(self._grammar_not_initialized_error_msg())
        if self.is_recursive:
            return self.oracle.get(self.oracle_query_string(x, y))
        else:
            return self.grammar[self.sampled_class].eval(x, y)

    def oracle_query_string(self, x, y):
        if self.grammar is None:
            raise BoltzmannFrameworkError(self._grammar_not_initialized_error_msg())
        if self.is_recursive:
            # Evaluations of recursive classes cannot be inferred automatically.
            return "{}({},{})".format(self._alias, x, y)
        else:
            return self.grammar[self.sampled_class].oracle_query_string(x, y)

    def get_children(self):
        if self.grammar is None:
            raise BoltzmannFrameworkError(self._grammar_not_initialized_error_msg())
        return [self.grammar[self.sampled_class]]

    def accept(self, visitor):
        # here we let the visitor decide if he wants to recurse further down into the children
        # kind of ugly but needed to avoid infinite recursion
        # alternative: let the Alias sampler itself decide that
        visitor_wants_to_go_on = visitor.visit(self)
        if visitor_wants_to_go_on:
            for child in self.get_children():
                child.accept(visitor)


class DecompositionGrammar(object):
    """
    Represents a decomposition grammar as a collection of several rules.

    Parameters
    ----------
    rules: dict, optional (default=None)
        Initial set of rules of this grammar.
    """

    def __init__(self, rules=None):
        if rules is None:
            rules = {}
        self._rules = rules
        self._recursive_rules = None

    @staticmethod
    def _grammar_not_initialized_error():
        msg = "Grammar not initialized"
        raise BoltzmannFrameworkError(msg)

    @staticmethod
    def _missing_rule_error(alias):
        msg = "Not a rule in the grammar: {}".format(alias)
        raise BoltzmannFrameworkError(msg)

    def init(self):
        """Initializes the grammar.

        A grammar can only be used for sampling after initialization.
        """
        # Initialize the alias samplers (set their referenced grammar to this grammar).
        self._set_active_grammar()
        # Find out which rules are recursive.
        self._find_recursive_rules()
        # Automatically set target class labels of transformation samplers where possible.
        self._infer_target_class_labels()

    def _set_active_grammar(self):
        """Sets the grammar in the alias samplers."""

        def apply_to_each(sampler):
            if isinstance(sampler, AliasSampler):
                sampler.grammar = self

        for alias in self._rules:
            v = self._DFSVisitor(apply_to_each)
            self[alias].accept(v)

    def _find_recursive_rules(self):
        """Analyses the grammar to find out which rules are recursive and saves them."""
        rec_rules = []
        for alias in self.rules:
            sampler = self[alias]

            def apply_to_each(sampler):
                if isinstance(sampler, AliasSampler) and sampler.sampled_class == alias:
                    return alias

            v = self._DFSVisitor(apply_to_each)
            sampler.accept(v)
            if v.result:
                rec_rules += v.result
        # Duplicates might occur.
        self._recursive_rules = set(rec_rules)

    def _infer_target_class_labels(self):
        """Automatically tries to infer class labels if they are not given explicitly."""
        for alias in self.rules:
            sampler = self[alias]
            # Looks if the top sampler of a rule is a transformation sampler and this case automatically sets the label
            # of the target class.
            while isinstance(sampler, BijectionSampler):
                sampler = sampler.get_children()[0]
            if isinstance(sampler, TransformationSampler):
                sampler.sampled_class = alias

    def set_builder(self, rules=None, builder=DefaultBuilder()):
        """Sets a builder for a given set of rules.

        Parameters
        ----------
        rules: str or iterable, optional (default=all rules in the grammar)
        builder: CombinatorialClassBuilder, optional (default=DefaultBuilder)

        Returns
        -------
        v: SetBuilderVisitor
        """
        if rules is None:
            rules = self._rules.keys()
        if type(rules) is str:
            rules = [rules]
        v = self._SetBuilderVisitor(builder)
        for alias in rules:
            self[alias].accept(v)
        return v

    def add_rule(self, alias, sampler):
        """Adds a decomposition rule to this grammar.

        Parameters
        ----------
        alias: str
        sampler: BoltzmannSamplerBase
        """
        self._rules[alias] = sampler

    def __setitem__(self, key, value):
        """Shorthand for add_rule."""
        self.add_rule(key, value)

    def get_rule(self, alias):
        """Returns the rule corresponding to the given alias.

        Parameters
        ----------
        alias: str
        """
        return self._rules[alias]

    def __getitem__(self, item):
        """A shorthand for get_rule."""
        return self._rules[item]

    @property
    def rules(self):
        return self._rules

    @rules.setter
    def rules(self, rules):
        """Adds the given set of rules.

        Parameters
        ----------
        rules: dict
            The rules to be added.
        """
        for alias in rules:
            self[alias] = rules[alias]

    @property
    def recursive_rules(self):
        """Gets the recursive rules in this grammar.

        May only be called after initialization.

        Returns
        -------
        rules: set of str
            The aliases of all recursive rules in this gramamr.
        """
        if self._recursive_rules is None:
            DecompositionGrammar._grammar_not_initialized_error()
        return sorted(self._recursive_rules)

    def is_recursive_rule(self, alias):
        """Checks if the rule corresponding to the given alias is recursive.

        Parameters
        ----------
        alias: str

        Returns
        -------
        is_recursive: bool
        """
        if self._recursive_rules is None:
            DecompositionGrammar._grammar_not_initialized_error()
        return alias in self.recursive_rules

    def collect_oracle_queries(self, alias, x, y):
        """Returns all oracle queries that may be needed when sampling from the rule identified by alias.

        Parameters
        ----------
        alias: str
        x: str
            Symbolic x value.
        y: str
            Symbolic y value.

        Returns
        -------
        oracle_queries: set of str
        """
        if alias not in self.rules:
            DecompositionGrammar._missing_rule_error(alias)
        visitor = self._CollectOracleQueriesVisitor(x, y)
        self[alias].accept(visitor)
        return sorted(visitor.result)

    def precompute_evals(self, alias, x, y):
        """Precomputes all evaluations needed for sampling from the given class with the symbolic x and y values.

        Parameters
        ----------
        alias: str
        x: str
            Symbolic x value.
        y: str
            Symbolic y value.
        """
        if alias not in self.rules:
            DecompositionGrammar._missing_rule_error(alias)
        visitor = self._PrecomputeEvaluationsVisitor(x, y)
        self[alias].accept(visitor)

    def sample(self, alias, x, y):
        """Samples from the rule identified by the given alias.

        Parameters
        ----------
        alias: str
        x: str
            Symbolic x value.
        y: str
            Symbolic y value.

        Returns
        -------
        CombinatorialClass
        """
        sampler = None
        try:
            sampler = self[alias]
        except KeyError:
            DecompositionGrammar._missing_rule_error(alias)
        return sampler.sample(x, y)

    def dummy_sampling_mode(self):
        """Changes the state of the grammar to the dummy sampling mode.

        A dummy object only records its size but otherwise has no internal structure which is useful for testing sizes.
        This will overwrite existing builder information. After this operation, dummies can be sampled with sample(...).
        """
        v = self.set_builder(builder=DummyBuilder())
        if v.overwrites_builder and Settings.debug_mode:
            warnings.warn("dummy_sampling_mode has overwritten existing builders")

    class _DFSVisitor:
        """
        Traverses the sampler hierarchy with a DFS.

        Parameters
        ----------
        f: function
            Function to be applied to all nodes (=samplers).
        """

        def __init__(self, f):
            self._f = f
            self._result = []
            self._seen_alias_samplers = set()

        def visit(self, sampler):
            # Apply the function to the current sampler.
            r = self._f(sampler)
            # Append the return value to the result list if any.
            if r is not None:
                self.result.append(r)
            if isinstance(sampler, AliasSampler):
                if sampler.sampled_class in self._seen_alias_samplers:
                    # Do not recurse into the alias sampler because we have already seen it.
                    return False
                else:
                    self._seen_alias_samplers.add(sampler.sampled_class)
                    # Recurse further down.
                    return True

        @property
        def result(self):
            return self._result

    class _SetBuilderVisitor:
        """
        Sets builders until hitting an AliasSampler.

        Parameters
        ----------
        builder: CombinatorialClassBuilder
            The builder to be set to all visited samplers.
        """

        def __init__(self, builder):
            self._builder = builder
            self._overwrites_builder = False

        def visit(self, sampler):
            if isinstance(sampler, AliasSampler):
                # Don't recurse into the alias samplers.
                return False
            else:
                # Otherwise set the given builder.
                if sampler.builder is not None:
                    self._overwrites_builder = True
                sampler.builder = self._builder

        @property
        def overwrites_builder(self):
            return self._overwrites_builder

    class _PrecomputeEvaluationsVisitor:
        """
        Precomputes evaluations for the sampler in the given hierarchy.
        Parameters
        ----------
        x: str
            Symbolic x value.
        y: str
            Symbolic y value.
        """

        def __init__(self, x, y):
            self._seen_alias_samplers = set()
            self._x = x
            self._y = y
            self._stack_x = []
            self._stack_y = []

        def visit(self, sampler):
            if self._stack_x and self._stack_x[-1][0] == sampler:
                _, x = self._stack_x.pop()
                self._x = x
            if self._stack_y and self._stack_y[-1][0] == sampler:
                _, y = self._stack_y.pop()
                self._y = y
            if isinstance(sampler, LSubsSampler):
                self._stack_x.append((sampler.rhs, self._x))
            if isinstance(sampler, USubsSampler):
                self._stack_y.append((sampler.rhs, self._y))
            sampler.precompute_eval(self._x, self._y)
            if isinstance(sampler, AliasSampler):
                if sampler.sampled_class in self._seen_alias_samplers:
                    # Indicate that the recursion should not go further down here as we have already seen the alias.
                    return False
                else:
                    self._seen_alias_samplers.add(sampler.sampled_class)
                    # Recurse further down.
                    return True

    class _CollectOracleQueriesVisitor:
        """
        Predicts which oracle queries will be needed when sampling from the grammar.
        This might still be a bit buggy but its not crucial for the correctness of the samplers.

        Parameters
        ----------
        x: str
            Symbolic x value.
        y: str
            Symbolic y value.
        """

        def __init__(self, x, y):
            self._seen_alias_samplers = set()
            self._result = set()
            self._x = x
            self._y = y
            self._stack_x = []
            self._stack_y = []

        @property
        def result(self):
            return self._result

        def visit(self, sampler):
            if self._stack_x and self._stack_x[-1][0] == sampler:
                _, x = self._stack_x.pop()
                self._x = x
            if self._stack_y and self._stack_y[-1][0] == sampler:
                _, y = self._stack_y.pop()
                self._y = y
            if isinstance(sampler, LAtomSampler) or isinstance(sampler, UAtomSampler):
                self._result.add(sampler.oracle_query_string(self._x, self._y))
            if isinstance(sampler, LSubsSampler):
                self._stack_x.append((sampler.rhs, self._x))
                self._x = sampler.rhs.oracle_query_string(self._x, self._y)
            if isinstance(sampler, USubsSampler):
                self._stack_y.append((sampler.rhs, self._y))
                self._y = sampler.rhs.oracle_query_string(self._x, self._y)
            if isinstance(sampler, TransformationSampler) and not isinstance(sampler, BijectionSampler):
                if sampler._eval_transform is None:
                    self._result.add(sampler.oracle_query_string(self._x, self._y))
                # Otherwise the sampler has an eval_transform function and does not directly query the oracle.
            if isinstance(sampler, AliasSampler):
                if sampler.sampled_class in self._seen_alias_samplers:
                    if sampler.is_recursive:
                        self._result.add(sampler.oracle_query_string(self._x, self._y))
                    # Indicate that the recursion should not go further down here as we have already seen the alias.
                    return False
                else:
                    self._seen_alias_samplers.add(sampler.sampled_class)
                    # Recurse further down.
                    return True
