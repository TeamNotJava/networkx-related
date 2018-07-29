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

from __future__ import division, print_function
import math

from framework.decomposition_grammar import *
from framework.evaluation_oracle import EvaluationOracle

# TODO make some reasonable things here or delete
from framework.generic_samplers import BoltzmannSamplerBase


def dummy_sampling():
    print("Dummy sampling example.\n-----------------------\n")
    L = LAtomSampler()
    Tree = AliasSampler('Tree')

    tree_grammar = DecompositionGrammar()
    tree_grammar.rules = {
        # Tree is either a leaf or inner node with two children which are trees.
        'Tree': L + L * Tree ** 2,
    }
    # init the grammar
    tree_grammar.init()
    tree_grammar.dummy_sampling_mode()

    def get_x_for_size(n):
        return math.sqrt(n ** 2 - 1) / (2 * n)

    def eval_T(x):
        return (math.sqrt(1 - 4 * x ** 2) + 1) / (2 * x)

    def eval_T_dx(x):
        return (1 / (math.sqrt(1 - 4 * x ** 2)) + 1) / (2 * x ** 2)

    target_size = 10
    x = get_x_for_size(target_size)
    T = eval_T(x)
    T_dx = eval_T_dx(x)
    tree_oracle = EvaluationOracle({
        'x': x,
        'Tree(x,y)': T,
        'Tree_dx(x,y)': T_dx
    })

    # Inject the oracle into the samplers.
    BoltzmannSamplerBase.oracle = tree_oracle

    print(tree_grammar.collect_oracle_queries('Tree', 'x', 'y'))

    num_samples = 10
    while True:
        try:
            trees = [tree_grammar.sample('Tree', 'x', 'y') for _ in range(num_samples)]
            break
        except RecursionError:
            pass
    print(sum([tree.l_size for tree in trees]) / len(trees))


def natural_numbers():
    print("Natural numbers example.\n------------------------\n")

    # Define some shortcuts to make the grammar more readable.
    One = UAtomSampler()
    Zero = ZeroAtomSampler()
    N = AliasSampler('N')

    # Define the grammar and initialize.
    grammar = DecompositionGrammar({
        # A natural number is either zero or the successor (+1) of another natural number.
        'N': Zero + One * N
    })
    grammar.init()

    y = 0.95
    N = 1 / (1 - y)
    N_dy = 1 / (1 - y) ** 2
    oracle = EvaluationOracle({
        'y': y,
        'N(x,y)': N
    })
    BoltzmannSamplerBase.oracle = oracle
    grammar.precompute_evals('N', 'x', 'y')
    print("expected number: {}".format(y * N_dy / N))
    num_samples = 10
    numbers = [grammar.sample('N', 'x', 'y') for _ in range(num_samples)]
    avg_size = sum(n.u_size for n in numbers) / num_samples
    print("average in {} trials: {}".format(num_samples, avg_size))


def integer_partitions():
    print("Integer partitions example.\n---------------------------\n")

    # Define some shortcuts to make the grammar more readable.
    U = UAtomSampler
    Set = SetSampler
    USubs = USubsSampler
    Bij = BijectionSampler
    Rule = AliasSampler

    class Partition(SetClass):
        def __init__(self, numbers):
            super(Partition, self).__init__(numbers)

        @property
        def u_size(self):
            return sum(iter(self))

    def to_partition(p):
        return Partition([n.u_size for n in p])

    # Define the grammar and initialize.
    grammar = DecompositionGrammar({
        # A natural number is either zero or the successor (+1) of another natural number.
        'N': U() + U() * Rule('N'),
        'P': Bij(USubs(Set(1, U()), Rule('N')), to_partition)
    })
    grammar.init()
    print("Needed oracle entries for sampling: {}\n".format(grammar.collect_oracle_queries('P', 'x', 'y')))

    y = 0.56
    N = y / (1 - y)
    P = math.exp(N) - 1
    P_dy = math.exp(N) / (1 - y) ** 2
    oracle = EvaluationOracle({
        'y': y,
        'N(x,y)': N,
    })
    BoltzmannSamplerBase.oracle = oracle
    print("expected number: {}\n".format(y * P_dy / P))
    target_size = 4
    num_samples = 100
    partitions = []
    while len(partitions) < num_samples:
        p = grammar.sample('P', 'x', 'y')
        if p.u_size == target_size:
            partitions.append(p)

    for i in range(1, 5):
        print("number of partitions into {} numbers: {}".format(i, len([p for p in partitions if len(p) == i])))

    # We can observe that the distribution is not uniform, thus we did *not* actually describe the class of integer
    # partitions correctly (which is much more complicated).


def set_partitions():
    print("Set partitions example.\n-----------------------\n")

    # In this examples, we ...

    L = LAtomSampler()
    Set = SetSampler

    def eval_P(x):
        return math.exp(math.exp(x) - 1)

    def expected_size(x):
        return x * math.exp(x)

    grammar = DecompositionGrammar({
        'P': Set(0, Set(1, L))
    })
    grammar.init()

    oracle = EvaluationOracle({
        'x': 1.05
    })
    BoltzmannSamplerBase.oracle = oracle
    partition = grammar.sample('P', 'x', 'y')
    partition.assign_random_labels()

    print("expected size of set: {}\n".format(expected_size(oracle.get('x'))))
    print(partition)


def binary_trees():
    print("Binary tree example.\n--------------------\n")

    def height(tree):
        if isinstance(tree, LAtomClass):
            return 1
        else:
            assert isinstance(tree, ProdClass)
            return max(height(tree._second._first), height(tree._second._second)) + 1

    # Define the grammar.

    # Define some shortcuts for readability.
    L = LAtomSampler
    _ = AliasSampler

    # Initialize a grammar object and set the sampling rules (in this case just one single rule).
    tree_grammar = DecompositionGrammar({
        # A binary tree is either a leaf or an inner node with two children that are binary trees.
        'T': L() + L() * _('T') ** 2
    })

    # Set the builder information and initialize the grammar.
    # tree_grammar.set_builder(['T'], BinaryTreeBuilder())
    tree_grammar.init()

    # Do the mathematical stuff.

    def get_x_for_size(n):
        return math.sqrt(n ** 2 - 1) / (2 * n)

    def eval_T(x):
        return (math.sqrt(1 - 4 * x ** 2) + 1) / (2 * x)

    def eval_T_dx(x):
        return (1 / (math.sqrt(1 - 4 * x ** 2)) + 1) / (2 * x ** 2)

    target_size = 10
    x = get_x_for_size(target_size)
    T = eval_T(x)
    T_dx = eval_T_dx(x)
    tree_oracle = EvaluationOracle({
        'x': x,
        'T(x,y)': T,
        'T_dx(x,y)': T_dx
    })
    # Set the newly created oracle as the active oracle.
    BoltzmannSamplerBase.oracle = tree_oracle

    print("expected size of the trees: {}\n".format(tree_oracle.get_expected_l_size('T', 'x', 'y')))
    print("needed oracle entries for sampling: {}\n".format(tree_grammar.collect_oracle_queries('T', 'x', 'y')))

    num_samples = 10
    while True:
        try:
            trees = [tree_grammar.sample('T', 'x', 'y') for _ in range(num_samples)]
            break
        except RecursionError:
            pass
    avg_size = sum([tree.l_size for tree in trees]) / num_samples
    print("average size in {} trials: {}".format(num_samples, avg_size))
    avg_height = sum([height(tree) for tree in trees]) / num_samples
    print("average height of trees: {}".format(avg_height))

    print(2 * math.sqrt(math.pi * avg_size / 2))


def test_examples():
    examples = [
        natural_numbers,
        binary_trees,
        integer_partitions,
        set_partitions,
        dummy_sampling
    ]
    for example in examples:
        example()
        print('\n')


if __name__ == "__main__":
    # random.seed(123456)
    test_examples()
