from planar_graph_generator import PlanarGraphGenerator
import networkx as nx
import cProfile
import time
from planar_graph_sampler.evaluations_planar_graph import planar_graph_evals

def __time_statistics_for_different_graph_sizes():
    graphs_sizes = [30000, 40000, 50000, 75000, 100000]
    variances = [50]
    how_many_graphs_per_size = 10

    with open(("time_statistics_%s.txt" % variances[0]), "a") as stats_file:
        for N in graphs_sizes:
            for variance in variances:
                for i in range(how_many_graphs_per_size):
                    start = time.time()

                    generator = PlanarGraphGenerator()
                    gnx, lower_bound_errors, upper_bound_errors = generator.generate_planar_graph_with_statistics(N, variance)

                    end = time.time()
                    time_in_seconds = end - start
                    print(nx.info(gnx))
                    stats_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (N, variance,
                        gnx.number_of_nodes(), gnx.number_of_edges(), time_in_seconds, lower_bound_errors, upper_bound_errors ))
                    stats_file.flush()


def __time_statistics_for_different_graph_sizes_with_multiprocessing():
    graphs_sizes = [30000]
    variances = [50]
    how_many_graphs_per_size = 10

    with open(("time_statistics_parallel_impl_%s.txt" % variances[0]), "a") as stats_file:
        for N in graphs_sizes:
            for variance in variances:
                for i in range(how_many_graphs_per_size):
                    start = time.time()

                    generator = PlanarGraphGenerator()
                    gnx, lower_bound_errors, upper_bound_errors = generator.initial_multiprocess_implementation(N, variance)

                    end = time.time()
                    time_in_seconds = end - start
                    print(nx.info(gnx))
                    stats_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (N, variance,
                        gnx.number_of_nodes(), gnx.number_of_edges(), time_in_seconds, lower_bound_errors, upper_bound_errors ))
                    stats_file.flush()


def __time_statistics_for_graph_size_100_and_different_oracles():
    graphs_sizes = [100]
    variances = [50, 10]
    oracle_parameters = [100, 1000, 10000]
    how_many_graphs_per_size = 20

    with open("time_statistics_oracles.txt", "a") as stats_file:
        for N in graphs_sizes:
            for oracle_param in oracle_parameters:
                for variance in variances:
                    for i in range(how_many_graphs_per_size):
                        start = time.time()

                        generator = PlanarGraphGenerator()
                        gnx, lower_bound_errors, upper_bound_errors = \
                            generator.generate_planar_graph_with_statistics(N, variance, planar_graph_evals[oracle_param])

                        end = time.time()
                        time_in_seconds = end - start
                        print(nx.info(gnx))
                        stats_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (N, variance, oracle_param,
                            gnx.number_of_nodes(), gnx.number_of_edges(), time_in_seconds, lower_bound_errors, upper_bound_errors ))
                        stats_file.flush()


def __generate_planar_graph_profiling():
    generator = PlanarGraphGenerator()
    gnx, lower_bound_errors, upper_bound_errors = generator.generate_planar_graph_with_statistics(10000, 50)
    print(nx.info(gnx))






if __name__ == '__main__':
    #cProfile.run('__generate_planar_graph_profiling()')
    #__time_statistics_for_different_graph_sizes()
    #__time_statistics_for_graph_size_100_and_different_oracles()
    __time_statistics_for_different_graph_sizes_with_multiprocessing()

