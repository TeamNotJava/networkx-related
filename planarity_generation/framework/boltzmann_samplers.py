from .combinatorial_classes.generic_classes import *
from .combinatorial_classes.three_connected_graph import EdgeRootedThreeConnectedPlanarGraph
from .utils import *
import networkx as nx


class BoltzmannSampler:
    # shared accross all instances
    # not sure if this is an okay pattern
    oracle = None
    active_grammar = None

    # returns a string representation of the sampled class
    # is basically used to query the oracle
    def get_alias(self):
        raise NotImplementedError

    # gets the evaluation of the generating function of the class being sampled
    def get_eval(self, x, y):
        raise NotImplementedError

    # samples from the uderlying class
    # x and y are always *symbols* no actual number!
    def sample(self, x, y):
        raise NotImplementedError

    # string used as key in oracle
    def oracle_query_string(self, x, y):
        return self.get_alias() + '(' + x + ',' + y + ')'

    # comes in very handy when writing the grammars
    def __add__(self, other):
        return Sum(self, other)

    def __mul__(self, other):
        return Prod(self, other)


class ZeroAtom(BoltzmannSampler):
    def get_alias(self):
        return '1'

    # see 3.2
    def get_eval(self, x, y):
        return 1

    def sample(self, x, y):
        # we *cannot* use singletons here
        return ZeroAtomClass()


class LAtom(BoltzmannSampler):
    def get_alias(self):
        return 'L'

    # see 3.2
    def get_eval(self, x, y):
        return self.oracle.get(x)

    def sample(self, x, y):
        return LAtomClass()


class UAtom(BoltzmannSampler):
    def get_alias(self):
        return 'U'

    # see 3.2
    def get_eval(self, x, y):
        return self.oracle.get(y)

    def sample(self, x, y):
        return UAtomClass()


class Sum(BoltzmannSampler):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def get_alias(self):
        return '(' + self.lhs.getAlias() + '+' + self.rhs.getAlias() + ')'

    # see 3.2
    def get_eval(self, x, y):
        # for sum class (= disjoint union) the generating function is the sum of the 2 generating functions
        return self.lhs.get_eval(x, y) + self.rhs.get_eval(x, y)

    def sample(self, x, y):
        # this can be made more efficient!
        if bern(self.lhs.get_eval(x, y) / self.get_eval(x, y)):
            return self.lhs.sample(x, y)
        else:
            return self.rhs.sample(x, y)


class Prod(BoltzmannSampler):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def get_alias(self):
        return '(' + self.lhs.getAlias() + '*' + self.rhs.getAlias() + ')'

    # see 3.2
    def get_eval(self, x, y):
        assert self.lhs and self.rhs
        return self.lhs.get_eval(x, y) * self.rhs.get_eval(x, y)

    def sample(self, x, y):
        return ProdClass(self.lhs.sample(x, y), self.rhs.sample(x, y))


class Set(BoltzmannSampler):
    def __init__(self, d, arg):
        self.d = d
        self.arg = arg

    def get_alias(self):
        return 'Set_' + self.d + '(' + self.arg.get_alias() + ')'

        # see 3.2

    def get_eval(self, x, y):
        return exp_tail(self.d, self.arg.get_eval(x, y))

    def sample(self, x, y):
        k = pois(self.d, self.arg.get_eval(x, y))
        return SetClass([self.arg.sample(x, y) for _ in range(0, k)])


class LSubs(BoltzmannSampler):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def get_alias(self):
        return '(' + self.lhs.getAlias() + ' lsubs ' + self.rhs.getAlias() + ')'

    # see 3.2
    def get_eval(self, x, y):
        # todo: is this correct or does x or y have to be replace by somethin?
        self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        gamma = self.lhs.sample(self.rhs.get_eval(x, y), y)
        gamma.replace_l_atoms(self.rhs.sample, x, y)
        return gamma


class USubs(BoltzmannSampler):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def get_alias(self):
        return '(' + self.lhs.getAlias() + ' usubs ' + self.rhs.getAlias() + ')'

    # see 3.2
    def get_eval(self, x, y):
        # todo: is this correct or does x or y have to be replace by somethin?
        self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        gamma = self.lhs.sample(x, self.rhs.get_eval(x, y))
        gamma.replace_u_atoms(self.rhs.sample, x, y)
        return gamma


# An alias class is a class defined by a rule in a decomposition grammar.
# The rule can contain the same alias class itself.
# This allows to implement recursive decompositions.
class Alias(BoltzmannSampler):
    def __init__(self, alias):
        self.alias = alias

    def get_alias(self):
        return self.alias

    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        assert self.active_grammar  # must be set
        return self.active_grammar.sample(self.alias, x, y)


class SpecialSampler1(BoltzmannSampler):
    def __init__(self, something):
        pass


class SpecialSampler2(BoltzmannSampler):
    def __init__(self, something):
        pass


# u-derived sampler from l-derived sampler
class UDerFromLDer(BoltzmannSampler):
    def __init__(self, l_der_sampler, alpha_u_l):
        # l_der_sampler is a sampler for the l-derived class
        self.l_der_sampler = l_der_sampler
        self.alpha_u_l = alpha_u_l

    def get_alias(self):
        l_der_alias = self.l_der_sampler.get_alias()
        # discard the last symbol (') and append _
        return l_der_alias[0:len(l_der_alias) - 1] + '_'

    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    # see lemma 6
    def sample(self, x, y):
        while True:
            gamma = self.l_der_sampler.sample(x, y)
            p = (1 / self.alpha_u_l) * (gamma.get_u_size() / (gamma.get_l_size() + 1))
            if bern(p):
                gamma = gamma.get_underlying_structure()
                rand_u_atom = gamma.random_u_atom()
                return UDerivedClass(gamma, rand_u_atom)


class LDerFromUDer(BoltzmannSampler):
    def __init__(self, u_der_sampler, alpha_l_u):
        pass


class Bijection(BoltzmannSampler):
    def __init__(self, sampler, f):
        # f is the bijection from the underlying class to the target class
        self.f = f
        # sampler is a sampler of the underlying class
        self.sampler = sampler

    def get_alias(self):
        # not quire sure about this
        return self.sampler.get_alias()

    def get_eval(self, x, y):
        return self.sampler.get_eval(x, y)

    def sample(self, x, y):
        # sample from the underlying class and apply the bijection
        return self.f(self.sampler.sample(x, y))


# this is a dummy in the current version
class EdgeRootedThreeConnectedPlanarGraphSampler(BoltzmannSampler):
    def init__(self):
        pass

    def get_alias(self):
        return 'G_3_arrow'

    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        # todo this is a dummy
        graph = nx.Graph()
        graph.add_edges_from([
            (1, 3),
            (1, 7),
            (1, 6),
            (6, 7),
            (7, 4),
            (6, 5),
            (4, 5),
            (4, 3),
            (3, 2),
            (4, 2),
            (2, 5)
        ])
        root_edge = (1, 2)
        return EdgeRootedThreeConnectedPlanarGraph(graph, root_edge)


class LDerThreeConnectedPlanarGraphSampler(BoltzmannSampler):
    pass
