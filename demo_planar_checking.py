import networkx as nx

def main():
    print("Starting planarity check (planar grid graph 50x50)...")
    G = nx.grid_2d_graph(50, 50)
    is_planar, _ = nx.check_planarity(G)

    print("Planarity check result: " + str(is_planar))

    print("Starting planarity check (non planar modified grid graph 50x50)...")
    G = nx.grid_2d_graph(50, 50)
    G.add_edge((1, 1), (48, 48))
    is_planar, _ = nx.check_planarity(G)

    print("Planarity check result: " + str(is_planar))

if __name__ == '__main__':
    main()
