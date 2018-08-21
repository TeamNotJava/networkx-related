from planar_graph_generator import PlanarGraphGenerator
import networkx as nx



if __name__ == '__main__':
    sampler = PlanarGraphGenerator()
    graph = sampler.generate_planar_graph(1000, 50)
    print(nx.info(graph))
