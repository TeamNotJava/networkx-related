import random 
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.evaluation_oracle import EvaluationOracle
from framework.generic_samplers import *

class TestSampler(object):
    def setUp(self):
        """Setup various shared variables and functionality
        """
        # Set a seed to get reproducible test runs.
        random.seed(12345)

        Z = ZeroAtomSampler()
        L = LAtomSampler()
        U = UAtomSampler()

        Heads = AliasSampler('Heads')
        Tails = AliasSampler('Tails')
        CoinFlip = AliasSampler('CoinFlip')
        CoinFlip2 = AliasSampler('CoinFlip2')
        RecursiveFlip = AliasSampler('RecursiveFlip')

        Tree = AliasSampler('Tree')
        Bla = AliasSampler('Bla')
        Blub = AliasSampler('Blub')
        Blob = AliasSampler('Blob')


        self.coin_grammar = DecompositionGrammar()
        self.coin_grammar.add_rules({
            'Heads': L,
            'Tails': L,
            'CoinFlip': Heads + Tails,
            'CoinFlip2': CoinFlip * CoinFlip,
            'RecursiveFlip': CoinFlip + RecursiveFlip
        })
        self.coin_grammar.init()

        self.coin_oracle = EvaluationOracle({
            'x': 0.4999749994,
            'y': 1.0,  # this is not needed here
            'Heads(x,y)': 0.5,
            'Tails(x,y)': 0.5,
            'CointFlip(x,y)': 0.99005,
            'RecursiveFlip(x,y)': 0.99005
        })

        self.tree_grammar = DecompositionGrammar()
        self.tree_grammar.add_rules({
            'Tree': L + Tree * L * Blub,
            'Blub': USubsSampler(Bla, Blob),
            'Blob': L + U + Z,
            'Bla': LSubsSampler(Blub, Blob),
        })
        self.tree_grammar.init()

        self.tree_oracle = EvaluationOracle({
            'x': 0.4999749994,
            'y': 1.0,  # this is not needed here
            'Tree(x,y)': 0.99005
        })


    def test_sample_coin_grammar(self):
        """Test if for coint_grammar the pseudo random sampled element is equal to the expected result
        """
        BoltzmannSampler.oracle = self.coin_oracle
        coinflip = self.coin_grammar.sample('CoinFlip', 'x', 'y')

    def test_sample_tree_grammar(self):

        BoltzmannSampler.oracle = self.tree_oracle
        tree = self.tree_grammar.sample('Tree', 'x', 'y')
        print(tree)
        raise AssertionError
