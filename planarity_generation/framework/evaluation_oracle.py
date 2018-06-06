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
