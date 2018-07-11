from framework.generic_classes import *


class CombinatorialClassBuilder:
    """
    Interface for objects that build combinatorial classes.
    # TODO implement size checking mechanism.
    """

    def zero_atom(self):
        raise NotImplementedError

    def l_atom(self):
        raise NotImplementedError

    def u_atom(self):
        raise NotImplementedError

    def product(self, lhs, rhs):
        raise NotImplementedError

    def set(self, elements):
        raise NotImplementedError


class DefaultBuilder(CombinatorialClassBuilder):
    """
    Builds the generic objects.
    """

    def zero_atom(self):
        return ZeroAtomClass()

    def l_atom(self):
        return LAtomClass()

    def u_atom(self):
        return UAtomClass()

    def product(self, lhs, rhs):
        return ProdClass(lhs, rhs)

    def set(self, elements):
        return SetClass(elements)


class DummyBuilder(CombinatorialClassBuilder):
    """
    Builds dummy objects.
    """

    def zero_atom(self):
        return DummyClass()

    def l_atom(self):
        return DummyClass(l_size=1)

    def u_atom(self):
        return DummyClass(u_size=1)

    def product(self, lhs, rhs):
        l_size = lhs.get_l_size() + rhs.get_l_size()
        u_size = lhs.get_u_size() + rhs.get_u_size()
        return DummyClass(l_size, u_size)

    def set(self, dummies):
        l_size = 0
        u_size = 0
        for dummy in dummies:
            l_size += dummy.get_l_size()
            u_size += dummy.get_u_size()
        return DummyClass(l_size, u_size)
