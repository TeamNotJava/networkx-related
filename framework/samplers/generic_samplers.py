from framework.combinatorial_classes.generic_classes import *
from framework.utils import *
from framework.combinatorial_classes import CombinatorialClass


# All references in comments in this file refer to:
# "E. Fusy: Uniform Random Sampling of Planar Graphs in Linear Time"

class BoltzmannSampler:
    """Abstract base class for Boltzmann samplers.

    Attributes:
        oracle  The oracle to be used by all instantiations of this class.
    """

    oracle = None

    def sampled_class(self):
        """Returns a string representation of the sampled class.

        :rtype: str
        """
        raise NotImplementedError

    def sample(self, x, y):
        """Invokes this sampler with the given x and y parameters.

        :param x: symbolic x argument
        :param y: symbolic y argument
        :rtype: CombinatorialClass
        """
        raise NotImplementedError

    def sample_dummy(self, x, y):
        """Samples a dummy object that just records l-size and u-size

        :param x:
        :param y:
        """
        raise NotImplementedError

    def get_eval(self, x, y):
        """Gets the evaluation of the generating function of the class being sampled.

        Possibly queries the oracle directly or indirectly.

        :param x: symbolic x argument
        :param y: symbolic y argument
        :rtype: float
        """
        raise NotImplementedError

    def precompute_eval(self, x, y):
        """Precomputes the evaluation of the generating function and stores it.

        :param x: symbolic x argument
        :param y: symbolic y argument
        """
        self.precomputed_eval = self.get_eval(x, y)

    # todo maybe find a better name for this
    def oracle_query_string(self, x, y):
        """String used as key in oracle.

        This is like a 'symbolic evaluation' of the generating function of the class being sampled from this sampler.

        :param x: symbolic x argument
        :param y: symbolic y argument
        :rtype: str
        """
        raise NotImplementedError

    def get_children(self):
        """Gets the samplers this sampler depends on (if any).

        :rtype: list
        """
        raise NotImplementedError

    def accept(self, visitor):
        """Calls visitor.visit(self) and lets the children accept the visitor as well.

        """
        visitor.visit(self)
        for child in self.get_children():
            child.accept(visitor)

    def __add__(self, other):
        """Sum construction of samplers.

        Comes in very handy when writing the grammars.

        :param other: The right hand side argument.
        :return: The sum-sampler resulting from this sampler and the given sampler.
        :rtype BoltzmannSampler
        """
        return SumSampler(self, other)

    def __mul__(self, other):
        """Product construction of samplers.

        Comes in very handy when writing the grammars.

        :param other: The right hand side argument.
        :return: The product-sampler resulting from this sampler and the given sampler.
        :rtype BoltzmannSampler
        """
        return ProdSampler(self, other)


### Atom Samplers ###

class AtomSampler(BoltzmannSampler):
    """Abstract base class for atom samplers.

    """

    def sampled_class(self):
        raise NotImplementedError

    def sample(self, x, y):
        raise NotImplementedError

    def sample_dummy(self, x, y):
        raise NotImplementedError

    def get_eval(self, x, y):
        # see 3.2
        return self.oracle.get(self.oracle_query_string(x, y))

    def oracle_query_string(self, x, y):
        raise NotImplementedError

    def get_children(self):
        # an atom does not have any children
        return []


class ZeroAtomSampler(AtomSampler):
    """Sampler for the zero atom.

    """

    def sampled_class(self):
        return '1'

    def sample(self, x, y):
        return ZeroAtomClass()

    def sample_dummy(self, x, y):
        return DummyClass()

    def get_eval(self, x, y):
        # see 3.2, instead of querying '1' to the oracle we just return it.
        return 1

    def oracle_query_string(self, x, y):
        # '1' is actually never an oracle query because it's trivial but anyway
        return '1'


class LAtomSampler(AtomSampler):
    """Sampler for the l-atom (labeled atom).

    """

    def sampled_class(self):
        return 'L'

    def sample(self, x, y):
        return LAtomClass()

    def sample_dummy(self, x, y):
        return DummyClass(l_size=1)

    def oracle_query_string(self, x, y):
        # generating function of the l-atom is just x
        return x


class UAtomSampler(AtomSampler):
    """Sampler for the u-atom (unlabeled atom).

    """

    def sampled_class(self):
        return 'U'

    def sample(self, x, y):
        return UAtomClass()

    def sample_dummy(self, x, y):
        return DummyClass(u_size=1)

    def oracle_query_string(self, x, y):
        # generating function of the u-atom is just y
        return y


### Binary samplers - depend on two other samplers ###

class BinarySampler(BoltzmannSampler):
    """Abstract base class for a sampler that depends on exactly 2 other samplers.

    """

    def __init__(self, lhs, rhs):
        """

        :param lhs: The first sampler.
        :param rhs: The second sampler.
        """
        self.lhs = lhs
        self.rhs = rhs

    def sampled_class(self):
        raise NotImplementedError

    def sample(self, x, y):
        raise NotImplementedError

    def sample_dummy(self, x, y):
        raise NotImplementedError

    def get_eval(self, x, y):
        raise NotImplementedError

    def oracle_query_string(self, x, y):
        raise NotImplementedError

    def get_children(self):
        return [self.lhs, self.rhs]


class SumSampler(BinarySampler):
    """Samples from the disjoint union of the two underlying classes.

    """

    def __init__(self, lhs, rhs):
        super(SumSampler, self).__init__(lhs, rhs)

    def sampled_class(self):
        return '(' + self.lhs.sampled_class() + '+' + self.rhs.sampled_class() + ')'

    def sample(self, x, y):
        # todo this can be made more efficient (self.get_eval also evaluates self.lhs.get_eval)
        if bern(self.lhs.get_eval(x, y) / self.get_eval(x, y)):
            return self.lhs.sample(x, y)
        else:
            return self.rhs.sample(x, y)

    def sample_dummy(self, x, y):
        if bern(self.lhs.get_eval(x, y) / self.get_eval(x, y)):
            return self.lhs.sample_dummy(x, y)
        else:
            return self.rhs.sample_dummy(x, y)

    def get_eval(self, x, y):
        # see 3.2: for sum class (= disjoint union) the generating function is the sum of the 2 generating functions
        return self.lhs.get_eval(x, y) + self.rhs.get_eval(x, y)

    def oracle_query_string(self, x, y):
        return '(' + self.lhs.oracle_query_string(x, y) + '+' + self.rhs.oracle_query_string(x, y) + ')'


class ProdSampler(BinarySampler):
    """Samples from the cartesian product of the two underlying classes.

    """

    def __init__(self, lhs, rhs):
        super(ProdSampler, self).__init__(lhs, rhs)

    def sampled_class(self):
        return '(' + self.lhs.sampled_class() + '*' + self.rhs.sampled_class() + ')'

    def sample(self, x, y):
        return ProdClass(self.lhs.sample(x, y), self.rhs.sample(x, y))

    def sample_dummy(self, x, y):
        dummy_lhs = self.lhs.sample_dummy(x, y)
        dummy_rhs = self.rhs.sample_dummy(x, y)
        l_size = dummy_lhs.get_l_size() + dummy_rhs.get_l_size()
        u_size = dummy_lhs.get_u_size() + dummy_rhs.get_u_size()
        return DummyClass(l_size, u_size)

    def get_eval(self, x, y):
        # see 3.2: for product class (= cartesian prod.) the generating function is the product of the 2 generating
        # functions
        return self.lhs.get_eval(x, y) * self.rhs.get_eval(x, y)

    def oracle_query_string(self, x, y):
        return self.lhs.oracle_query_string(x, y) + '*' + self.rhs.oracle_query_string(x, y)


class LSubsSampler(BinarySampler):
    """Samples from the class resulting from substituting the l-atoms of the first class with objects of the second
    class.

    """

    def __init__(self, lhs, rhs):
        super(LSubsSampler, self).__init__(lhs, rhs)

    def sampled_class(self):
        return '(' + self.lhs.sampled_class() + ' lsubs ' + self.rhs.sampled_class() + ')'

    def sample(self, x, y):
        gamma = self.lhs.sample(self.rhs.oracle_query_string(x, y), y)
        # todo this is wrong, we must replace using different sample calls
        gamma.replace_l_atoms(self.rhs.sample, x, y)
        return gamma

    def sample_dummy(self, x, y):
        gamma = self.lhs.sample_dummy(self.rhs.oracle_query_string(x, y), y)
        l_size  = 0
        u_size = gamma.get_u_size()
        for _ in range(gamma.get_l_size()):
            dummy = self.rhs.sample_dummy(x, y)
            l_size += dummy.get_l_size()
            u_size += dummy.get_u_size()
        return DummyClass(l_size, u_size)

    def get_eval(self, x, y):
        # return self.oracle.get(self.oracle_query_string(x, y))
        return self.lhs.get_eval(self.rhs.oracle_query_string(x, y), y)

    def oracle_query_string(self, x, y):

        # see 3.2: A(B(x,y),y) where A = lhs and B = rhs
        return self.lhs.oracle_query_string(self.rhs.oracle_query_string(x, y), y)


class USubsSampler(BinarySampler):
    """Samples from the class resulting from substituting the u-atoms of the first class with objects of the second
    class.

    """

    def __init__(self, lhs, rhs):
        super(USubsSampler, self).__init__(lhs, rhs)

    def sampled_class(self):
        return '(' + self.lhs.sampled_class() + ' usubs ' + self.rhs.sampled_class() + ')'

    def sample(self, x, y):
        gamma = self.lhs.sample(x, self.rhs.oracle_query_string(x, y))
        gamma.replace_u_atoms(self.rhs.sample, x, y)
        return gamma

    def sample_dummy(self, x, y):
        gamma = self.lhs.sample_dummy(x, self.rhs.oracle_query_string(x, y))
        l_size  = gamma.get_l_size()
        u_size = 0
        for _ in range(gamma.get_u_size()):
            dummy = self.rhs.sample_dummy(x, y)
            l_size += dummy.get_l_size()
            u_size += dummy.get_u_size()
        return DummyClass(l_size, u_size)

    def get_eval(self, x, y):
        # todo not 100% sure about this yet
        return self.lhs.get_eval(x, self.rhs.oracle_query_string(x, y))
        #return self.oracle.get(self.oracle_query_string(x, y))

    def oracle_query_string(self, x, y):
        # see 3.2: A(x,B(x,y)) where A = lhs and B = rhs
        return self.lhs.oracle_query_string(x, self.rhs.oracle_query_string(x, y))


### Unary samplers - depend on one other sampler ###

class UnarySampler(BoltzmannSampler):
    """Abstract base class for samplers that depend exactly on one other sampler.

    """

    def __init__(self, sampler):
        """

        :param sampler: A sampler of the underlying class.
        """
        self.sampler = sampler

    def sampled_class(self):
        raise NotImplementedError

    def sample(self, x, y):
        raise NotImplementedError

    def sample_dummy(self, x, y):
        raise NotImplementedError

    def get_eval(self, x, y):
        raise NotImplementedError

    def oracle_query_string(self, x, y):
        raise NotImplementedError

    def get_children(self):
        return [self.sampler]


class SetSampler(UnarySampler):
    """Samples a set of elements from the underlying class.

    """

    def __init__(self, d, sampler):
        """

        :param d: The minimum size of the set.
        :param sampler: A sampler of the underlying class.
        """
        super(SetSampler, self).__init__(sampler)
        self.d = d

    def sampled_class(self):
        return 'Set_' + str(self.d) + '(' + self.sampler.sampled_class() + ')'

    def sample(self, x, y):
        k = pois(self.d, self.sampler.get_eval(x, y))
        return SetClass([self.sampler.sample(x, y) for _ in range(k)])

    def sample_dummy(self, x, y):
        k = pois(self.d, self.sampler.get_eval(x, y))
        l_size = 0
        u_size = 0
        for _ in range(k):
            dummy = self.sampler.sample_dummy(x, y)
            l_size += dummy.get_l_size()
            u_size += dummy.get_u_size()
        return DummyClass(l_size, u_size)

    def get_eval(self, x, y):
        # see 3.2
        return exp_tail(self.d, self.sampler.get_eval(x, y))

    def oracle_query_string(self, x, y):
        return 'exp_' + str(self.d) + '(' + self.sampler.oracle_query_string(x, y) + ')'


class TransformationSampler(UnarySampler):
    """Generic sampler that transforms the the objects sampled from the base class to a new class.
    For bijections use the base class BijectionSampler.

    """

    def __init__(self, sampler, f, eval_transform=None, target_class_label=None):
        """

        :param sampler: Sampler of the underlying class.
        :param f: Function from the underlying class to the target class.
        :param eval_transform: Optional transformation of the evaluation of the generating function.
        :param target_class_label: Optional label of the sampled class.
        """
        super(TransformationSampler, self).__init__(sampler)
        self.f = f
        self.eval_transform = eval_transform
        if target_class_label is None:
            # set a default label for the target class based on the nume of the transformation function
            self.target_class_label = f.__name__ + '(' + sampler.sampled_class() + ')'
        else:
            self.target_class_label = target_class_label

    def sampled_class(self):
        return self.target_class_label

    def sample(self, x, y):
        # sample from the underlying class and apply the bijection
        return self.f(self.sampler.sample(x, y))

    def sample_dummy(self, x, y):
        return self.sampler.sample_dummy(x, y)

    def get_eval(self, x, y):
        # if a transformation is given, apply it here
        if self.eval_transform is not None:
            return self.eval_transform(self.sampler.get_eval(x, y), x, y)
        # otherwise query the oracle because we cannot infer the evaluation in the case of a general transformation
        return self.oracle.get(self.oracle_query_string(x, y))

    def oracle_query_string(self, x, y):
        return self.sampled_class() + '(' + x + ',' + y + ')'

    def set_target_class_label(self, label):
        """

        :param label: Label of the target class.
        """
        self.target_class_label = label


class BijectionSampler(TransformationSampler):
    """Samples a class that is isomorphic to the underlying class.

    """

    def __init__(self, sampler, f, target_class_label=None):
        """

        :param sampler: Sampler of the underlying class.
        :param f: Bijection from the underlying class to the target class.
        :param target_class_label: Optional label of the sampled class.
        """
        super(BijectionSampler, self).__init__(sampler, f, None, target_class_label)

    def get_eval(self, x, y):
        # since the target class is isomorphic to the underlying class, the evaluation is also the same
        return self.sampler.get_eval(x, y)

    def oracle_query_string(self, x, y):
        # here we can also take the underlying class
        return self.sampler.oracle_query_string(x, y)


class RejectionSampler(TransformationSampler):
    """Generic rejection sampler, special case of transformation.

    """

    def __init__(self, sampler, is_acceptable, eval_transform=None, target_class_label=None):
        """

        :param sampler: Sampler of the underlying class.
        :param is_acceptable: Criterion for accepting an object from the underlying class.
        :param eval_transform: Optional transformation of the evaluation function.
        :param target_class_label: Optional label of the sampled class.
        """
        super(RejectionSampler, self).__init__(sampler, is_acceptable, eval_transform, target_class_label)
        self.rejections_count = 0

    def sample(self, x, y):
        self.rejections_count = 0
        gamma = self.sampler.sample(x, y)
        while not self.f(gamma):
            self.rejections_count += 1
            gamma = self.sampler.sample(x, y)
        return gamma

    def sample_dummy(self, x, y):
        self.rejections_count = 0
        gamma = self.sampler.sample_dummy(x, y)
        while not self.f(gamma):
            self.rejections_count += 1
            gamma = self.sampler.sample_dummy(x, y)
        return gamma

    def get_rejections_count(self):
        return self.rejections_count


class UDerFromLDerSampler(TransformationSampler):
    """Samples the u-derived (dy) class of the given l-derived (dx) class sampler.

    """

    def __init__(self, sampler, alpha_u_l):
        """

        :param sampler: A sampler of the l-derived class. Must sample an LDerivedClass.
        :param alpha_u_l: Limit value of u-size/l-size of the underlying class.
        """
        super(UDerFromLDerSampler, self).__init__(sampler, None, None,
                                           sampler.sampled_class()[0:len(sampler.sampled_class()) - 2] + 'dy')
        self.alpha_u_l = alpha_u_l

    def sample(self, x, y):
        # see lemma 6
        while True:
            gamma = self.sampler.sample(x, y)
            p = (1 / self.alpha_u_l) * (gamma.get_u_size() / (gamma.get_l_size() + 1))
            if bern(p):
                gamma = gamma.get_base_class_object()
                rand_u_atom = gamma.random_u_atom()
                return UDerivedClass(gamma, rand_u_atom)

    def sample_dummy(self, x, y):
        while True:
            gamma = self.sampler.sample_dummy(x, y)
            p = (1 / self.alpha_u_l) * (gamma.get_u_size() / (gamma.get_l_size() + 1))
            if bern(p):
                gamma.l_size += 1
                gamma.u_size -= 1
                assert gamma.get_u_size() >= 0
                return gamma


class LDerFromUDerSampler(TransformationSampler):
    """Samples the l-derived (dx) class of the given u-derived (dy) class.

       """

    def __init__(self, sampler, alpha_l_u):
        """

        :param sampler: A sampler of the u-derived class. Must sample a UDerivedClass.
        :param alpha_l_u: Limit value of l-size/u-size of the underlying class.
        """
        super(LDerFromUDerSampler, self).__init__(sampler, None, None,
                                           sampler.sampled_class()[0:len(sampler.sampled_class()) - 2] + 'dx')
        self.alpha_l_u = alpha_l_u

    def sample(self, x, y):
        while True:
            gamma = self.sampler.sample(x, y)
            p = (1 / self.alpha_l_u) * (gamma.get_l_size() / (gamma.get_u_size() + 1))
            if bern(p):
                gamma = gamma.get_base_class_object()
                rand_l_atom = gamma.random_l_atom()
                return LDerivedClass(gamma, rand_l_atom)

    def sample_dummy(self, x, y):
        while True:
            gamma = self.sampler.sample_dummy(x, y)
            p = (1 / self.alpha_l_u) * (gamma.get_l_size() / (gamma.get_u_size() + 1))
            if bern(p):
                gamma.l_size -= 1
                gamma.u_size += 1
                assert gamma.get_l_size() >= 0
                return gamma
