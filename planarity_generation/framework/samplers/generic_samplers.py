from framework.combinatorial_classes.generic_classes import *
from framework.utils import *
from framework.evaluation_oracle import Oracle


class BoltzmannSampler:
    # static class variable
    # not sure if this is an okay pattern
    oracle: Oracle = None

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

    def get_children(self):
        raise NotImplementedError

    def accept(self, visitor):
        visitor.visit(self)
        for child in self.get_children():
            child.accept(visitor)

    def sample(self, x: str, y: str) -> CombinatorialClass:
        """Invokes this sampler.

        :param x: symbolic x argument
        :param y: symbolic y argument
        """
        raise NotImplementedError

    # todo find a better name for this
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


### Atom Samplers ###

class AtomSampler(BoltzmannSampler):

    def get_children(self):
        # an atom does not have any children
        return []

    def sampled_class(self) -> str:
        raise NotImplementedError

    def get_eval(self, x: str, y: str) -> float:
        # see 3.2
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x: str, y: str) -> CombinatorialClass:
        raise NotImplementedError

    def oracle_query_string(self, x: str, y: str) -> str:
        raise NotImplementedError


class ZeroAtom(AtomSampler):

    def sampled_class(self):
        return '1'

    def oracle_query_string(self, x, y):
        # '1' is actually never an oracle query because it's trivial but anyway
        return '1'

    def get_eval(self, x, y):
        # see 3.2
        return 1

    def sample(self, x, y):
        # we *cannot* use singletons here
        return ZeroAtomClass()


class LAtom(AtomSampler):
    def sampled_class(self):
        return 'L'

    def oracle_query_string(self, x, y):
        return x

    def sample(self, x, y):
        return LAtomClass()


class UAtom(AtomSampler):
    def sampled_class(self):
        return 'U'

    def oracle_query_string(self, x, y):
        return y

    def sample(self, x, y):
        return UAtomClass()


### Binary samplers - depend on two other samplers ###

class BinarySampler(BoltzmannSampler):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def get_children(self):
        return [self.lhs, self.rhs]

    def sampled_class(self) -> str:
        raise NotImplementedError

    def get_eval(self, x: str, y: str) -> float:
        raise NotImplementedError

    def sample(self, x: str, y: str) -> CombinatorialClass:
        raise NotImplementedError

    def oracle_query_string(self, x: str, y: str) -> str:
        raise NotImplementedError


class Sum(BinarySampler):
    def __init__(self, lhs, rhs):
        super(Sum, self).__init__(lhs, rhs)

    def sampled_class(self):
        return '(' + self.lhs.getAlias() + '+' + self.rhs.getAlias() + ')'

    def oracle_query_string(self, x, y):
        return self.lhs.oracle_query_string(x, y) + '+' + self.rhs.oracle_query_string(x, y)

    def get_eval(self, x, y):
        # see 3.2
        # for sum class (= disjoint union) the generating function is the sum of the 2 generating functions
        return self.lhs.get_eval(x, y) + self.rhs.get_eval(x, y)

    def sample(self, x, y):
        # todo this can be made more efficient (self.get_eval also evaluates self.lhs.get_eval)
        if bern(self.lhs.get_eval(x, y) / self.get_eval(x, y)):
            return self.lhs.sample(x, y)
        else:
            return self.rhs.sample(x, y)


class Prod(BinarySampler):
    def __init__(self, lhs, rhs):
        super(Prod, self).__init__(lhs, rhs)

    def sampled_class(self):
        return '(' + self.lhs.getAlias() + '*' + self.rhs.getAlias() + ')'

    def oracle_query_string(self, x, y):
        return self.lhs.oracle_query_string(x, y) + '*' + self.rhs.oracle_query_string(x, y)

    def get_eval(self, x, y):
        # see 3.2
        return self.lhs.get_eval(x, y) * self.rhs.get_eval(x, y)

    def sample(self, x, y):
        return ProdClass(self.lhs.sample(x, y), self.rhs.sample(x, y))


class LSubs(BinarySampler):
    def __init__(self, lhs, rhs):
        super(LSubs, self).__init__(lhs, rhs)

    def sampled_class(self):
        return '(' + self.lhs.sampled_class() + ' lsubs ' + self.rhs.sampled_class() + ')'

    def oracle_query_string(self, x, y):
        # see 3.2
        # A(B(x,y),y) where A = lhs and B = rhs
        return self.lhs.oracle_query_string(self.rhs.oracle_query_string(x, y), y)

    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        gamma = self.lhs.sample(self.rhs.oracle_query_string(x, y), y)
        gamma.replace_l_atoms(self.rhs.sample, x, y)
        return gamma


class USubs(BinarySampler):
    def __init__(self, lhs, rhs):
        super(USubs, self).__init__(lhs, rhs)

    def sampled_class(self):
        return '(' + self.lhs.sampled_class() + ' usubs ' + self.rhs.sampled_class() + ')'

    def oracle_query_string(self, x, y):
        return self.lhs.oracle_query_string(x, self.rhs.oracle_query_string(x, y))

    # see 3.2
    def get_eval(self, x, y):
        # A(x,B(x,y)) where A = lhs and B = rhs
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        gamma = self.lhs.sample(x, self.rhs.oracle_query_string(x, y))
        gamma.replace_u_atoms(self.rhs.sample, x, y)
        return gamma


### Unary samplers - depend on one other sampler ###

class UnarySampler(BoltzmannSampler):
    def __init__(self, sampler):
        self.sampler = sampler

    def get_children(self):
        return [self.sampler]

    def sampled_class(self):
        raise NotImplementedError

    def get_eval(self, x, y):
        raise NotImplementedError

    def sample(self, x, y):
        raise NotImplementedError

    def oracle_query_string(self, x, y):
        raise NotImplementedError


class Set(UnarySampler):
    def __init__(self, d, sampler):
        super(Set, self).__init__(sampler)
        self.d = d

    def sampled_class(self):
        return 'Set_' + self.d + '(' + self.sampler.sampled_class() + ')'

    def oracle_query_string(self, x, y):
        return 'exp_' + str(self.d) + '(' + self.sampler.oracle_query_string(x, y) + ')'

    def get_eval(self, x, y):
        # see 3.2
        return exp_tail(self.d, self.sampler.get_eval(x, y))

    def sample(self, x, y):
        k = pois(self.d, self.sampler.get_eval(x, y))
        return SetClass([self.sampler.sample(x, y) for _ in range(k)])


# u-derived sampler from l-derived sampler
class UDerFromLDer(UnarySampler):
    def __init__(self, sampler, alpha_u_l):
        super(UDerFromLDer, self).__init__(sampler)
        self.alpha_u_l = alpha_u_l

    def sampled_class(self):
        l_der_alias = self.sampler.sampled_class()
        # assume that l_der_alias = X_dx
        # discard the last symbol two symbols (dx) and append dy
        return l_der_alias[0:len(l_der_alias) - 2] + 'dy'

    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    # see lemma 6
    def sample(self, x, y):
        while True:
            gamma = self.sampler.sample(x, y)
            p = (1 / self.alpha_u_l) * (gamma.get_u_size() / (gamma.get_l_size() + 1))
            if bern(p):
                gamma = gamma.get_base_class_object()
                rand_u_atom = gamma.random_u_atom()
                return UDerivedClass(gamma, rand_u_atom)

    def oracle_query_string(self, x: str, y: str) -> str:
        return self.sampled_class() + '(' + x + ',' + y + ')'


class LDerFromUDer(UnarySampler):
    def __init__(self, sampler, alpha_l_u):
        # sampler is a sampler for the u-derived class
        super(LDerFromUDer, self).__init__(sampler)
        self.alpha_l_u = alpha_l_u

    def sampled_class(self):
        u_der_class = self.sampler.sampled_class()
        # assume u_der_class = X_dy
        return u_der_class[0:len(u_der_class) - 2] + 'dx'

    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        while True:
            gamma = self.sampler.sample(x, y)
            p = (1 / self.alpha_l_u) * (gamma.get_l_size() / (gamma.get_u_size() + 1))
            if bern(p):
                gamma = gamma.get_base_class_object()
                rand_l_atom = gamma.random_l_atom()
                return LDerivedClass(gamma, rand_l_atom)

    def oracle_query_string(self, x: str, y: str) -> str:
        return self.sampled_class() + '(' + x + ',' + y + ')'


class Bijection(UnarySampler):
    def __init__(self, sampler, f, target_class_label=None):
        # sampler is a sampler of the underlying class
        super(Bijection, self).__init__(sampler)
        # f is the bijection from the underlying class to the target class
        self.f = f
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


# generic sampler that transforms the the objects sampled from the base class to a new class
# is not an isomorphism, for isomorphisms use Bijection
class Transformation(UnarySampler):
    def __init__(self, sampler, f, target_class_label):
        # sampler is a sampler of the underlying class
        super(Transformation, self).__init__(sampler)
        # f is the function from the underlying class to the target class
        self.f = f
        # this is how the class resulting from this rejection is called (for the oracle)
        self.target_class_label = target_class_label

    def sampled_class(self):
        return self.target_class_label

    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        # sample from the underlying class and apply the bijection
        return self.f(self.sampler.sample(x, y))

    def oracle_query_string(self, x: str, y: str) -> str:
        return self.sampled_class() + '(' + x + ',' + y + ')'


# generic rejection sampler, special case of transformation
class Rejection(Transformation):
    def __init__(self, sampler, is_acceptable, target_class_label):
        # sampler is a sampler of the underlying class
        super(Rejection, self).__init__(sampler, None, target_class_label)
        # this is a function that takes a structure and outputs true iff it matches the acceptance criteria
        self.is_acceptable = is_acceptable

    def sample(self, x, y):
        gamma = self.sampler.sample(x, y)
        while not self.is_acceptable(gamma):
            gamma = self.sampler.sample(x, y)
        return gamma
