import networkx as nx

from ..combinatorial_classes.generic_classes import CombinatorialClass
from ..combinatorial_classes.three_connected_graph import EdgeRootedThreeConnectedPlanarGraph
from ..samplers.generic_samplers import BoltzmannSampler


class SpecialSampler1(BoltzmannSampler):


    def __init__(self, network_sampler):
        super(SpecialSampler1, self).__init__(network_sampler)

    def sampled_class(self) -> str:
        pass

    def get_eval(self, x: str, y: str) -> float:
        pass

    def sample(self, x: str, y: str) -> CombinatorialClass:
        pass

    def oracle_query_string(self, x: str, y: str) -> str:
        pass

    def get_children(self):
        pass


class SpecialSampler2(BoltzmannSampler):
    def __init__(self, something):
        pass

    def sampled_class(self) -> str:
        pass

    def get_eval(self, x: str, y: str) -> float:
        pass

    def sample(self, x: str, y: str) -> CombinatorialClass:
        pass

    def oracle_query_string(self, x: str, y: str) -> str:
        pass

# this is a dummy in the current version
class EdgeRootedThreeConnectedPlanarGraphSampler(BoltzmannSampler):
    def init__(self):
        pass

    def sampled_class(self):
        return 'G_3_arrow'

    def get_eval(self, x, y):
        return self.oracle.get(self.oracle_query_string(x, y))

    def sample(self, x, y):
        # todo this is a dummy
        graph = nx.Graph()
        graph.add_edges_from([
            (1, 3),
            (1, 7),
            (1, 6),
            (6, 7),
            (7, 4),
            (6, 5),
            (4, 5),
            (4, 3),
            (3, 2),
            (4, 2),
            (2, 5)
        ])
        root_edge = (1, 2)
        return EdgeRootedThreeConnectedPlanarGraph(graph, root_edge)

    def oracle_query_string(self, x: str, y: str) -> str:
        pass


class LDerThreeConnectedPlanarGraphSampler(BoltzmannSampler):
    def get_eval(self, x: str, y: str) -> float:
        pass

    def sample(self, x: str, y: str) -> CombinatorialClass:
        pass

    def oracle_query_string(self, x: str, y: str) -> str:
        pass

    def sampled_class(self) -> str:
        pass