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

from .utils import bern_choice
from .binary_tree import BinaryTreeSampler

class ThreeConnectedGraphSampler:
    """Sampler Class for 3-Connected Planar Graphs.
    Uses the Binary Tree Sampler for sampling the 3-Connected Planar Graph.
    """

    def three_connected_graph(self, n, epsilon=None):
        """Sample a 3-Connected Planar Graph with size n.
        If epsilon is not None the size can be between n(1-epsilon) and n(1+epsilon)
        """
        return self.___three_connected_graph()

    # Corresponds to 
    def ___three_connected_graph(self):
        pass