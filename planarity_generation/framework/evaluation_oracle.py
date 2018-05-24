class Oracle:
    # todo fill it with the evaluations
    def __init__(self):
        self.evaluations = {
            'x0': 0.249875,
            'y0': 1.0,
            'Tree(x0,y0)': 0.956257
        }

    def get(self, query_string):
        try:
            return self.evaluations[query_string]
        except(KeyError):
            print('Oracle key missing: {}'.format(query_string))
            return 0.5
