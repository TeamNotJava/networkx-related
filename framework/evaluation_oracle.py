from __future__ import division

import math


class EvaluationOracle:
    """Maintains a table of evaluations used by the samplers.

    """

    def __init__(self, evals=None):
        """

        :rtype: object
        :type evals: dict
        :param evals: The evals this oracle knows
        """
        if evals is None:
            evals = {}
        self.evals = evals

    def add_evals(self, evals):
        """Adds evaluations, overwrites existing keys.

        :type evals: dict
        :param evals: The new evaluations to be added
        """
        self.evals = {**self.evals, **evals}

    def get(self, query_string):
        """Gets an evaluation

        :type query_string: str
        :param query_string: The key in the evaluations dict
        :rtype: float
        """
        try:
            return self.evals[query_string]
        except KeyError:
            raise KeyError('Oracle key missing: {}'.format(query_string))

    def get_probability(self, class_label, symbolic_x, symbolic_y, l_size, u_size):
        """Computes the probability of an object with the given sizes."""
        query_string = '{}({},{})'.format(class_label, symbolic_x, symbolic_y)
        l_term = math.pow(self.get(symbolic_x), l_size) / math.factorial(l_size)
        u_term = math.pow(self.get(symbolic_y), u_size)
        return (l_term * u_term) / self.get(query_string)

    def get_expected_l_size(self, class_label, symbolic_x, symbolic_y):
        query_string = '{}({},{})'.format(class_label, symbolic_x, symbolic_y)
        query_string_dx = '{}_dx({},{})'.format(class_label, symbolic_x, symbolic_y)
        return self.get(symbolic_x) * self.get(query_string_dx) / self.get(query_string)

