import random 
from framework.decomposition_grammar import DecompositionGrammar, AliasSampler
from framework.generic_samplers import *
from framework.class_builder import CombinatorialClassBuilder

class TestGrammar(object):
    def setUp(self):
        """Setup various shared variables and functionality
        """
        # Set a seed to get reproducible test runs.
        random.seed(12345)

        Z = ZeroAtomSampler()

        self.grammar1 = DecompositionGrammar()
        self.grammar1.add_rules({
            'A': Z,
            'B': Z,
            'C': Z
        })
        
        

    def test_grammar_builder(self):
        """Test if a builder is applied to all 
        """
        class GrammarBuilder(CombinatorialClassBuilder):
            def zero_atom(self):
                return DummyClass()
            # TODO Add More


        self.grammar1.set_builder(['A', 'C'], GrammarBuilder())

        self.grammar1.init()

        # TODO check that each sampler has the correct builder set.