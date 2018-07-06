from framework.decomposition_grammar import *
from framework.evaluation_oracle import EvaluationOracle

# TODO make some reasonable things here or delete

def test_dummy_size():
    L = LAtomSampler()
    Tree = AliasSampler('Tree')

    tree_grammar = DecompositionGrammar()
    tree_grammar.add_rules({
        # tree is either a leaf or inner node with two children which are trees
        'Tree': L + Tree * L * Tree,
    })
    # init the grammar
    tree_grammar.init()

    tree_oracle = EvaluationOracle({
        'x': 0.4999749994,
        'y': 1.0,  # this is not needed here
        'Tree(x,y)': 0.99005
    })

    # inject the oracle into the samplers
    BoltzmannSampler.oracle = tree_oracle

    print(tree_grammar.collect_oracle_queries('Tree', 'x', 'y'))

    trees = [tree_grammar.sample('Tree', 'x', 'y') for _ in range(100)]
    print(sum([tree.get_l_size() for tree in trees]) / len(trees))

def coin():
    Heads = LAtomSampler()
    Tails = LAtomSampler()
    Nothing = ZeroAtomSampler()

    Throw = AliasSampler('Throw')

    coin_grammar = DecompositionGrammar()
    coin_grammar_rules = {
        'Throw': Nothing + (Heads * Throw),
        'Set_of_heads': SetSampler(0, Heads)
    }
    coin_grammar.add_rules(coin_grammar_rules)
    coin_grammar.init()

    coin_oracle = EvaluationOracle({
        'x': 10,
        'Throw(x,y)': 1 / (1 - 0.975),
        'y': 1.0
    })
    BoltzmannSampler.oracle = coin_oracle
    #[print(coin_grammar.sample('Throw', 'x', 'y')) for _ in range(10)]

    print(sum([coin_grammar.sample('Set_of_heads', 'x', 'y').get_l_size() for _ in range(1000)]) / 1000)



def tree():
    L = LAtomSampler()
    U = UAtomSampler()
    Z = ZeroAtomSampler()

    R_b = AliasSampler('R_b')
    R_w = AliasSampler('R_w')

    tree_grammar = DecompositionGrammar()
    tree_grammar_rules = {
        #'R_b': (UAtomSampler() + AliasSampler('R_w')) * LAtomSampler() * (UAtomSampler() + AliasSampler('R_w')),
        #'R_w': (UAtomSampler() + AliasSampler('R_b')) * (UAtomSampler() + AliasSampler('R_b')),
        'R_b': (U + R_w)**2 * L,
        'R_w': (U + R_b)**2,

    }
    tree_grammar.add_rules(tree_grammar_rules)
    tree_grammar.init()

    conv_rad = 0.0475080992953792
    tree_oracle = EvaluationOracle({
        'x': conv_rad - 1/(2*1000),
        'y': 1.0,
        'R_b(x,y)': 0.467436,
        'R_w(x,y)': 2.15337
    })
    BoltzmannSampler.oracle = tree_oracle
    # [print(tree_grammar.sample('R_b', 'x', 'y').get_l_size()) for _ in range(100)]

    print(sum([tree_grammar.sample('R_b', 'x', 'y').get_l_size() for _ in range(10000)]) / 10000)



if __name__ == "__main__":
    #test_dummy_size()
    tree()
