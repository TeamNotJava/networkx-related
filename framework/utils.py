# -*- coding: utf-8 -*-
import random as rnd
from math import exp, pow, factorial
import itertools


# Returns the nth item or a default value
# also works for a generator
def nth(iterable, n, default=None):
    return next(itertools.islice(iterable, n, None), default)


# tail of the exponential series starting at d
# needed in the set sampler
def exp_tail(d, x):
    result = exp(x)
    # subtract the first d terms
    for k in range(d):
        result -= pow(x, k) / factorial(k)
    return result


# probability distributions

# bernoulli
def bern(p):
    return rnd.uniform(0, 1) <= p


# poisson
# todo: implement properly
# c.f. duchon et al ... chapter 5
# the scheme stated there seems to contain a mistake
def pois_value(k, l):
    if k == 0:
        return exp(-l)
    else:
        return l * pois_value(k - 1, l) / k


def pois_prob(k, l):
    return exp(-l) * pow(l, k) / factorial(k)


def pois_try(d, l):
    u = rnd.uniform(0, 1)
    s = 0
    k = d
    while s < u:
        k += 1
        s += pois_value(k, l)
    return k


# currently used for pois
def pois(d, l):
    f = exp_tail(d, l)
    F = f
    k = 1
    u = rnd.uniform(0, 1)
    while (F < u):
        f = l / k * f
        F = F + f
        k = k + 1
    return k - 1
