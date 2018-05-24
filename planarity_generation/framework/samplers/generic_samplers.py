from framework.combinatorial_classes.generic_classes import *
from framework.utils import *
from framework.evaluation_oracle import Oracle
from framework.decomposition_grammar import DecompositionGrammar


class BoltzmannSampler:
    # shared accross all instances
    # not sure if this is an okay pattern
    oracle: Oracle = None
    # todo only the Alias sampler needs the active_grammar, so maybe it should just be there
    active_grammar: DecompositionGrammar = None

    def sampled_class(self) -> str:
        """Returns a string representation of the sampled class.
        maybe nice to have for debugging

        """
        raise NotImplementedError

    def get_eval(self, x: str, y: str) -> float:
        """Gets the evaluation of the generating function of the class being sampled

        Possibly queries the oracle directly or indirectly.
        :param x: symbolic x argument
        :param y: symbolic y argument
        """
        raise NotImplementedError

    def sample(self, x: str, y: str) -> CombinatorialClass:
        """Invokes this sampler.

        :param x: symbolic x argument
        :param y: symbolic y argument
        """
        raise NotImplementedError

    def oracle_query_string(self, x: str, y: str) -> str:
        """String used as key in oracle.

        This is like a 'symbolic evaluation' of the generating function of the class being sampled from.
        :param x: symbolic x argument
        :param y: symbolic y argument
        """
        raise NotImplementedError

    def __add__(self, other):
        """Sum construction of samplers.

        Comes in very handy when writing the grammars
        :param other: The right hand side argument.
        :return: The sum-sampler resulting from this sampler and the given sampler.
        """
        return Sum(self, other)

    def __mul__(self, other):
        """Product construction of samplers.

        Comes in very handy when writing the grammars
        :param other: The right hand side argument.
        :return: The product-sampler resulting from this sampler and the given sampler.
        """
        return Prod(self, other)


class ZeroAtom(BoltzmannSampler):
    def sampled_class(self):
        return '1'

    def oracle_query_string(self, x, y):
        return '1'

    # see 3.2
    def get_eval(self, x, y):
        return 1

    def sample(self, x, y):
        # we *cannot* use singletons here
        return ZeroAtomClass()


class LAtom(BoltzmannSampler):
    def sampled_class(self):
        return 'L'

    def oracle_query_string(self, x, y):
        return x

    # see 3.2
    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        return LAtomClass()


class UAtom(BoltzmannSampler):
    def sampled_class(self):
        return 'U'

    def oracle_query_string(self, x, y):
        return y

    # see 3.2
    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        return UAtomClass()


class Sum(BoltzmannSampler):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def sampled_class(self):
        return '(' + self.lhs.getAlias() + '+' + self.rhs.getAlias() + ')'

    def oracle_query_string(self, x, y):
        return self.lhs.oracle_query_string(x, y) + '+' + self.rhs.oracle_query_string(x, y)

    # see 3.2
    def get_eval(self, x, y):
        # for sum class (= disjoint union) the generating function is the sum of the 2 generating functions
        return self.lhs.get_eval(x, y) + self.rhs.get_eval(x, y)

    def sample(self, x, y):
        # this can be made more efficient (self.get_eval also evaluates self.lhs.get_eval)
        if bern(self.lhs.get_eval(x, y) / self.get_eval(x, y)):
            return self.lhs.sample(x, y)
        else:
            return self.rhs.sample(x, y)


class Prod(BoltzmannSampler):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def sampled_class(self):
        return '(' + self.lhs.getAlias() + '*' + self.rhs.getAlias() + ')'

    def oracle_query_string(self, x, y):
        return self.lhs.oracle_query_string(x, y) + '*' + self.rhs.oracle_query_string(x, y)

    # see 3.2
    def get_eval(self, x, y):
        return self.lhs.get_eval(x, y) * self.rhs.get_eval(x, y)

    def sample(self, x, y):
        return ProdClass(self.lhs.sample(x, y), self.rhs.sample(x, y))


class Set(BoltzmannSampler):
    def __init__(self, d, arg):
        self.d = d
        # arg is the class being sampled from
        self.arg = arg

    def sampled_class(self):
        return 'Set_' + self.d + '(' + self.arg.sampled_class() + ')'

    def oracle_query_string(self, x: str, y: str):
        return 'exp_' + self.d + '(' + self.arg.oracle_query_string(x, y) + ')'

    # see 3.2
    def get_eval(self, x, y):
        return exp_tail(self.d, self.arg.get_eval(x, y))

    def sample(self, x, y):
        k = pois(self.d, self.arg.get_eval(x, y))
        return SetClass([self.arg.sample(x, y) for _ in range(k)])


class LSubs(BoltzmannSampler):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def sampled_class(self):
        return '(' + self.lhs.sampled_class() + ' lsubs ' + self.rhs.sampled_class() + ')'

    def oracle_query_string(self, x: str, y: str):
        # A(B(x,y),y) where A = lhs and B = rhs
        return self.lhs.oracle_query_string(self.rhs.oracle_query_string(x, y), y)

    # see 3.2
    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        gamma = self.lhs.sample(self.rhs.get_eval(x, y), y)
        gamma.replace_l_atoms(self.rhs.sample, x, y)
        return gamma


class USubs(BoltzmannSampler):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def sampled_class(self):
        return '(' + self.lhs.sampled_class() + ' usubs ' + self.rhs.sampled_class() + ')'

    def oracle_query_string(self, x: str, y: str):
        return self.lhs.oracle_query_string(x, self.rhs.oracle_query_string(x, y))

    # see 3.2
    def get_eval(self, x, y):
        # A(x,B(x,y)) where A = lhs and B = rhs
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        gamma = self.lhs.sample(x, self.rhs.get_eval(x, y))
        gamma.replace_u_atoms(self.rhs.sample, x, y)
        return gamma


# An alias sampler is a sampler defined by a rule in a decomposition grammar.
# The rule can contain the same alias sampler itself.
# This allows to implement recursive decompositions.
class Alias(BoltzmannSampler):
    def __init__(self, alias):
        self.alias = alias

    def sampled_class(self):
        return self.alias

    def oracle_query_string(self, x: str, y: str):
        return self.alias + '(' + x + ',' + y + ')'

    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        return self.active_grammar.sample(self.alias, x, y)


# u-derived sampler from l-derived sampler
class UDerFromLDer(BoltzmannSampler):
    def __init__(self, l_der_sampler, alpha_u_l):
        # l_der_sampler is a sampler for the l-derived class
        self.l_der_sampler = l_der_sampler
        self.alpha_u_l = alpha_u_l

    def sampled_class(self):
        l_der_alias = self.l_der_sampler.sampled_class()
        # assume that l_der_alias = X_dx
        # discard the last symbol two symbols (dx) and append dy
        return l_der_alias[0:len(l_der_alias) - 2] + 'dy'

    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    # see lemma 6
    def sample(self, x, y):
        while True:
            gamma = self.l_der_sampler.sample(x, y)
            p = (1 / self.alpha_u_l) * (gamma.get_u_size() / (gamma.get_l_size() + 1))
            if bern(p):
                gamma = gamma.get_base_class_object()
                rand_u_atom = gamma.random_u_atom()
                return UDerivedClass(gamma, rand_u_atom)

    def oracle_query_string(self, x: str, y: str) -> str:
        return self.sampled_class() + '(' + x + ',' + y + ')'


class LDerFromUDer(BoltzmannSampler):
    def __init__(self, u_der_sampler, alpha_l_u):
        # u_der_sampler is a sampler for the u-derived class
        self.u_der_sampler = u_der_sampler
        self.alpha_l_u = alpha_l_u

    def sampled_class(self) -> str:
        u_der_class = self.u_der_sampler.sampled_class()
        # assume u_der_class = X_dy
        return u_der_class[0:len(u_der_class) - 2] + 'dx'

    def get_eval(self, x: str, y: str) -> float:
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x: str, y: str) -> CombinatorialClass:
        while True:
            gamma = self.u_der_sampler.sample(x, y)
            p = (1 / self.alpha_l_u) * (gamma.get_l_size() / (gamma.get_u_size() + 1))
            if bern(p):
                gamma = gamma.get_base_class_object()
                rand_l_atom = gamma.random_l_atom()
                return LDerivedClass(gamma, rand_l_atom)

    def oracle_query_string(self, x: str, y: str) -> str:
        return self.sampled_class() + '(' + x + ',' + y + ')'


class Bijection(BoltzmannSampler):
    def __init__(self, sampler, f, target_class_label=None):
        # f is the bijection from the underlying class to the target class
        self.f = f
        # sampler is a sampler of the underlying class
        self.sampler = sampler
        # optional label of target class
        self.target_class_label = target_class_label

    def sampled_class(self):
        # todo maybe this doesn't make too much sense but I don't know what would be better
        return self.target_class_label

    def get_eval(self, x, y):
        return self.sampler.get_eval(x, y)

    def sample(self, x, y):
        # sample from the underlying class and apply the bijection
        return self.f(self.sampler.sample(x, y))

    def oracle_query_string(self, x: str, y: str) -> str:
        return self.sampler.oracle_query_string(x, y)


# generic rejection sampler
class Rejection(BoltzmannSampler):
    def __init__(self, sampler, is_acceptable, target_class_label=None):
        self.sampler = sampler
        self.is_acceptable = is_acceptable
        # this is how the class resulting from this rejection is called (for the oracle)
        self.target_class_label = target_class_label

    def sampled_class(self) -> str:
        # todo not really sure what to do here
        return self.target_class_label

    def get_eval(self, x: str, y: str) -> float:
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        gamma = self.sampler.sample(x, y)
        while not self.is_acceptable(gamma):
            gamma = self.sampler.sample(x, y)
        return gamma

    def oracle_query_string(self, x: str, y: str) -> str:
        # we're proabaly not going to need this anyway
        return self.target_class_label + '(' + x + ',' + y + ')'
