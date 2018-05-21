class Oracle:
    # todo fill it with the evaluations
    evaluations = {
        'x0': 0.249875,
        'y0': 1.0,
        'Tree(x0,y0)': 0.956257
    }

    def get(self, query_string):
        # print(query_string)
        if query_string in self.evaluations:
            return self.evaluations[query_string]
        else:
            return 0.5
