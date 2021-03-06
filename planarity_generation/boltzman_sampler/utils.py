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

# Gets a list of probabilities
# Gets a random_function
# Returns the index or the size of the probabiliy.
# Acts as Bernoulli for len(probabilites) == 2
def bern_choice(probabilities, random_function) -> int:
    """Draws a random value with random_function and returns
    the index of a probability which the random value undercuts.
    The list is theoretically expanded to include 1-p
    """
    assert type(probabilities) is list
    random_value = random_function()
    for index in range(len(probabilities)):
        if random_value <= probabilities[index]:
            return index
    return len(probabilities)

def poiss(p) -> int:
    pass