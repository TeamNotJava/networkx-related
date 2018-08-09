from planar_graph_generator import PlanarGraphGenerator
import networkx as nx

if __name__ == '__main__':
    generator = PlanarGraphGenerator()
    gnx = generator.generate_planar_graph(1000, 50)
    print(nx.info(gnx))