import random
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

    def replace_l_atom(self, atom, subs):
        """Replaces the given atom.

        Parameters
        ----------
        atom: l-atom
            The l-atom to replace.
        subs: CombinatorialClass
            The object to be plugged in.

        Raises
        ------
        SubstitutionError
            If the atom does not exist or the object to be plugged in is invalid.
        """
        raise NotImplementedError

    def replace_u_atom(self, atom, subs):
        """Replaces the given atom.

        Parameters
        ----------
        atom: u-atom
            The u-atom to replace.
        subs: CombinatorialClass
            The object to be plugged in.

        Raises
        ------
        BoltzmannFrameworkError
            If the atom does not exist or the object to be plugged in is invalid.
        """
        raise NotImplementedError

    def replace_l_atoms(self, sampler, x, y, exceptions=None):
        """Replaces all l-atoms within this object.

        Parameters
        ----------
        sampler: BoltzmannSamplerBase
        x: str
        y: str
        exceptions: list of CombinatorialClass
        """
        if exceptions is None:
            exceptions = []
        for atom in self.l_atoms():
            if atom not in exceptions:
                self.replace_l_atom(atom, sampler.sample(x, y))

    def replace_u_atoms(self, sampler, x, y, exceptions=None):
        """Replaces all u-atoms."""
        if exceptions is None:
            exceptions = []
        for atom in self.u_atoms():
            if atom not in exceptions:
                self.replace_u_atom(atom, sampler.sample(x, y))

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
        for _ in range(self.l_size):
            yield LAtomClass()

    def u_atoms(self):
        for _ in range(self.u_size):
            yield UAtomClass()

    def replace_l_atom(self, atom, subs):
        if not (isinstance(atom, LAtomClass)) or self.l_size < 1:
            raise BoltzmannFrameworkError("No such atom to replace.")
        self._l_size += subs.l_size - 1
        self._u_size += subs.u_size

    def replace_u_atom(self, atom, subs):
        if not (isinstance(atom, UAtomClass)) or self.u_size < 1:
            raise BoltzmannFrameworkError("No such atom to replace.")
        self._l_size += subs.l_size
        self._u_size += subs.u_size - 1

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

    def replace_l_atom(self, atom, subs):
        raise BoltzmannFrameworkError("Cannot replace anything inside an atom")

    def replace_u_atom(self, atom, subs):
        raise BoltzmannFrameworkError("Cannot replace anything inside an atom")

    def __str__(self):
        return '1'


class LAtomClass(ZeroAtomClass):
    """Represents an l-atom (labelled atom)."""

    @property
    def l_size(self):
        return 1

    def l_atoms(self):
        yield self

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

    def replace_l_atom(self, atom, subs):
        if self._first is atom:
            self._first = subs
        elif self._second is atom:
            self._second = subs
        else:
            try:
                self._first.replace_l_atom(atom, subs)
            except SubstitutionError:
                self._second.replace_l_atom(atom, subs)

    def replace_u_atom(self, atom, subs):
        if self._first is atom:
            self._first = subs
        elif self._second is atom:
            self._second = subs
        else:
            try:
                self._first.replace_u_atom(atom, subs)
            except SubstitutionError:
                self._second.replace_u_atom(atom, subs)

    def replace_l_atoms(self, sampler, x, y):
        # More efficient than the function implemented in the base class.
        children = [self._first, self._second]
        for child in children:
            try:
                child.replace_l_atoms(sampler, x, y)
            except BoltzmannFrameworkError:
                if isinstance(child, LAtomClass):
                    children[children.index(child)] = sampler.sample(x, y)

    def replace_u_atoms(self, sampler, x, y):
        # More efficient than the function implemented in the base class.
        children = [self._first, self._second]
        for child in children:
            try:
                child.replace_u_atoms(sampler, x, y)
            except BoltzmannFrameworkError:
                if isinstance(child, UAtomClass):
                    children[children.index(child)] = sampler.sample(x, y)

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
        return len(self._elems)

    def __iter__(self):
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

    def replace_l_atom(self, atom, subs):
        for i, elem in enumerate(self._elems):
            if elem is atom:
                self._elems[i] = subs
                return
        for elem in self._elems:
            try:
                elem.replace_l_atom(atom, subs)
                return
            except BoltzmannFrameworkError:
                pass
        raise BoltzmannFrameworkError("Could not find the given atom")

    def replace_u_atom(self, atom, subs):
        for i, elem in enumerate(self._elems):
            if elem is atom:
                self._elems[i] = subs
                return
        for elem in self._elems:
            try:
                elem.replace_u_atom(atom, subs)
                return
            except BoltzmannFrameworkError:
                pass
        raise BoltzmannFrameworkError("Could not find the given atom")

    def replace_l_atoms(self, sampler, x, y):
        for child in self._elems:
            try:
                child.replace_l_atoms(sampler, x, y)
            except BoltzmannFrameworkError:
                if isinstance(child, LAtomClass):
                    self._elems[self._elems.index(child)] = sampler.sample(x, y)

    def replace_u_atoms(self, sampler, x, y):
        for child in self._elems:
            try:
                child.replace_u_atoms(sampler, x, y)
            except BoltzmannFrameworkError:
                if isinstance(child, UAtomClass):
                    self._elems[self._elems.index(child)] = sampler.sample(x, y)

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
        if marked_atom is not None:
            atoms = itertools.chain(base_class_object.l_atoms(), base_class_object.u_atoms())
            if marked_atom not in atoms:
                raise BoltzmannFrameworkError("Given atom does not exist in base class object")
        self._marked_atom = marked_atom
        self._base_class_object = base_class_object

    @property
    def l_size(self):
        return self.base_class_object.l_size

    @property
    def u_size(self):
        return self.base_class_object.u_size

    def replace_l_atom(self, atom, subs):
        if self.marked_atom is atom:
            raise BoltzmannFrameworkError("In a derived class, the marked atom may not be replaced")
        self._base_class_object.replace_l_atom(atom, subs)

    def replace_u_atom(self, atom, subs):
        if self.marked_atom is atom:
            raise BoltzmannFrameworkError("In a derived class, the marked atom may not be replaced")
        self._base_class_object.replace_u_atom(atom, subs)

    def l_atoms(self):
        return self._base_class_object.l_atoms()

    def u_atoms(self):
        return self._base_class_object.u_atoms()

    @property
    def marked_atom(self):
        """Returns the marked atom."""
        return self._marked_atom

    @marked_atom.setter
    def marked_atom(self, atom):
        if atom is not None:
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

    def __str__(self):
        return "{}_dy".format(str(self.base_class_object))
