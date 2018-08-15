from planar_graph_generator import PlanarGraphGenerator
import networkx as nx
import cProfile
import time


def __generate_planar_graph():
    graphs_sizes = [100, 500, 1000, 1500, 2000, 3000, 4000, 5000, 7500, 1000]
    variances = [50]
    how_many_graphs_per_size = 10

    with open("time_statistics.txt", "a") as myfile:
        for N in graphs_sizes:
            for variance in variances:
                for i in range(how_many_graphs_per_size):
                    start = time.time()

                    generator = PlanarGraphGenerator()
                    gnx, lower_bound_errors, upper_bound_errors = generator.generate_planar_graph_for_profiling(N, variance)

                    end = time.time()
                    time_in_seconds = end - start
                    print(nx.info(gnx))
                    myfile.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (N, variances,
                        gnx.number_of_nodes(), gnx.number_of_edges(), time_in_seconds, lower_bound_errors, upper_bound_errors ))
                    myfile.flush()



if __name__ == '__main__':
    #cProfile.run('__generate_planar_graph()')
    __generate_planar_graph()