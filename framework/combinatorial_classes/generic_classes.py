import random as rn
from ..utils import *


class BoltzmannFrameworkError(Exception):
    """Base class for exceptions in the framework."""
    pass


# CombinatorialClass instances are objects from a mixed combinatorial class (with l- and u-atoms)
class CombinatorialClass:
    def get_u_size(self):
        raise NotImplementedError

    def get_l_size(self):
        raise NotImplementedError

    def u_atoms(self):
        raise NotImplementedError

    def l_atoms(self):
        raise NotImplementedError

    def random_u_atom(self):
        rand_index = rn.randrange(self.get_u_size())
        return nth(self.u_atoms(), rand_index)

    def random_l_atom(self):
        rand_index = rn.randrange(self.get_l_size())
        return nth(self.l_atoms(), rand_index)

    def replace_u_atoms(self, sampler, x, y):
        raise NotImplementedError

    def replace_l_atoms(self, sampler, x, y):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class DummyClass(CombinatorialClass):

    def __init__(self, l_size=0, u_size=0):
        self.l_size = l_size
        self.u_size = u_size

    def get_u_size(self):
        return self.u_size

    def get_l_size(self):
        return self.l_size

    def u_atoms(self):
        raise NotImplementedError

    def l_atoms(self):
        raise NotImplementedError

    def replace_u_atoms(self, sampler, x, y):
        raise NotImplementedError

    def replace_l_atoms(self, sampler, x, y):
        raise NotImplementedError

    def __str__(self):
        return '(l: ' + str(self.l_size) + ", u: " + str(self.u_size) + ')'


class ZeroAtomClass(CombinatorialClass):
    def get_u_size(self):
        return 0

    def get_l_size(self):
        return 0

    # noinspection PyUnreachableCode
    def u_atoms(self):
        # this syntax implements an empty generator
        return
        yield

    # noinspection PyUnreachableCode
    def l_atoms(self):
        # this syntax implements an empty generator
        return
        yield

    def __str__(self):
        return '1'


class LAtomClass(CombinatorialClass):
    def get_u_size(self):
        return 0

    def get_l_size(self):
        return 1

    # noinspection PyUnreachableCode
    def u_atoms(self):
        # this syntax implements an empty generator
        return
        yield

    def l_atoms(self):
        yield self

    def __str__(self):
        return 'L'


class UAtomClass(CombinatorialClass):
    def get_u_size(self):
        return 1

    def get_l_size(self):
        return 0

    def u_atoms(self):
        yield self

    # noinspection PyUnreachableCode
    def l_atoms(self):
        return
        yield

    def __str__(self):
        return 'U'


class ProdClass(CombinatorialClass):
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def get_l_size(self):
        return self.first.get_l_size() + self.second.get_l_size()

    def get_u_size(self):
        return self.first.get_u_size() + self.second.get_u_size()

    def u_atoms(self):
        yield from self.first.u_atoms()
        yield from self.second.u_atoms()

    def l_atoms(self):
        yield from self.first.l_atoms()
        yield from self.second.l_atoms()

    def replace_u_atoms(self, sampler, x, y):
        children = [self.first, self.second]
        for child in children:
            try:
                child.replace_u_atoms(sampler, x, y)
            except:
                if isinstance(child, UAtomClass):
                    # note that here we cannot simply write "child = ... "
                    children[children.index(child)] = sampler.sample(x, y)

    def replace_l_atoms(self, sampler, x, y):
        children = [self.first, self.second]
        for child in children:
            try:
                child.replace_l_atoms(sampler, x, y)
            except:
                if isinstance(child, LAtomClass):
                    # note that here we cannot simply write "child = ... "
                    children[children.index(child)] = sampler.sample(x, y)

    def __str__(self):
        return '(' + str(self.first) + ',' + str(self.second) + ')'


class SetClass(CombinatorialClass):
    def __init__(self, elems):
        self.elems = elems

    def get_l_size(self):
        return sum([elem.get_l_size() for elem in self.elems])

    def get_u_size(self):
        return sum([elem.get_u_size() for elem in self.elems])

    def u_atoms(self):
        for elem in self.elems:
            yield from elem.u_atoms()

    def l_atoms(self):
        for elem in self.elems:
            yield from elem.l_atoms()

    def replace_u_atoms(self, sampler, x, y):
        for child in self.elems:
            try:
                child.replace_u_atoms(sampler, x, y)
            except:
                if isinstance(child, UAtomClass):
                    # note that here we cannot simply write "child = ... "
                    self.elems[self.elems.index(child)] = sampler.sample(x, y)

    def replace_l_atoms(self, sampler, x, y):
        for child in self.elems:
            try:
                child.replace_l_atoms(sampler, x, y)
            except:
                if isinstance(child, LAtomClass):
                    # note that here we cannot simply write "child = ... "
                    self.elems[self.elems.index(child)] = sampler.sample(x, y)

    def __str__(self):
        result = '['
        for elem in self.elems:
            result += elem + ','
        result += ']'
        return result


class DerivedClass(CombinatorialClass):
    """Base class for l-derived and u-derived classes.

    """

    def __init__(self, base_class_object, marked_atom=None):
        """

        :param base_class_object: Object from the underlying class.
        :param marked_atom: Optional marked atom. Maybe none because it is not always needed.
        """
        self.marked_atom = marked_atom
        self.base_class_object = base_class_object

    def get_l_size(self):
        return self.base_class_object.get_l_size() - 1

    def get_u_size(self):
        return self.base_class_object.get_u_size()

    def l_atoms(self):
        yield from self.base_class_object.l_atoms()

    def u_atoms(self):
        yield from self.base_class_object.u_atoms()

    def get_marked_atom(self):
        """

        :return: The marked atom if any, otherwise exception.
        """
        return self.marked_atom

    def get_base_class_object(self):
        """

        :return: The underived object of the base class.
        """
        return self.base_class_object

    def invert_derivation_order(self):
        """Inverts the derivation order.

        Only works if the underlying class is a derived class as well.
        """
        raise NotImplementedError

    class InvertDerivationOrderError(BoltzmannFrameworkError):
        """Exception raised when invert derivation order fails.

        """

        def __init__(self, message):
            self.message = message


class LDerivedClass(DerivedClass):
    """Wrapper for an l-derived class.

    """

    def __init__(self, base_class_object, marked_l_atom=None):
        super(LDerivedClass, self).__init__(base_class_object, marked_l_atom)

    def get_l_size(self):
        return self.base_class_object.get_l_size() - 1

    def l_atoms(self):
        for l_atom in self.base_class_object.l_atoms():
            if l_atom != self.marked_atom:
                yield l_atom

    def invert_derivation_order(self):
        if not isinstance(self.base_class_object, UDerivedClass):
            raise DerivedClass.InvertDerivationOrderError("underlying class is no instance of UDerivedClass")
        gamma = self.base_class_object.get_base_class_object()
        l_derived = LDerivedClass(gamma, self.marked_atom)
        u_derived = UDerivedClass(l_derived, self.base_class_object.get_marked_atom())
        return u_derived

    def __str__(self):
        return str(self.base_class_object) + "->" + str(self.marked_atom)


class UDerivedClass(DerivedClass):
    """Wrapper for a u-derived class.

    """

    def __init__(self, base_class_object, marked_u_atom=None):
        super(UDerivedClass, self).__init__(base_class_object, marked_u_atom)

    def get_u_size(self):
        return self.base_class_object.get_u_size() - 1

    def u_atoms(self):
        for u_atom in self.base_class_object.u_atoms():
            if u_atom != self.marked_atom:
                yield u_atom

    # invert the derivation order
    # the base class must be an LDerivedClass instance
    def invert_derivation_order(self):
        if not isinstance(self.base_class_object, UDerivedClass):
            raise DerivedClass.InvertDerivationOrderError("underlying class is no instance of LDerivedClass")
        gamma = self.base_class_object.get_base_class_object()
        u_derived = UDerivedClass(gamma, self.marked_atom)
        l_derived = LDerivedClass(u_derived, self.base_class_object.get_marked_atom())
        return l_derived

    def __str__(self):
        return str(self.base_class_object) + "->" + str(self.marked_atom)
