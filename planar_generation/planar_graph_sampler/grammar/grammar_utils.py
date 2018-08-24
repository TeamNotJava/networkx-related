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

from framework.generic_classes import UDerivedClass, LDerivedClass


def underive(obj):
    """Returns the base class object of a derivec class."""
    return obj.base_class_object


def to_l_derived_class(obj):
    """Returns an u-derived version of the given object."""
    return LDerivedClass(obj)


def to_u_derived_class(obj):
    """Returns a u-derived version of the given object."""
    return UDerivedClass(obj)


def divide_by_2(evl, x, y):
    """Divides the given evaluation by 2. Needed for several samplers."""
    return 0.5 * evl


def singleton(class_):
    """Decorator for singleton class."""
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return get_instance


@singleton
class Counter(object):
    """
    This singleton Counter creates unique labels for combinatorial classes.
    This way we do not need to relabel the sampled elements for the product of two classes.
    """

    def __init__(self):
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        count = self.count
        self.count += 1
        return count
