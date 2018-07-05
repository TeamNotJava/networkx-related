# -*- coding: utf-8 -*-
import random as rnd
from math import exp, pow, factorial
import itertools


# Returns the nth item or a default value
# also works for a generator
def nth(iterable, n, default=None):
    return next(itertools.islice(iterable, n, None), default)


# probability distributions

# bernoulli
def bern(p):
    return rnd.uniform(0, 1) <= p


# poisson
# todo: implement properly
# c.f. duchon et al ... chapter 5

# tail of the exponential series starting at d
# needed in the set sampler
def exp_tail(d, x):
    result = exp(x)
    # subtract the first d terms
    for i in range(d):
        result -= (pow(x, i) / factorial(i))
    return result

def pois_prob(d, k, l):
    return 1 / exp_tail(d, l) * pow(l, k) / factorial(k)


def pois(d, l):
    u = rnd.uniform(0,1)
    s = 0
    k = d
    p = pois_prob(d, k, l)
    while True:
        s += p
        if s >= u:
            return k
        k += 1
        p *= l / k


def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class Counter(object):
    def __init__(self):
        self.count = 0
    def __iter__(self):
        return self
    def __next__(self):
        count = self.count
        self.count += 1
        return count


