import networkx as nx
import matplotlib.pyplot as plt

def main():
    # Cycle graph

    _, embedding = nx.check_planarity(nx.cycle_graph(20))
    embedding_fully, _ = nx.triangulate_embedding(embedding, True)
    diff_fully = nx.Graph(list(embedding_fully.edges - embedding.edges))
    embedding_internal, _ = nx.triangulate_embedding(embedding, False)
    diff_internal = nx.Graph(list(embedding_internal.edges - embedding.edges))
    pos = nx.combinatorial_embedding_to_pos(embedding_fully)
    nx.draw(diff_fully, pos, alpha=0.5, width=1, style="dotted", node_size=30)
    nx.draw(embedding, pos, width=2 , node_size=30)
    plt.savefig("drawing_cycle_fully_triangulated.png", format="PNG")
    plt.show()

    pos = nx.combinatorial_embedding_to_pos(embedding_internal)
    nx.draw(diff_internal, pos, alpha=0.5, width=1, style="dotted", node_size=30)
    nx.draw(embedding, pos, width=2, node_size=30)
    plt.savefig("drawing_cycle_internally_triangulated.png", format="PNG")
    plt.show()

    # Other graph
    G = nx.Graph([(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (1, 4), (4, 3)])
    is_planar, embedding = nx.check_planarity(G)
    print(is_planar)
    embedding_fully, _ = nx.triangulate_embedding(embedding, True)
    diff_fully = nx.Graph(list(embedding_fully.edges - embedding.edges))
    embedding_internal, _ = nx.triangulate_embedding(embedding, False)
    diff_internal = nx.Graph(list(embedding_internal.edges - embedding.edges))
    pos = nx.combinatorial_embedding_to_pos(embedding_fully)
    nx.draw(diff_fully, pos, alpha=0.5, width=1, style="dotted", node_size=30)
    nx.draw(embedding, pos, width=2, node_size=30)
    plt.savefig("drawing_other_fully_triangulated.png", format="PNG")
    plt.show()

    pos = nx.combinatorial_embedding_to_pos(embedding_internal)
    nx.draw(diff_internal, pos, alpha=0.5, width=1, style="dotted", node_size=30)
    nx.draw(embedding, pos, width=2, node_size=30)
    plt.savefig("drawing_other_internally_triangulated.png", format="PNG")
    plt.show()

    embedding_data = {0: [36, 42], 1: [], 2: [23, 16], 3: [19], 4: [23, 17], 5: [45, 18], 6: [42, 29, 40], 7: [48, 26, 32], 8: [15, 44, 23], 9: [11, 27], 10: [39, 11, 32, 47, 26, 15], 11: [10, 9], 12: [41, 34, 35], 13: [48], 14: [28, 45], 15: [34, 8, 10], 16: [2, 39, 21], 17: [4], 18: [5], 19: [22, 3], 20: [], 21: [16, 49], 22: [26, 47, 19], 23: [8, 2, 4], 24: [46], 25: [], 26: [7, 34, 10, 22, 38], 27: [9, 48], 28: [36, 41, 14], 29: [6], 30: [48], 31: [], 32: [7, 10, 46], 33: [48], 34: [12, 15, 26], 35: [12, 41], 36: [0, 28, 43], 37: [47], 38: [26], 39: [16, 10], 40: [6], 41: [28, 12, 35], 42: [44, 0, 6], 43: [36], 44: [8, 42], 45: [14, 5], 46: [32, 24], 47: [22, 10, 37], 48: [27, 7, 13, 30, 33], 49: [21]}
    embedding = nx.PlanarEmbedding()
    embedding.set_data(embedding_data)
    pos = nx.combinatorial_embedding_to_pos(embedding, fully_triangulate=False)
    nx.draw(embedding, pos, node_size=30)
    plt.savefig("drawing_large_graph_internally_triangulated.png", format="PNG")
    plt.show()






if __name__ == '__main__':
    main()