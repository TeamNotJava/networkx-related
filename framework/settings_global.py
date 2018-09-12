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

#from framework.generic_classes import BoltzmannFrameworkError


class Settings(object):
    """Holds global settings for the Boltzmann framework.

    """

    def __init__(self):
        #raise BoltzmannFrameworkError("This class is not meant to be instantiated")
        raise RuntimeError("This class is not meant to be instantiated")

    debug_mode = False


class Stats(object):
    rules = {}
