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

from __future__ import division

from framework.class_builder import DefaultBuilder
from framework.generic_classes import *
from framework.utils import *


def return_precomp(func):
    def wrapper(self, *args, **kwargs):
        if self._precomputed_eval is not None:
            return self._precomputed_eval
        return func(self, *args, **kwargs)

    return wrapper


class BoltzmannSamplerBase(object):
    """
    Abstract base class for Boltzmann samplers.

    Attributes
    ----------
    oracle: EvaluationOracle
        The oracle to be used by all instantiations of this class and its subclasses.
    debug_mode: bool
        Will perform additional (possibly time consuming) checks when set to True.

    References
    ----------
    .. [1] E. Fusy:
        Uniform Random Sampling of Planar Graphs in Linear Time'
        ??
        ??
    """

    oracle = None
    debug_mode = False

    __slots__ = '_builder', '_precomputed_eval'

    def __init__(self):
        # Samplers are always initialized with the default builder.
        self._builder = DefaultBuilder()
        self._precomputed_eval = None

    @property
    def sampled_class(self):
        """Returns a string representation of the sampled class.

        Returns
        -------
        str
            A string representation of the sampled class.
        """
        raise NotImplementedError

    def sample(self, x, y):
        """Invokes this sampler with the given x and y parameters.

        Calls the child-samplers recursively.

        Parameters
        ----------
        x: str
            symbolic x argument
        y: str
            symbolic y argument

        Returns
        -------
        CombinatorialClass
            The result of the sampling operation.
        """
        raise NotImplementedError

    def eval(self, x, y):
        """Gets the evaluation of the generating function of the class being sampled.

        Possibly queries the oracle directly or indirectly.

        Parameters
        ----------
        x: str
            symbolic x argument
        y: str
            symbolic y argument

        Returns
        -------
        evaluation: float
            The value of the generating function of the sampled class at the given point.
        """
        raise NotImplementedError

    def precompute_eval(self, x, y):
        """Precomputes the evaluation of the generating function and stores it.

        Parameters
        ----------
        x: str
            symbolic x argument
        y: str
            symbolic y argument
        """
        self._precomputed_eval = self.eval(x, y)

    def oracle_query_string(self, x, y):
        """String used as key in oracle.

        This is like a 'symbolic evaluation' of the generating function of the class being sampled from this _sampler.

        Parameters
        ----------
        x: str
            symbolic x argument
        y: str
            symbolic y argument

        Returns
        -------
        query_string: str
            String that may be used to query the oracle for the generating function of the sampled class.
        """
        raise NotImplementedError

    @property
    def builder(self):
        """Returns the builder registered with this sampler or None.

        Returns
        -------
        builder: CombinatorialClassBuilder
            Builder registered with this sampler or None.
        """
        return self._builder

    @builder.setter
    def builder(self, builder):
        """Registers a builder for the output class.

        Output will be in generic format if not set.

        Parameters
        ----------
        builder: CombinatorialClassBuilder
        """
        self._builder = builder

    def get_children(self):
        """Gets the samplers this sampler depends on (if applicable).

        Applies to all samplers except atom samplers.

        Returns
        -------
        iterator
            An iterator over all samplers this _sampler depends on.
        """
        raise NotImplementedError

    def accept(self, visitor):
        """Accepts a visitor.

        Parameters
        ----------
        visitor: object
        """
        visitor.visit(self)
        for child in self.get_children():
            child.accept(visitor)

    def __add__(self, other):
        """Sum construction of samplers.

        Parameters
        ----------
        other: BoltzmannSamplerBase
            The right hand side argument.

        Returns
        -------
        BoltzmannSamplerBase
            The sum-_sampler resulting from this _sampler and the given _sampler.
        """
        return SumSampler(self, other)

    def __mul__(self, other):
        """Product construction of samplers.

        Parameters
        ----------
        other: BoltzmannSamplerBase
            The right hand side argument.

        Returns
        -------
        BoltzmannSamplerBase
            The product-_sampler resulting from this _sampler and the given _sampler.
        """
        return ProdSampler(self, other)

    # todo Support all integers.
    def __rmul__(self, other):
        """Adds (sum construction) a _sampler to itself several times.

        Parameters
        ----------
        other: int
            The left hand side argument, must be either 2 or 3.

        Returns
        -------
        BoltzmannSamplerBase
            The _sampler resulting from this operation.

        Notes
        -----
        This only affects the generating function but not the outcome.
        """
        if other == 2:
            return self + self
        if other == 3:
            return self + self + self
        else:
            raise ValueError("Multiplication with a constant only implemented for integers 2 and 3")

    # todo Support all integers.
    def __pow__(self, power, modulo=None):
        """Multiplies a _sampler with itself.

        Parameters
        ----------
        power: int
            The right hand side argument, must be either 2 or 3.

        Returns
        -------
        BoltzmannSamplerBase
            The _sampler resulting from this operation.

        """
        if power == 2:
            return self * self
        if power == 3:
            return self * self * self
        else:
            raise ValueError("Power only implemented for integers 2 and 3")


class AtomSampler(BoltzmannSamplerBase):
    """Abstract base class for atom samplers."""

    def __init__(self):
        super(AtomSampler, self).__init__()

    @property
    def sampled_class(self):
        raise NotImplementedError

    def sample(self, x, y):
        raise NotImplementedError

    @return_precomp
    def eval(self, x, y):
        return self.oracle[self.oracle_query_string(x, y)]

    def oracle_query_string(self, x, y):
        raise NotImplementedError

    def get_children(self):
        # An atom does not have any children.
        return []


class ZeroAtomSampler(AtomSampler):
    """Sampler for the zero atom."""

    def __init__(self):
        super(ZeroAtomSampler, self).__init__()

    @property
    def sampled_class(self):
        return '1'

    def sample(self, x, y):
        if Settings.debug_mode:
            # todo
            return self._builder.zero_atom()
        else:
            return self._builder.zero_atom()

    def eval(self, x, y):
        # See 3.2, instead of querying '1' to the oracle we just return it.
        return 1

    def oracle_query_string(self, x, y):
        return '1'


class LAtomSampler(AtomSampler):
    """Sampler for the l-atom (labeled atom)."""

    def __init__(self):
        super(LAtomSampler, self).__init__()

    @property
    def sampled_class(self):
        return 'L'

    def sample(self, x, y):
        # todo
        return self._builder.l_atom()

    def oracle_query_string(self, x, y):
        # Generating function of the l-atom is just x.
        return x


class UAtomSampler(AtomSampler):
    """Sampler for the u-atom (unlabeled atom)."""

    def __init__(self):
        super(UAtomSampler, self).__init__()

    @property
    def sampled_class(self):
        return 'U'

    def sample(self, x, y):
        # todo
        return self._builder.u_atom()

    def oracle_query_string(self, x, y):
        # Generating function of the u-atom is just y.
        return y


class BinarySampler(BoltzmannSamplerBase):
    """
    Abstract base class for a _sampler that depends on exactly 2 other samplers.

    Parameters
    ----------
    lhs: BoltzmannSamplerBase
        The left hand side argument.
    rhs: BoltzmannSamplerBase
        The right hand side argument.
    op_symbol: str
        The string representation of the implemented operator.
    """

    __slots__ = 'lhs', 'rhs', '_op_symbol'

    def __init__(self, lhs, rhs, op_symbol):
        super(BinarySampler, self).__init__()
        self.lhs = lhs
        # While this is okay for the recursive sampling it causes problems in the iterative version.
        if lhs is rhs:
            from copy import copy
            rhs = copy(lhs)
        self.rhs = rhs
        self._op_symbol = op_symbol

    # TODO remove this because of performnance?
    # @property
    # def lhs(self):
    #     """Returns the left argument of this sampler."""
    #     return self._lhs
    #
    # @property
    # def rhs(self):
    #     """Returns the right argument of this sampler."""
    #     return self._rhs

    @property
    def sampled_class(self):
        return "({}{}{})".format(self.lhs.sampled_class, self._op_symbol, self.rhs.sampled_class)

    def sample(self, x, y):
        raise NotImplementedError

    def eval(self, x, y):
        raise NotImplementedError

    def oracle_query_string(self, x, y):
        return "({}{}{})".format(
            self.lhs.oracle_query_string(x, y),
            self._op_symbol,
            self.rhs.oracle_query_string(x, y)
        )

    def get_children(self):
        return [self.lhs, self.rhs]


class SumSampler(BinarySampler):
    """Samples from the disjoint union of the two underlying classes."""

    def __init__(self, lhs, rhs):
        super(SumSampler, self).__init__(lhs, rhs, '+')

    def sample(self, x, y):
        if bern(self.lhs.eval(x, y) / self.eval(x, y)):
            return self.lhs.sample(x, y)
        else:
            return self.rhs.sample(x, y)

    @return_precomp
    def eval(self, x, y):
        # For the sum class (disjoint union) the generating function is the sum of the 2 generating functions.
        return self.lhs.eval(x, y) + self.rhs.eval(x, y)


class ProdSampler(BinarySampler):
    """Samples from the cartesian product of the two underlying classes."""

    def __init__(self, lhs, rhs):
        super(ProdSampler, self).__init__(lhs, rhs, '*')

    def sample(self, x, y):
        # todo
        return self._builder.product(self.lhs.sample(x, y), self.rhs.sample(x, y))

    @return_precomp
    def eval(self, x, y):
        # For the product class (cartesian prod.) the generating function is the product of the 2 generating functions.
        return self.lhs.eval(x, y) * self.rhs.eval(x, y)

    def oracle_query_string(self, x, y):
        return "{}{}{}".format(
            self.lhs.oracle_query_string(x, y),
            self._op_symbol,
            self.rhs.oracle_query_string(x, y)
        )


class LSubsSampler(BinarySampler):
    """Samples from the class resulting from substituting the l-atoms of lhs with objects of rhs."""

    def __init__(self, lhs, rhs):
        super(LSubsSampler, self).__init__(lhs, rhs, ' lsubs ')

    def sample(self, x, y):
        gamma = self.lhs.sample(self.rhs.oracle_query_string(x, y), y)
        gamma = gamma.replace_l_atoms(self.rhs, x, y)
        return gamma

    @return_precomp
    def eval(self, x, y):
        return self.lhs.eval(self.rhs.oracle_query_string(x, y), y)

    def oracle_query_string(self, x, y):
        #  A(B(x,y),y) where A = lhs and B = rhs (see 3.2).
        return self.lhs.oracle_query_string(self.rhs.oracle_query_string(x, y), y)


class USubsSampler(BinarySampler):
    """Samples from the class resulting from substituting the u-atoms of lhs with objects of rhs."""

    def __init__(self, lhs, rhs):
        super(USubsSampler, self).__init__(lhs, rhs, ' usubs ')

    def sample(self, x, y):
        gamma = self.lhs.sample(x, self.rhs.oracle_query_string(x, y))
        gamma = gamma.replace_u_atoms(self.rhs, x, y)
        return gamma

    @return_precomp
    def eval(self, x, y):
        return self.lhs.eval(x, self.rhs.oracle_query_string(x, y))

    def oracle_query_string(self, x, y):
        # A(x,B(x,y)) where A = lhs and B = rhs (see 3.2).
        return self.lhs.oracle_query_string(x, self.rhs.oracle_query_string(x, y))


class UnarySampler(BoltzmannSamplerBase):
    """
    Abstract base class for samplers that depend exactly on one other _sampler.

    Parameters
    ----------
    sampler: BoltzmannSamplerBase
        The _sampler this _sampler depends on.
    """

    __slots__ = '_sampler'

    def __init__(self, sampler):
        super(UnarySampler, self).__init__()
        self._sampler = sampler

    @property
    def sampled_class(self):
        raise NotImplementedError

    def sample(self, x, y):
        raise NotImplementedError

    def eval(self, x, y):
        raise NotImplementedError

    def oracle_query_string(self, x, y):
        raise NotImplementedError

    def get_children(self):
        return [self._sampler]


class SetSampler(UnarySampler):
    """
    Samples a set of elements from the underlying class.

    A set has no order and no duplicate elements. The underlying class may not contain objects with l-size 0. Otherwise
    this sampler will not output correct results.

    Parameters
    ----------
    d: int
        The minimum size of the set.
    sampler: BoltzmannSamplerBase
        The sampler that produces the elements in the set.

    Notes
    -----
    It is not checked/ensured automatically that object from the underlying class do not have l-size 0.
    """

    __slots__ = '_d'

    def __init__(self, d, sampler):
        super(SetSampler, self).__init__(sampler)
        self._d = d

    @property
    def sampled_class(self):
        return "Set_{}({})".format(self._d, self._sampler.sampled_class)

    def draw_k(self, x, y):
        return pois(self._d, self._sampler.eval(x, y))

    def sample(self, x, y):
        # todo
        k = self.draw_k(x, y)
        return self._builder.set([self._sampler.sample(x, y) for _ in range(k)])

    @return_precomp
    def eval(self, x, y):
        # The generating function of a set class is a tail of the exponential row evaluated at the generating function
        # of the underlying class (see 3.2).
        return exp_tail(self._d, self._sampler.eval(x, y))

    def oracle_query_string(self, x, y):
        return "exp_{}({})".format(self._d, self._sampler.oracle_query_string(x, y))


class TransformationSampler(UnarySampler):
    """
    Generic sampler that transforms the the objects sampled from the base class to a new class.

    For bijections use the base class BijectionSampler.

    Parameters
    ----------
    sampler: BoltzmannSamplerBase
    f: transformation function, optional (default=id)
    eval_transform: generating function transformation, optional (default=id)
    target_class_label: str, optional (default=None)
    """

    def __init__(self, sampler, f=None, eval_transform=None, target_class_label=None):
        super(TransformationSampler, self).__init__(sampler)
        self._f = f
        self._eval_transform = eval_transform
        if target_class_label is None:
            # Set a default label for the target class based on the name of the transformation function.
            if f is not None:
                self._target_class_label = "{}({})".format(f.__name__, sampler.sampled_class)
        else:
            self._target_class_label = target_class_label

    @property
    def transformation(self):
        """Returns the transformation function."""
        return self._f

    @transformation.setter
    def transformation(self, f):
        """Sets the transformation function."""
        self._f = f

    @property
    def sampled_class(self):
        return self._target_class_label

    @sampled_class.setter
    def sampled_class(self, label):
        self._target_class_label = label

    def sample(self, x, y):
        if self._f is not None:
            # Sample from the underlying class and apply the transformation.
            return self._f(self._sampler.sample(x, y))
        # Otherwise sample without transformation.
        return self._sampler.sample(x, y)

    @return_precomp
    def eval(self, x, y):
        # If a transformation of the generating function is given, apply it here.
        if self._eval_transform is not None:
            return self._eval_transform(self._sampler.eval(x, y), x, y)
        # Otherwise query the oracle because we cannot infer the evaluation in the case of a general transformation.
        return self.oracle.get(self.oracle_query_string(x, y))

    def oracle_query_string(self, x, y):
        try:
            return "{}({},{})".format(self.sampled_class, x, y)
        except AttributeError:
            # self.sampled_class might be None.
            raise BoltzmannFrameworkError("No target class label was given or could be inferred")


class BijectionSampler(TransformationSampler):
    """
    Samples a class that is isomorphic to the underlying class.

    Parameters
    ----------
    sampler: BoltzmannSamplerBase
    f: transformation function
    target_class_label: str, optional (default=None)
    """

    def __init__(self, sampler, f, target_class_label=None):
        super(BijectionSampler, self).__init__(sampler, f, None, target_class_label)

    def sample(self, x, y):
        # Sample from the underlying class and apply the bijection.
        # In debug_mode check the sizes before and after applying the bijection.
        if Settings.debug_mode:
            # l_size/u_size may be not implemented on some classes, in this case the check is ignored.
            gamma = self._sampler.sample(x, y)
            try:
                l_size_before = gamma.l_size
                u_size_before = gamma.u_size
                gamma = self._f(gamma)
                l_size_after = gamma.l_size
                u_size_after = gamma.u_size
                assert l_size_before == l_size_after and u_size_before == u_size_after
                return gamma
            except NotImplementedError:
                return self._f(gamma)
        else:
            return self._f(self._sampler.sample(x, y))

    @return_precomp
    def eval(self, x, y):
        # Since the target class is isomorphic to the underlying class, the evaluation is also the same.
        return self._sampler.eval(x, y)

    def oracle_query_string(self, x, y):
        return self._sampler.oracle_query_string(x, y)


class RejectionSampler(TransformationSampler):
    """
    Generic rejection sampler, special case of transformation.

    Parameters
    ----------
    sampler: BoltzmannSamplerBase
        Sampler of the underlying class.
    is_acceptable: function
        Criterion for accepting an object from the underlying class.
    eval_transform: function, optional (default=None)
        Optional transformation of the evaluation function.
    target_class_label: str, optional (default=None)
        Optional label of the sampled class.
    """

    def __init__(self, sampler, is_acceptable, eval_transform=None, target_class_label=None):
        super(RejectionSampler, self).__init__(sampler, is_acceptable, eval_transform, target_class_label)
        self._rejections_count = 0

    @property
    def rejections_count(self):
        """Counts the number of unsuccessful sampling operations.

        Returns
        -------
        rejections_count: int
            Number of rejections in the last sampling operation.
        """
        return self._rejections_count

    def sample(self, x, y):
        self._rejections_count = 0
        gamma = self._sampler.sample(x, y)
        is_acceptable = self._f
        while not is_acceptable(gamma):
            self._rejections_count += 1
            gamma = self._sampler.sample(x, y)
        return gamma


class UDerFromLDerSampler(TransformationSampler):
    """
    Samples the u-derived (dy) class of the given l-derived (dx) class sampler.

    Parameters
    ----------
    sampler: BoltzmannSamplerBase
        A sampler of the l-derived class. Must sample an LDerivedClass.
    alpha_u_l: float
        Limit value of u-size/l-size of the underlying class.
    """

    def __init__(self, sampler, alpha_u_l):
        # Try to infer a label that makes sense.
        if sampler.sampled_class[-2:] is 'dx':
            label = "{}dy".format(sampler.sampled_class[:-2])
        else:
            label = "{}_dy_from_dx".format(sampler.sampled_class)
        super(UDerFromLDerSampler, self).__init__(sampler, None, None, label)
        self._alpha_u_l = alpha_u_l

    def sample(self, x, y):
        # See lemma 6 for this rejection technique.
        while True:
            gamma = self._sampler.sample(x, y)
            p = (1 / self._alpha_u_l) * (gamma.u_size / (gamma.l_size + 1))
            if bern(p):
                return UDerivedClass(gamma.base_class_object)


class LDerFromUDerSampler(TransformationSampler):
    """
    Samples the l-derived (dx) class of the given u-derived (dy) class.

    Parameters
    ----------
    sampler: BoltzmannSamplerBase
        A sampler of the u-derived class. Must sample a UDerivedClass.
    alpha_l_u: float
        Limit value of l-size/u-size of the underlying class.

    """

    def __init__(self, sampler, alpha_l_u):
        # Try to infer a label that makes sense.
        if sampler.sampled_class[-2:] is 'dy':
            label = "{}dx".format(sampler.sampled_class[:-2])
        else:
            label = "{}_dx_from_dy".format(sampler.sampled_class)
        super(LDerFromUDerSampler, self).__init__(sampler, None, None, label)
        self._alpha_l_u = alpha_l_u

    def sample(self, x, y):
        while True:
            gamma = self._sampler.sample(x, y)
            p = (1 / self._alpha_l_u) * (gamma.l_size / (gamma.u_size + 1))
            if bern(p):
                return LDerivedClass(gamma.base_class_object)
