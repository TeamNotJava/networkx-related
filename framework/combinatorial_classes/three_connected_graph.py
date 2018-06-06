from .generic_classes import CombinatorialClass, UAtomClass
from ..bijections.networks import u_atom_to_network


class EdgeRootedThreeConnectedPlanarGraph(CombinatorialClass):
    def __init__(self, graph, root_edge):
        # the graph does not contain the root edge!
        self.graph = graph
        self.root_edge = root_edge

    def get_u_size(self):
        # root edge does not count
        # see 3.4.2.
        return self.graph.numer_of_edges()

    def get_l_size(self):
        # root vertices do not count
        # see 3.4.2.
        return self.graph.number_of_nodes() - 2

    def u_atoms(self):
        raise NotImplementedError

    def l_atoms(self):
        raise NotImplementedError

    def random_u_atom(self):
        raise NotImplementedError

    def random_l_atom(self):
        raise NotImplementedError

    # we need this. in the network decomposition we have to replace the u atoms with networks
    # todo HOW?? in figure 9 it says in a 'canonical way', wtf ...
    def replace_u_atoms(self, sampler, x, y):
        # this is a dummy
        return u_atom_to_network(UAtomClass())

    # not needed as we never have l substitution in EdgeRootedThreeConnectedPlanarGraphs
    def replace_l_atoms(self, sampler, x, y):
        raise NotImplementedError

    # this is an ugly method to avoid using isinstance or similar
    def is_l_atom(self):
        raise NotImplementedError

    # this is an ugly method to avoid using isinstance or similar
    def is_u_atom(self):
        raise NotImplementedError

    def __str__(self):
        repr = 'Root Edge : %s \n' % self.root_edge.__repr__()
        repr += 'Graph Representation : %s' % self.graph.__repr__()
        return repr
