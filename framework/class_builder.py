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
        """

        Parameters
        ----------
        lhs: CombinatorialClass
        rhs: CombinatorialClass
        """
        raise NotImplementedError

    def set(self, elements):
        """

        Parameters
        ----------
        elements: list of CombinatorialClass
        """
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
        l_size = lhs.l_size + rhs.l_size
        u_size = lhs.u_size + rhs.u_size
        return DummyClass(l_size, u_size)

    def set(self, elements):
        l_size = 0
        u_size = 0
        for dummy in elements:
            l_size += dummy.l_size
            u_size += dummy.u_size
        return DummyClass(l_size, u_size)
