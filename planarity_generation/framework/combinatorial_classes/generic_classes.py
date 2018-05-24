# generic combinatorial classes

import random as rn
from framework.utils import *


# todo may these classes should rather be called something like "ProdClassInstance" or "ProdClassObject"
# as they do not represent combinatorial classes as a whole but rather instances of them

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

    # this is an ugly method to avoid using isinstance or similar
    def is_l_atom(self):
        return False

    # this is an ugly method to avoid using isinstance or similar
    def is_u_atom(self):
        return False

    def __str__(self):
        raise NotImplementedError


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

    # this is an ugly method to avoid using isinstance or similar
    def is_l_atom(self):
        return True

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

    # this is an ugly method to avoid using isinstance or similar
    def is_u_atom(self):
        return True

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
                if child.is_u_atom():
                    # note that here we cannot simply write "child = ... "
                    children[children.index(child)] = sampler.sample(x, y)

    def replace_l_atoms(self, sampler, x, y):
        children = [self.first, self.second]
        for child in children:
            try:
                child.replace_l_atoms(sampler, x, y)
            except:
                if child.is_l_atom():
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
                if child.is_u_atom():
                    # note that here we cannot simply write "child = ... "
                    self.elems[self.elems.index(child)] = sampler.sample(x, y)

    def replace_l_atoms(self, sampler, x, y):
        for child in self.elems:
            try:
                child.replace_l_atoms(sampler, x, y)
            except:
                if child.is_l_atom():
                    # note that here we cannot simply write "child = ... "
                    self.elems[self.elems.index(child)] = sampler.sample(x, y)

    def __str__(self):
        result = '['
        for elem in self.elems:
            result += elem + ','
        result += ']'
        return result

class DerivedClass(CombinatorialClass):

    def __init__(self, base_class_object, marked_atom):
        self.marked_atom = marked_atom
        # the unmarked object from the underived base combinatorial class
        self.base_class_object = base_class_object

    def get_marked_atom(self):
        return self.marked_atom

    def get_base_class_object(self):
        return self.base_class_object


# wrapper for an l-derived class
class LDerivedClass(DerivedClass):
    def __init__(self, base_class_object, marked_l_atom):
        super(LDerivedClass, self).__init__(base_class_object, marked_l_atom)

    def get_l_size(self):
        return self.base_class_object.get_l_size() - 1

    def get_u_size(self):
        return self.base_class_object.get_u_size()

    def u_atoms(self):
        yield from self.base_class_object.u_atoms()

    def l_atoms(self):
        for l_atom in self.base_class_object.l_atoms():
            if l_atom != self.marked_atom:
                yield l_atom

    # invert the derivation order
    # the base class must be a UDerivedClass instance
    def to_dx_dy(self):
        gamma = self.base_class_instance.base_class_instance
        l_derived = LDerivedClass(gamma, self.marked_atom)
        u_derived = UDerivedClass(l_derived, self.base_class_instance.get_marked_atom())
        return u_derived

    def __str__(self):
        return str(self.base_class_instance) + "->" + str(self.marked_atom)


# wrapper for a u-derived class
class UDerivedClass(CombinatorialClass):
    def __init__(self, base_class_object, marked_u_atom):
        super(UDerivedClass, self).__init__(base_class_object, marked_u_atom)

    def get_l_size(self):
        return self.base_class_object.get_l_size()

    def get_u_size(self):
        return self.base_class_object.get_u_size() - 1

    def l_atoms(self):
        yield from self.base_class_object.l_atoms()

    def u_atoms(self):
        for u_atom in self.base_class_object.u_atoms():
            if u_atom != self.marked_u_atom:
                yield u_atom

    # invert the derivation order
    # the base class must be an LDerivedClass instance
    def to_dy_dx(self):
        try:
            gamma = self.base_class_object.base_class_instance
            u_derived = UDerivedClass(gamma, self.marked_u_atom)
            l_derived = LDerivedClass(u_derived, self.base_class_object.get_marked_atom())
            return l_derived
        except:
            print('could not change derivation order')
            raise

    def __str__(self):
        return str(self.base_class_object) + "->" + str(self.marked_u_atom)
