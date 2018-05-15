#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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