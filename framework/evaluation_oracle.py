class Oracle:
    # todo fill it with the evaluations
    def __init__(self):
        self.evaluations = {
            '1+D(x*G_1_dx(x,y),y)': 0.5,
            'D(x*G_1_dx(x,y),y)': 0.5,
            'D_dx(x*G_1_dx(x,y),y)': 0.5,
            'G_1_dx(x,y)': 0.5,
            'G_1_dx_dx(x,y)': 0.5,
            'H(x*G_1_dx(x,y),y)': 0.5,
            'H_dx(x*G_1_dx(x,y),y)': 0.5,
            'P(x*G_1_dx(x,y),y)': 0.5,
            'P_dx(x*G_1_dx(x,y),y)': 0.5,
            'S(x*G_1_dx(x,y),y)': 0.5,
            'S_dx(x*G_1_dx(x,y),y)': 0.5,
            'exp_0(G_1(x,y))': 0.5,
            'x': 0.5,
            'x*G_1_dx(x,y)': 0.5,
            'y': 0.5,
        }

    def get(self, query_string):
        try:
            return self.evaluations[query_string]
        except(KeyError):
            print('Oracle key missing: {}'.format(query_string))
            return 0.5
