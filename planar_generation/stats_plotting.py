import matplotlib.pyplot as plt
import numpy as np

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


def plot_comparable_data(data_1, data_2, label1, label2, xlabel=None, ylabel=None, title=None):

    data_1_x = [d.target_nodes for d in data_1]
    data_1_y = [d.time for d in data_1]
    data_2_x = [d.target_nodes for d in data_2]
    data_2_y = [d.time for d in data_2]

    plt.plot(data_1_x, data_1_y, 'ro', markersize = 4, label=label1)
    plt.plot(data_2_x, data_2_y, 'b+', markersize = 4, label=label2)

    plt.axis([-100, 30500, 1, 3000])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.show()


def plot_regression_lines_on_comparable_data(data_1, data_2, label1, label2, xlabel=None, ylabel=None, title=None):

    data_1_x = [d.target_nodes for d in data_1]
    data_1_y = [d.time for d in data_1]
    data_2_x = [d.target_nodes for d in data_2]
    data_2_y = [d.time for d in data_2]

    fit_1 = np.polyfit(data_1_x, data_1_y, 1)
    fit_fn_1 = np.poly1d(fit_1)

    fit_2 = np.polyfit(data_2_x, data_2_y, 1)
    fit_fn_2 = np.poly1d(fit_2)

    x = [i for i in range(30000)]
    plt.plot(x, fit_fn_1(x), '--r', label=label1)
    plt.plot(x, fit_fn_2(x), '--b', label=label2)
    plt.xlim(0, 30000)
    plt.ylim(0, 2000)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
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

    plt.axis([-100, 30500, 2.0, 2.25])
    plt.xlabel('#nodes')
    plt.ylabel('ratio')
    plt.title('Edges vs. nodes ratio in graphs bigger than 500.')
    plt.show()


#oracle_data = read_stat_data('time_statistics_oracles.txt', True)
#plot_oracle_stat_data(oracle_data)

sampling_data_50 = read_stat_data('time_statistics_50.txt', False)
sampling_data_20 = read_stat_data('time_statistics_20.txt', False)
sampling_data_parallel_50 = read_stat_data('time_statistics_parallel_impl_50.txt', False)

plot_edges_nodes_ratio(sampling_data_20 + sampling_data_50 + sampling_data_parallel_50)


plot_comparable_data(
    sampling_data_50,
    sampling_data_parallel_50,
    'Serial sampling',
    'Sampling in parallel',
    '#target nodes',
    'time(s)',
    'Serial vs. parallel sampling.')


plot_regression_lines_on_comparable_data(
    sampling_data_50,
    sampling_data_parallel_50,
    'Serial sampling',
    'Sampling in parallel',
    '#target nodes',
    'time(s)',
    'Serial vs. parallel sampling.')