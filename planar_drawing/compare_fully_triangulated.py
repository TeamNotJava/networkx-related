import matplotlib.pyplot as plt
import networkx as nx


def main():
    while True:
        n = 50
        p = 1.0
        is_planar = False
        while not is_planar:
            G = nx.fast_gnp_random_graph(n, p)
            is_planar, embedding = nx.check_planarity(G)
            p *= 0.99
        print("Embedding: ", embedding.get_data())
        print("Displaying not fully triangulated drawing")
        plt.subplot(1, 2, 1)
        nx.draw_planar(embedding, node_size=2)

        pos = nx.combinatorial_embedding_to_pos(embedding, fully_triangulate=True)
        print("Displaying fully triangulated drawing")
        plt.subplot(1, 2, 2)
        nx.draw(G, pos, node_size=2)

        plt.show()


if __name__ == '__main__':
    main()
