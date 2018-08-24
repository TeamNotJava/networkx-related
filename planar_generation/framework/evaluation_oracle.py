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

from __future__ import division
import math

from framework.generic_classes import BoltzmannFrameworkError


class EvaluationOracle(object):
    """Maintains a table of evaluations used by the samplers.

    Parameters
    ----------
    evals: dict, optional (default=None)
        Generating function evaluations this oracle knows initially.

    Notes
    -----
    The evaluations can be accessed with a string that represents the 'symbolic evaluation' of the generating function.
    For example, for a class C, the evaluation of C at x and y can be accessed with 'C(x,y)' while the evaluation
    of D at x = z and y = C(x,z) for some other class D will have the key 'D(z,C(x,z))' and so on.
    Notice that in general generating functions are named by the label of the corresponding class.
    """

    def __init__(self, evals=None):
        if evals is None:
            evals = {}
        self.evals = evals

    def add_evals(self, evals):
        """Adds evaluations, overwrites existing keys.

        Parameters
        ----------
        evals: dict
            Generating function evaluations to be added to this oracle.
        """
        for key in evals:
            self.evals[key] = evals[key]

    def get(self, query_string):
        """Queries the oracle for an evaluation.

        Parameters
        ----------
        query_string: str
            The symbolic evaluation of the wanted generating function.

        Returns
        -------
        evaluation: float
        """
        try:
            return self.evals[query_string]
        except KeyError:
            raise BoltzmannFrameworkError('Oracle key missing: {}'.format(query_string))
            
    @staticmethod            
    def get_best_oracle_for_size(size, graph_evals):
        """Returns the best fitting oracle.
        
        This is choosen based on the sampling size. 
        The next bigger evaluations are chosen to sample more bigger graphs.
        
        Parameters
        ----------
        node_number: int
            The number of nodes the final graph should have.
        graph_evals: dict-of-dicts
            The evaluation of the generating function. 
            The size of the evaluation is used as key for the topmost dict.
        
        Returns
        -------
        orcale: EvaluationOracle
        """
        for eval_size in graph_evals.keys():
            if size <= eval_size:
                best_evals = graph_evals[eval_size]
                break
        
        return EvaluationOracle(best_evals)
        

    def __getitem__(self, query_string):
        """Same as EvaluationOracle.get(query_string).

        Parameters
        ----------
        query_string: str
            The symbolic evaluation of the wanted generating function.

        Returns
        -------
        evaluation: float
        """
        return self.get(query_string)

    def __contains__(self, query_string):
        """Checks whether this oracle contains a given evaluation.

        Parameters
        ----------
        query_string: str
            The symbolic evaluation of the wanted generating function.

        Returns
        -------
        bool
            True iff the oracle contains query_string.
        """
        return query_string in self.evals

    def contains_all(self, query_strings):
        """Checks whether this oracle contains all the evaluations in the given range.

        Parameters
        ----------
        query_strings: iterable
            An iterable of query_strings to check.

        Returns
        -------
        bool
            True iff all evaluations in query_string are present in the oracle.

        Notes
        -----
        May be used to check if all evaluations needed by a specific grammar exist in the oracle.
        """
        return all(q in self for q in query_strings)

    def get_probability(self, class_label, symbolic_x, symbolic_y, l_size, u_size):
        """Computes the probability of an object with the given sizes.

        Parameters
        ----------
        class_label: str
            The label of the class (= name of generating function).
        symbolic_x: str
            The symbolic x argument.
        symbolic_y: str
            The symbolic y argument.
        l_size: int
            The desired l-size.
        u_size: int
            The desired u-size.

        Returns
        -------
        probability: float
            The probability of an object from the given class under the Boltzmann distribution induced by the given
            parameters.
        """
        query_string = '{}({},{})'.format(class_label, symbolic_x, symbolic_y)
        l_term = math.pow(self[symbolic_x], l_size) / math.factorial(l_size)
        u_term = math.pow(self[symbolic_y], u_size)
        return (l_term * u_term) / self.get(query_string)

    def get_expected_l_size(self, class_label, symbolic_x, symbolic_y, class_label_dx=None):
        """Computes the expected l-size of an object from the given class.

        Parameters
        ----------
        class_label: str
            The label of the class (= name of generating function).
        symbolic_x: str
            The symbolic x argument.
        symbolic_y: str
            The symbolic y argument.
        class_label_dx: str, optional (default=None)

        Returns
        -------
        float
            Expected l-size of the sampled objects from the given class.

        Raises
        ------
        BoltzmannFrameworkError
            If the result could not be computed due to missing values in the oracle.

        Notes
        -----
        This will only work of the evaluation of the l-derived class is also available in the oracle.
        """
        query_string = '{}({},{})'.format(class_label, symbolic_x, symbolic_y)
        if class_label_dx is None:
            query_string_dx = '{}_dx({},{})'.format(class_label, symbolic_x, symbolic_y)
        else:
            query_string_dx = '{}({},{})'.format(class_label_dx, symbolic_x, symbolic_y)
        return self[symbolic_x] * self[query_string_dx] / self[query_string]
