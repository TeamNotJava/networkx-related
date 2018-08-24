import networkx as nx
import random
import matplotlib.pyplot as plt


def sample_planar(n):
    while True:
        #m = random.randint(0, n * (n - 1) / 2)
        G = nx.gnp_random_graph(n, 0.6)
        is_planar, emb = nx.check_planarity(G)
        if is_planar and nx.is_connected(G):
            return G, emb


def sample_planar_connected(n):
    # # Eulerian formula only holds for n >= 3.
    # if n < 3:
    #     raise ValueError('n must be at least 3')
    # trials_count = 0
    #
    # while True:
    #     trials_count += 1
    #     # Generate a random number of edges.
    #     # There must be at least n-1 edges since otherwise the graph is disconnected.
    #     # There can be at most 3n-6 edges in a connected planar graph with at least 3 nodes (Euler).
    #     m = random.randint(n - 1, 3 * n - 6)
    #     G = nx.gnm_random_graph(n, m)
    #     if not nx.is_connected(G):
    #         continue
    #
    #     is_planar, emb = nx.check_planarity(G)
    #     if is_planar:
    #         # print("Trials: {}".format(trials_count))
    #         return G, emb
    while True:
        G, emb = sample_planar(n)
        if nx.is_connected(G):
            return G, emb


if __name__ == "__main__":
    # while True:
    #     G, emb = sample_planar_connected(4)
    #     pos = nx.combinatorial_embedding_to_pos(emb, fully_triangulate=True)
    #     nx.draw(G, pos=pos, with_labels=False, node_size=100)
    #     plt.show()


    c = [0, 0, 0, 0, 0, 0, 0]
    n = 4
    samples = 1000
    for _ in range(samples):
        G, emb = sample_planar(4)
        c[G.number_of_edges()] += 1

    print(c)
