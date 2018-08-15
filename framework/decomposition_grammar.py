# -*- coding: utf-8 -*-
#    Copyright (C) 2018 by
#    Marta Grobelna <marta.grobelna@rwth-aachen.de>
#    Petre Petrov <petrepp4@gmail.com>
#    Rudi Floren <rudi.floren@gmail.com>
#    Tobias Winkler <tobias.winkler1@rwth-aachen.de>
#    All rights reserved.
#    BSD license.
#
# Authors:  Marta Grobelna <marta.grobelna@rwth-aachen.de>
#           Petre Petrov <petrepp4@gmail.com>
#           Rudi Floren <rudi.floren@gmail.com>
#           Tobias Winkler <tobias.winkler1@rwth-aachen.de>

import warnings

from framework.class_builder import DefaultBuilder, DummyBuilder
from framework.generic_samplers import *


class AliasSampler(BoltzmannSamplerBase):
    """
    Sampler defined by a rule in a decomposition grammar.

    The rule can contain the same alias sampler itself, allowing the implementation of recursive decompositions.
    From a different point of view, an alias sampler is a non-terminal symbol in the decomposition grammar.

    Parameters
    ----------
    alias: str
    """

    __slots__ = '_alias', '_grammar', '_referenced_sampler'

    def __init__(self, alias):
        super(AliasSampler, self).__init__()
        self._alias = alias
        self._grammar = None
        self._referenced_sampler = None  # The referenced sampler.

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
        return self._referenced_sampler.sample(x, y)

    @return_precomp
    def eval(self, x, y):
        if self.grammar is None:
            raise BoltzmannFrameworkError(self._grammar_not_initialized_error_msg())
        if self.is_recursive:
            return self.oracle.get(self.oracle_query_string(x, y))
        else:
            return self._referenced_sampler.eval(x, y)

    def oracle_query_string(self, x, y):
        if self.grammar is None:
            raise BoltzmannFrameworkError(self._grammar_not_initialized_error_msg())
        if self.is_recursive:
            # Evaluations of recursive classes cannot be inferred automatically.
            return "{}({},{})".format(self._alias, x, y)
        else:
            return self._referenced_sampler.oracle_query_string(x, y)

    def get_children(self):
        # TODO removed due to measurable performance increase
        # if self.grammar is None:
        #    raise BoltzmannFrameworkError(self._grammar_not_initialized_error_msg())
        # return [self._grammar[self._sampled_class]]
        return [self._referenced_sampler]

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
        self._init_alias_samplers()
        # Find out which rules are recursive.
        self._find_recursive_rules()
        # Automatically set target class labels of transformation samplers where possible.
        self._infer_target_class_labels()

    def _init_alias_samplers(self):
        """Sets the grammar in the alias samplers."""

        def apply_to_each(sampler):
            if isinstance(sampler, AliasSampler):
                sampler.grammar = self
                sampler._referenced_sampler = self[sampler.sampled_class]

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

        Returns
        -------
        BoltzmannSamplerBase
        """
        return self._rules[alias]

    def __getitem__(self, item):
        """A shorthand for get_rule.

        Parameters
        ----------
        item: str

        Returns
        -------
        BoltzmannSamplerBase
        """
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

    def dummy_sampling_mode(self, delete_transformations=False):
        """Changes the state of the grammar to the dummy sampling mode.

        A dummy object only records its size but otherwise has no internal structure which is useful for testing sizes.
        This will overwrite existing builder information. After this operation, dummies can be sampled with sample(...).
        """
        v = self.set_builder(builder=DummyBuilder())
        if v.overwrites_builder and Settings.debug_mode:
            warnings.warn("dummy_sampling_mode has overwritten existing builders")

        if delete_transformations:
            def apply_to_each(sampler):
                if isinstance(sampler, TransformationSampler) and not isinstance(sampler, RejectionSampler):
                    sampler.transformation = lambda x: x

            for alias in self.rules:
                v = self._DFSVisitor(apply_to_each)
                self[alias].accept(v)

    def sample_iterative(self, alias, x, y):
        """Samples from the rule identified by `alias` in an iterative manner.

        Traverses the decomposition tree in post-order.
        The tree may be arbitrarily large and is expanded on the fly.
        """

        return self._IterativeSampler(self[alias]).sample(x, y)

    class _IterativeSampler(object):
        """

        Parameters
        ----------
        sampler: BoltzmannSamplerBase

        """

        def __init__(self, sampler):
            self.sampler = sampler

        class _ResultStack(list):
            """Modified stack that keeps track of the total l-size it contains."""

            def __init__(self):
                self.l_size = 0

            def append(self, obj):
                list.append(self, obj)
                # self.l_size += obj.l_size

            def pop(self):
                obj = list.pop(self)
                # self.l_size -= obj.l_size
                return obj

        def sample(self, x, y, max_size=1000000, abs_tolerance=0):
            """Invokes the iterative sampler for the given symbolic parameters.

            Parameters
            ----------
            x: str
            y: str
            max_size: int # TODO implement this
            abs_tolerance: int

            """
            # Main stack.
            stack = [self.sampler]
            # Stack that holds the intermediate sampling results.
            result_stack = self._ResultStack()
            # Stack that records variable substitutions.
            substitution_stack = []
            # The previously visited node in the decomposition tree.
            prev = None
            while stack:

                # Get top of stack.
                curr = stack[-1]

                # TODO find an optimal order of these if statements or, even better, refactor the code somehow so to not have this horrible case distinction

                no_prev_or_curr_in_prev_children = prev is None or curr in prev.get_children()

                if isinstance(curr, ProdSampler):
                    if no_prev_or_curr_in_prev_children:
                        stack.append(curr.lhs)
                    elif curr.lhs is prev:
                        # Left child has already been visited - visit right child.
                        stack.append(curr.rhs)
                    else:
                        # Both children have been processed.
                        stack.pop()
                        arg_rhs = result_stack.pop()
                        arg_lhs = result_stack.pop()
                        result_stack.append(curr.builder.product(arg_lhs, arg_rhs))

                elif isinstance(curr, SumSampler):
                    if no_prev_or_curr_in_prev_children:
                        if bern(curr.lhs.eval(x, y) / curr.eval(x, y)):
                            stack.append(curr.lhs)
                        else:
                            stack.append(curr.rhs)
                    else:
                        stack.pop()

                elif isinstance(curr, AliasSampler):
                    if no_prev_or_curr_in_prev_children:
                        stack.append(curr._referenced_sampler)
                    else:
                        stack.pop()

                elif isinstance(curr, AtomSampler):
                    # Atom samplers are the leaves in the decomposition tree.
                    stack.pop()
                    result_stack.append(curr.sample(x, y))

                elif isinstance(curr, SetSampler):
                    # We use recursion here for now.
                    stack.pop()
                    set_elems_sampler = curr.get_children().pop()
                    k = curr.draw_k(x, y)
                    sampler = self.__class__(set_elems_sampler)
                    set_elems = []
                    for _ in range(k):
                        obj = sampler.sample(x, y, max_size - result_stack.l_size, abs_tolerance)
                        set_elems.append(obj)
                    result_stack.append(curr.builder.set(set_elems))

                elif isinstance(curr, LDerFromUDerSampler):
                    if no_prev_or_curr_in_prev_children:
                        stack.append(curr.get_children().pop())
                    else:
                        obj_to_check = result_stack.pop()

                        def is_acceptable(gamma):
                            return bern((1 / curr._alpha_l_u) * (gamma.l_size / (gamma.u_size + 1)))

                        if is_acceptable(obj_to_check):
                            stack.pop()
                            result_stack.append(LDerivedClass(obj_to_check.base_class_object))
                        else:
                            stack.append(curr.get_children().pop())

                elif isinstance(curr, LSubsSampler):
                    if no_prev_or_curr_in_prev_children:
                        # Save the old x to the substitution stack.
                        substitution_stack.append(x)
                        x = curr.rhs.oracle_query_string(x, y)
                        # Sample from lhs with substituted x.
                        stack.append(curr.lhs)
                    else:
                        stack.pop()
                        # Get the object in which the l-atoms have to be replaced from the result stack.
                        core_object = result_stack.pop()
                        # Recover the old y from the stack.
                        x = substitution_stack.pop()
                        # Replace the atoms and push result.
                        sampler = self.__class__(curr.rhs)
                        res = core_object.replace_l_atoms(sampler, x, y)  # Recursion for now.
                        result_stack.append(res)

                elif isinstance(curr, RejectionSampler):
                    if no_prev_or_curr_in_prev_children:
                        stack.append(curr.get_children().pop())
                    else:
                        obj_to_check = result_stack.pop()
                        is_acceptable = curr.transformation  # This is kind of weird ...
                        if is_acceptable(obj_to_check):
                            stack.pop()
                            result_stack.append(obj_to_check)
                        else:
                            stack.append(curr.get_children().pop())

                elif isinstance(curr, USubsSampler):
                    if no_prev_or_curr_in_prev_children:
                        # Save the old y to the substitution stack.
                        substitution_stack.append(y)
                        y = curr.rhs.oracle_query_string(x, y)
                        # Sample from lhs with substituted y.
                        stack.append(curr.lhs)
                    else:
                        stack.pop()
                        # Get the object in which the u-atoms have to be replaced from the result stack.
                        core_object = result_stack.pop()
                        # Recover the old y from the stack.
                        y = substitution_stack.pop()
                        # Replace the atoms and push result.
                        sampler = self.__class__(curr.rhs)
                        res = core_object.replace_u_atoms(sampler, x, y)  # Recursion for now.
                        result_stack.append(res)

                elif isinstance(curr, UDerFromLDerSampler):
                    if no_prev_or_curr_in_prev_children:
                        stack.append(curr.get_children().pop())
                    else:
                        obj_to_check = result_stack.pop()

                        # TODO this code is duplicated in the recursive sampler
                        def is_acceptable(gamma):
                            return bern((1 / curr._alpha_u_l) * (gamma.u_size / (gamma.l_size + 1)))

                        if is_acceptable(obj_to_check):
                            stack.pop()
                            result_stack.append(UDerivedClass(obj_to_check.base_class_object))
                        else:
                            stack.append(curr.get_children().pop())

                else:
                    assert isinstance(curr, TransformationSampler)
                    if no_prev_or_curr_in_prev_children:
                        stack.append(curr.get_children().pop())
                    else:
                        stack.pop()
                        to_transform = result_stack.pop()
                        # A transformation may not be given.
                        if curr.transformation is not None:
                            result_stack.append(curr.transformation(to_transform))
                        else:
                            result_stack.append(to_transform)

                prev = curr

            assert len(result_stack) == 1
            return result_stack[0]

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
            self._grammar = None

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
            sampler.precompute_eval(self._x, self._y)
            if isinstance(sampler, LSubsSampler):
                self._stack_x.append((sampler.rhs, self._x))
                self._x = sampler.rhs.oracle_query_string(self._x, self._y)
            if isinstance(sampler, USubsSampler):
                self._stack_y.append((sampler.rhs, self._y))
                self._y = sampler.rhs.oracle_query_string(self._x, self._y)
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
