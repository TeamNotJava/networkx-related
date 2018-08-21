from planar_graph_generator import PlanarGraphGenerator
import networkx as nx
import matplotlib.pyplot as plt



if __name__ == '__main__':
    sampler = PlanarGraphGenerator()
    graph = sampler.generate_planar_graph(100, 50)
    print(nx.info(graph))

    pos = nx.combinatorial_embedding_to_pos(graph)
    nx.draw(graph, pos, width=2, node_size=30)
    plt.savefig("planar_graph.png", format="PNG")
    plt.show()
