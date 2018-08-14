import networkx as nx
from networkx.algorithms.tests.test_planar_drawing import planar_drawing_conforms_to_embedding, is_planar_drawing_correct
from nose.tools import assert_true

"""
This file must be run with python3, otherwise the import is not possible. 
"""

def test_random():
    while True:
        n = 50
        p = 1.0
        is_planar = False
        while not is_planar:
            G = nx.fast_gnp_random_graph(n, p)
            is_planar, embedding = nx.check_planarity(G)
            p *= 0.9
        pos = nx.combinatorial_embedding_to_pos(embedding,
                                                fully_triangulate=False)
        assert_true(planar_drawing_conforms_to_embedding(embedding, pos),
                    "Planar drawing does not conform to the embedding")
        assert_true(is_planar_drawing_correct(G, pos),
                    "Planar drawing is not correct")
        print("Graph correct")


if __name__ == '__main__':
    test_random()