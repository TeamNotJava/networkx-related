import random

from framework.settings_global import Settings
from framework.utils import *


class BoltzmannFrameworkError(Exception):
    """Base class for exceptions in the framework."""


class SubstitutionError(BoltzmannFrameworkError):
    """Raised when a substitution fails."""


class InvertDerivationOrderError(BoltzmannFrameworkError):
    """Raised when invert derivation order fails."""


class DerivationError(BoltzmannFrameworkError):
    """"""


class CombinatorialClass(object):
    """
    Abstract base class for objects from mixed combinatorial classes.

    CombinatorialClass instances are objects from a mixed combinatorial class (with l- and u-atoms). They do not
    represent the class itself (the naming is sort of inaccurate).
    """

    @property
    def l_size(self):
        """Number of l-atoms in this object.

        Returns
        -------
        int
            L-size (number of labelled atoms).
        """
        raise NotImplementedError

    @property
    def u_size(self):
        """Number of u-atoms in this object.

        Returns
        -------
        int
            U-size (number of unlabelled atoms).
        """
        raise NotImplementedError

    def l_atoms(self):
        """Iterator over all l-atoms."""
        raise NotImplementedError

    def u_atoms(self):
        """Iterator over all u-atoms."""
        raise NotImplementedError

    def random_l_atom(self):
        """Returns a random l-atom within this object or the object itself."""
        rand_index = random.randrange(self.l_size)
        return nth(self.l_atoms(), rand_index)

    def random_u_atom(self):
        """Returns a random l-atom within this object or the object itself."""
        rand_index = random.randrange(self.u_size)
        return nth(self.u_atoms(), rand_index)

    def replace_l_atoms(self, sampler, x, y, exceptions=None):
        """Replaces all l-atoms within this object.

        Returns
        -------

        Parameters
        ----------
        sampler: BoltzmannSamplerBase
        x: str
        y: str
        exceptions: list of CombinatorialClass
        """
        raise NotImplementedError

    def replace_u_atoms(self, sampler, x, y, exceptions=None):
        """Replaces all u-atoms."""
        raise NotImplementedError

    def assign_random_labels(self):
        """Assigns labels from [0, l-size) to all l-atoms in this object (including itself).

        Notes
        -----
        ...
        """
        labels = random.sample(range(self.l_size), self.l_size)
        for atom in self.l_atoms():
            atom.label = labels.pop()

    def __str__(self):
        """Returns a string representation of this object."""
        raise NotImplementedError


class DummyClass(CombinatorialClass):
    """An object without internal structure that only tracks sizes.

    Useful for more efficient testing of a _sampler's size distribution.

    Parameters
    ----------
    l_size: int, optional (default=0)
    u_size: int, optional (default=0)
    """

    def __init__(self, l_size=0, u_size=0):
        self._l_size = l_size
        self._u_size = u_size

    @property
    def l_size(self):
        return self._l_size

    @property
    def u_size(self):
        return self._u_size

    def l_atoms(self):
        raise BoltzmannFrameworkError("Cannot iterate over atoms from dummy class")

    def u_atoms(self):
        raise BoltzmannFrameworkError("Cannot iterate over atoms from dummy class")

    def replace_l_atoms(self, sampler, x, y, exceptions=None):
        if len(exceptions) > self.l_size:
            raise BoltzmannFrameworkError("Too many exceptions for substitution")
        l_growth = -(self.l_size - len(exceptions))
        u_growth = 0
        for _ in range(self.l_size - len(exceptions)):
            gamma = sampler.sample(x, y)
            if gamma.l_size <= 0:
                raise BoltzmannFrameworkError("You may not use l-substitution when class contains objects of l-size 0")
            l_growth += gamma.l_size
            u_growth += gamma.u_size
        self._l_size += l_growth
        self._u_size += u_growth
        return self

    def replace_u_atoms(self, sampler, x, y, exceptions=None):
        if len(exceptions) > self.u_size:
            raise BoltzmannFrameworkError("Too many exceptions for substitution")
        l_growth = 0
        u_growth = -(self.u_size - len(exceptions))
        for _ in range(self.u_size - len(exceptions)):
            gamma = sampler.sample(x, y)
            if gamma.u_size < 0:
                raise BoltzmannFrameworkError("You may not use u-substitution when class contains objects of u-size 0")
            l_growth += gamma.l_size
            u_growth += gamma.u_size
        self._l_size += l_growth
        self._u_size += u_growth
        return self

    def __str__(self):
        return "(l: {}, u: {}".format(self.l_size, self.u_size)


class ZeroAtomClass(CombinatorialClass):
    """Represents the zero-atom."""

    @property
    def l_size(self):
        return 0

    @property
    def u_size(self):
        return 0

    # noinspection PyUnreachableCode
    def l_atoms(self):
        # This syntax implements an empty generator.
        return
        yield

    # noinspection PyUnreachableCode
    def u_atoms(self):
        # This syntax implements an empty generator.
        return
        yield

    def replace_l_atoms(self, sampler, x, y, exceptions=None):
        return self

    def replace_u_atoms(self, sampler, x, y, exceptions=None):
        return self

    def __str__(self):
        return '1'


class LAtomClass(ZeroAtomClass):
    """Represents an l-atom (labelled atom)."""

    @property
    def l_size(self):
        return 1

    def l_atoms(self):
        yield self

    def replace_l_atoms(self, sampler, x, y, exceptions=None):
        if exceptions is not None and self in exceptions:
            return self
        else:
            return sampler.sample(x, y)

    def __str__(self):
        try:
            return str(self.label)
        except AttributeError:
            return 'L'


class UAtomClass(ZeroAtomClass):
    """Represents a u-atom (unlabelled atom)."""

    @property
    def u_size(self):
        return 1

    def u_atoms(self):
        yield self

    def replace_u_atoms(self, sampler, x, y, exceptions=None):
        if exceptions is not None and self in exceptions:
            return self
        else:
            return sampler.sample(x, y)

    def __str__(self):
        return 'U'


class ProdClass(CombinatorialClass):
    """Represents an object from a cartesian product of two combinatorial classes.

    Parameters
    ----------
    first: CombinatorialClass
    second: CombinatorialClass
    """

    def __init__(self, first, second):
        self._first = first
        self._second = second

    @property
    def l_size(self):
        return self._first.l_size + self._second.l_size

    @property
    def u_size(self):
        return self._first.u_size + self._second.u_size

    def l_atoms(self):
        for atom in itertools.chain(self._first.l_atoms(), self._second.l_atoms()):
            yield atom

    def u_atoms(self):
        for atom in itertools.chain(self._first.u_atoms(), self._second.u_atoms()):
            yield atom

    def replace_l_atoms(self, sampler, x, y, exceptions=None):
        self._first = self._first.replace_l_atoms(sampler, x, y, exceptions)
        self._second = self._second.replace_l_atoms(sampler, x, y, exceptions)
        return self

    def replace_u_atoms(self, sampler, x, y, exceptions=None):
        self._first = self._first.replace_u_atoms(sampler, x, y, exceptions)
        self._second = self._second.replace_u_atoms(sampler, x, y, exceptions)
        return self

    def __str__(self):
        return "({},{})".format(self._first, self._second)


class SetClass(CombinatorialClass):
    """An object from the class of sets of objects of a combinatorial class.

    Parameters
    ----------
    elems: list of CombinatorialClass
    """

    def __init__(self, elems):
        self._elems = elems

    def __len__(self):
        """Returns the number of elements in the set."""
        return len(self._elems)

    def __iter__(self):
        """Returns an iterator over the set."""
        return iter(self._elems)

    @property
    def l_size(self):
        return sum([elem.l_size for elem in self._elems])

    @property
    def u_size(self):
        return sum([elem.u_size for elem in self._elems])

    def l_atoms(self):
        for elem in self._elems:
            for atom in elem.l_atoms():
                yield atom

    def u_atoms(self):
        for elem in self._elems:
            for atom in elem.l_atoms():
                yield atom

    def replace_l_atoms(self, sampler, x, y, exceptions=None):
        for index, child in enumerate(self._elems):
            self._elems[index] = child.replace_l_atoms(sampler, x, y, exceptions)
        return self

    def replace_u_atoms(self, sampler, x, y, exceptions=None):
        for index, child in enumerate(self._elems):
            self._elems[index] = child.replace_u_atoms(sampler, x, y, exceptions)
        return self

    def __str__(self):
        result = '['
        for elem in self._elems:
            result += "{}{}".format(str(elem), ',' if elem is not self._elems[-1] else '')
        result += ']'
        return result


class DerivedClass(CombinatorialClass):
    """Base class for l-derived and u-derived classes.

    A derived class is a combinatorial class where one atom is marked and does not count to the l-size/u-size.
    This class is not meant to be instantiated directly. Instantiate LDerivedClass or UDerivedClass instead.

    Parameters
    ----------
    base_class_object: CombinatorialClass
        The object form the underlying underived class.
    marked_atom: CombinatorialClass, optional (default=None)
        The distinguished atom. None stands for any random atom.

    Raises
    ------
    BoltzmannFrameworkError
        If the given atom does not exist in the base class object.
    """

    def __init__(self, base_class_object, marked_atom=None):
        if type(self) is DerivedClass:
            raise BoltzmannFrameworkError("Instantiate objects of LDerivedClass or UDerivedClass")
        self._base_class_object = base_class_object
        if marked_atom is not None:
            # Use the setter that checks if marked_atom is actually in the object
            self.marked_atom = marked_atom

    @property
    def marked_atom(self):
        """Returns the marked atom."""
        return self._marked_atom

    @marked_atom.setter
    def marked_atom(self, atom):
        """Sets the marked atom."""
        if atom is not None:
            # todo is the check expensive?
            atoms = itertools.chain(self.base_class_object.l_atoms(), self.base_class_object.u_atoms())
            if self.marked_atom not in atoms:
                raise BoltzmannFrameworkError("Given atom does not exist in base class object")
            self._marked_atom = atom

    @property
    def base_class_object(self):
        """Returns the object from the underlying underived class."""
        return self._base_class_object

    def invert_derivation_order(self):
        """Inverts the derivation order.

        Only works if the underlying class is a derived class as well.

        Raises
        ------
        BoltzmannFrameworkError
            If the underlying class is no derived class.
        """
        if not isinstance(self.base_class_object, DerivedClass):
            raise BoltzmannFrameworkError("Base class object is not from a derived class")
        # todo

    @property
    def l_size(self):
        return self.base_class_object.l_size

    @property
    def u_size(self):
        return self.base_class_object.u_size

    def l_atoms(self):
        return self.base_class_object.l_atoms()

    def u_atoms(self):
        return self.base_class_object.u_atoms()

    def replace_l_atoms(self, sampler, x, y, exceptions=None):
        return self.base_class_object.replace_l_atoms(sampler, x, y, exceptions)

    def replace_u_atoms(self, sampler, x, y, exceptions=None):
        return self.base_class_object.replace_u_atoms(sampler, x, y, exceptions)

    def __str__(self):
        raise NotImplementedError


class LDerivedClass(DerivedClass):
    """Wrapper for an l-derived class.

    An l-derived class is a combinatorial class where one l-atom is marked and does not count to the l-size.

    Parameters
    ----------
    base_class_object: CombinatorialClass
        The object form the underlying underived class.
    marked_l_atom: CombinatorialClass, optional (default=None)
        The distinguished l-atom. None stands for any random atom.
    """

    def __init__(self, base_class_object, marked_l_atom=None):
        super(LDerivedClass, self).__init__(base_class_object, marked_l_atom)

    @property
    def l_size(self):
        return self.base_class_object.l_size - 1

    def l_atoms(self):
        if self.marked_atom is None:
            # Select a random l-atom as the marked l-atom.
            self._marked_atom = self.random_l_atom()
        for l_atom in self.base_class_object.l_atoms():
            if l_atom != self.marked_atom:
                yield l_atom

    def replace_l_atoms(self, sampler, x, y, exceptions=None):
        if exceptions is None:
            exceptions = []
        if self.marked_atom is None:
            self._marked_atom = self.base_class_object.random_l_atom()
        exceptions.append(self.marked_atom)
        return self.base_class_object.replace_l_atoms(sampler, x, y, exceptions)

    def __str__(self):
        return "{}_dx".format(str(self.base_class_object))


class UDerivedClass(DerivedClass):
    """Wrapper for a u-derived class.

    """

    def __init__(self, base_class_object, marked_u_atom=None):
        super(UDerivedClass, self).__init__(base_class_object, marked_u_atom)

    @property
    def u_size(self):
        return self.base_class_object.u_size - 1

    def u_atoms(self):
        if self.marked_atom is None:
            # Select a random u-atom as the marked u-atom.
            self._marked_atom = self.random_u_atom()
        for u_atom in self.base_class_object.u_atoms():
            if u_atom != self.marked_atom:
                yield u_atom

    def replace_u_atoms(self, sampler, x, y, exceptions=None):
        if exceptions is None:
            exceptions = []
        if self.marked_atom is None:
            self._marked_atom = self.base_class_object.random_u_atom()
        exceptions.append(self.marked_atom)
        return self.base_class_object.replace_u_atoms(sampler, x, y, exceptions)

    def __str__(self):
        return "{}_dy".format(str(self.base_class_object))
