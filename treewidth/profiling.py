import networkx as nx
from networkx.algorithms.approximation.treewidth import treewidth_decomp_min_degree_faster, treewidth_decomp, min_degree_heuristic
import os
import cProfile
import pstats
import pandas as pd
pd.set_option('expand_frame_repr', False) # nicer printing of DataFrame

# configure these options
# download the benchmark here: https://people.mmci.uni-saarland.de/~hdell/pace17/he-instances-PACE2017-public-2016-12-02.tar.bz2
BENCHMARK_PATH = './he-instances-PACE2017-public-2016-12-02'
MAX_FILE_SIZE_IN_BYTE = 100 * 1000 # 500 KB
MAX_NODES = 2000
WHICH_STAT = 3 # 3 for cumtime, 2 for tottime
TOP = 10 # only print top x functions (sorted by mean)
PROFILED_CALL = 'treewidth_decomp_min_degree_faster(G)' # G traverses all loaded graphs


def load_graphs():
    print("loading graphs...")
    graphs = []

    for file in os.listdir(BENCHMARK_PATH):
        file = BENCHMARK_PATH + '/' + file
        # only load files with .gr file extension and max. allowed file size
        if file.endswith(".gr") and os.stat(file).st_size <= MAX_FILE_SIZE_IN_BYTE:
            # ignore lines beginning with 'p'
            G = nx.read_edgelist(file, comments = 'p')
            graphs.append(G)

    # remove too large graphs
    graphs = [G for G in graphs if G.number_of_nodes() <= MAX_NODES]

    print("loaded " + str(len(graphs)) + " graphs")
    node_avg = sum([G.number_of_nodes() for G in graphs]) / len(graphs)
    edge_avg = sum([G.number_of_edges() for G in graphs]) / len(graphs)
    print("node avg: " + str(node_avg))
    print("edge avg: " + str(edge_avg))
    print()

    return graphs


def run_profiler(graphs):
    print("running profiler ...")
    stats = {}
    tottime = 0

    for G in graphs:
        cProfile.runctx(PROFILED_CALL, globals(), locals(), 'stats')
        p = pstats.Stats('stats')
        p.strip_dirs()
        for method in p.stats.keys():
            # make a nicer looking key
            key = method[0] + ":" + str(method[1]) + "(" + method[2] + ")" if method[0] != "~" else method[2]
            if key not in stats:
                stats[key] = []
            stats[key].append(100 * p.stats[method][WHICH_STAT] / p.total_tt)
        tottime += p.total_tt

    return (stats, tottime)


def print_stats(stats):
    df = pd.DataFrame(stats)#, columns = col_names)
    # computes mean, std, min, max and quartiles
    df= df.describe()\
        .transpose()\
        .sort_values(by='mean', ascending=False)\
        .drop(['count', '25%', '75%'], axis=1)
    print(df[0:TOP])


def main():
    graphs = load_graphs()
    (stats, tottime) = run_profiler(graphs)
    print("total time: " + str(tottime))
    print_stats(stats)

if __name__ == '__main__':
    main()
