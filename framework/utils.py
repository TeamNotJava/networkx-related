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

import random

from math import exp, pow, factorial
import itertools

boltzmann_framework_random_gen = random.Random()


def nth(iterable, n, default=None):
    """Returns the nth item or a default value, also works for a generator."""
    return next(itertools.islice(iterable, n, None), default)


def bern(p):
    """Bernoulli generator.

    Parameters
    ----------
    p: float

    Returns
    -------
    bool
    """
    # assert 0 <= p <= 1
    return boltzmann_framework_random_gen.uniform(0, 1) <= p


def exp_tail(d, x):
    """Tail of the exponential series starting at d. Needed in the set sampler.

    Parameters
    ----------
    d: int
    x: float

    Returns
    -------
    float
    """

    result = exp(x)
    # Subtract the _first _d terms.
    for i in range(d):
        result -= (pow(x, i) / factorial(i))
    return result


def pois_prob(d, k, l):
    """Poisson probability.

    Parameters
    ----------
    d: int
    k: int
    l: float

    Returns
    -------
    float
    """
    return 1 / exp_tail(d, l) * pow(l, k) / factorial(k)


def pois(d, l):
    """
    Poisson generator.

    Parameters
    ----------
    d: int
    l: float

    Returns
    -------
    int
    """
    u = boltzmann_framework_random_gen.uniform(0, 1)
    s = 0
    k = d
    p = pois_prob(d, k, l)
    while True:
        s += p
        if s >= u:
            return k
        k += 1
        p *= l / k
