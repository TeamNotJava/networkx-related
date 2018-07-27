import networkx as nx
import urllib
import tarfile
import os
from timeit import default_timer as timer

links = [
    ('https://users.dcc.uchile.cl/~jfuentess/datasets/files/g/planar1M.tar.gz', 'planar_embedding1000000.pg'),
    ('https://users.dcc.uchile.cl/~jfuentess/datasets/files/g/planar5M.tar.gz', 'planar_embedding5000000.pg'),
    ('https://users.dcc.uchile.cl/~jfuentess/datasets/files/g/planar10M.tar.gz', 'planar_embedding10000000.pg'),
    ('https://users.dcc.uchile.cl/~jfuentess/datasets/files/g/planar15M.tar.gz', 'planar_embedding15000000.pg'),
    ('https://users.dcc.uchile.cl/~jfuentess/datasets/files/g/planar20M.tar.gz', 'planar_embedding20000000.pg'),
    ('https://users.dcc.uchile.cl/~jfuentess/datasets/files/g/planar25M.tar.gz', 'planar_embedding25000000.pg'),
    ('https://users.dcc.uchile.cl/~jfuentess/datasets/files/g/worldcities.tar.gz', 'worldcitiespop.pg')
]

graph_num = 1

graph_link = links[graph_num][0]
graph_tar = graph_link.split("/")[-1]
graph_file = links[graph_num][1]
print("Starting check on planar graph: " + graph_file)

time_start = timer()

if not os.path.isfile(graph_file):
    if not os.path.isfile(graph_tar):
        urllib.urlretrieve(graph_link, graph_tar)
    tar = tarfile.open(graph_tar)
    tar.extractall()
    tar.close()
    os.remove(graph_tar)

time_download_finished = timer()
print("Download time: {}".format(time_download_finished - time_start))

G = nx.read_edgelist(graph_file)

time_graph_import_finished = timer()
print("Graph successfully loaded. Graph import time: {}".format(time_graph_import_finished- time_download_finished))

res, embedding = nx.check_planarity(G)

time_planarity_check_finished = timer()
print("Planarity check time: {}".format(time_planarity_check_finished - time_graph_import_finished))

if not res:
    print("The check returned 'non planar'.")
    exit()

embedding.check_structure()

time_structure_check_finished = timer()
print("Everything is correct. Structure check time: {}".format(time_structure_check_finished - time_planarity_check_finished))
print("Complete time: {}".format(time_structure_check_finished - time_start))
