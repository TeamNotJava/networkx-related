import matplotlib.pyplot as plt

class TimeStatatisticRow(object):
    """ Represents the full rows in stats files. """
    def __init__(self, target_nodes, variance, oracle_used, num_nodes, num_edges, time, trials):
        self.target_nodes = target_nodes
        self.variance = variance
        self.oracle_used = oracle_used
        self.num_nodes = num_nodes
        self.num_edges = num_edges
        self.time = time
        self.trials = trials

def read_stat_data(file_path, has_oracle):
    stat_data = []
    with open(file_path) as f_in:
        for line in f_in:
            parts = line.split('\t')
            if has_oracle:
                stat_data.append(
                    TimeStatatisticRow(int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]),
                                       int(parts[4]), float(parts[5]), int(parts[6]) + int(parts[7])))
            else:
                stat_data.append(TimeStatatisticRow(int(parts[0]), int(parts[1]), -1, int(parts[2]),
                                   int(parts[3]), float(parts[4]), int(parts[5]) + int(parts[6])))
    return stat_data

def plot_oracle_stat_data(data):
    data_by_variance = {d.variance:[] for d in data}
    for d in data:
        data_by_variance[d.variance].append(d)

    data_var_50 = data_by_variance[50]
    data_var_50_x = [d.oracle_used for d in data_var_50]
    data_var_50_y = [d.trials for d in data_var_50]

    data_var_10 = data_by_variance[10]
    data_var_10_x = [d.oracle_used for d in data_var_10]
    data_var_10_y = [d.trials for d in data_var_10]


    plt.plot(data_var_10_x, data_var_10_y, 'b+', markersize = 12, label='Variance=10')
    plt.plot(data_var_50_x, data_var_50_y, 'ro', markersize = 6, label='Variance=50')

    plt.axis([-50, 10500, 1, 200000])
    plt.xlabel('Oracles used')
    plt.ylabel('#trials')
    plt.title('Oracles effect over the number of trials in sampling 100 nodes graphs')
    plt.legend()
    plt.show()

def plot_stats_for_different_graph_sizes(data_50, data_20):

    data_var_50_x = [d.target_nodes for d in data_50]
    data_var_50_y = [d.time for d in data_50]
    data_var_20_x = [d.target_nodes for d in data_20]
    data_var_20_y = [d.time for d in data_20]

    plt.plot(data_var_50_x, data_var_50_y, 'ro', markersize = 4, label='Variance=50')
    plt.plot(data_var_20_x, data_var_20_y, 'b+', markersize = 4, label='Variance=20')

    plt.axis([-100, 20500, 1, 10000])
    plt.xlabel('#target nodes')
    plt.ylabel('time(s)')
    plt.title('Number of target nodes effect over needed time.')
    plt.legend()
    plt.show()

def plot_edges_nodes_ratio(data):
    more_than_500_nodes = []
    for d in data:
        if d.num_nodes >= 500:
            more_than_500_nodes.append(d)

    x_axis_data = [d.num_nodes for d in more_than_500_nodes]
    # Directed graph, therefore we should divide by 2
    y_axis_data = [d.num_edges / (2.0 * d.num_nodes) for d in more_than_500_nodes]

    plt.plot(x_axis_data, y_axis_data, 'ro', markersize = 1)

    plt.axis([-100, 20500, 2.0, 2.25])
    plt.xlabel('#nodes')
    plt.ylabel('ratio')
    plt.title('Edges vs. nodes ratio in grapsh bigger than 500.')
    #plt.legend()
    plt.show()


#oracle_data = read_stat_data('time_statistics_oracles.txt', True)
#plot_oracle_stat_data(oracle_data)

sampling_data_50 = read_stat_data('time_statistics_50.txt', False)
sampling_data_20 = read_stat_data('time_statistics_20.txt', False)
#plot_stats_for_different_graph_sizes(sampling_data_50, sampling_data_20)

plot_edges_nodes_ratio(sampling_data_20 + sampling_data_50)