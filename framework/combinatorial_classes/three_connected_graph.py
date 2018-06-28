from .generic_classes import CombinatorialClass, UAtomClass
from ..bijections.networks import u_atom_to_network
from ..bijections.network_substitution import EdgeByNetworkSubstitution


class EdgeRootedThreeConnectedPlanarGraph(CombinatorialClass):
    def __init__(self, vertices_list, edges_list, root_half_edge):
        # All of the vertices in the graph represented as half-edges.
        # Do not contain the vertices which are part from the root edge.
        self.vertices_list = vertices_list
        # the edges list not contain the root edge!
        self.edges_list = edges_list
        # Only one part from the root edge. The other can be accessed through the opposite pointer.
        self.root_half_edge = root_half_edge

    def get_u_size(self):
        # root edge does not count
        # see 3.4.2.
        return len(self.edges_list)

    def get_l_size(self):
        # The root vertices are not part from the vertices list, therefore we don't have to subtract 2.
        # see 3.4.2.
        return len(self.vertices_list)

    def u_atoms(self):
        raise NotImplementedError

    def l_atoms(self):
        raise NotImplementedError

    def random_u_atom(self):
        raise NotImplementedError

    def random_l_atom(self):
        raise NotImplementedError

    # we need this. in the network decomposition we have to replace the u atoms with networks
    def replace_u_atoms(self, sampler, x, y):
        # Get the edges for substitution in a separate list
        edges_for_subs = list(self.edges_list)

        # Instantiate an object from the substitute worker class
        edge_by_network_subs = EdgeByNetworkSubstitution()

        # Substitute the edges with a newly sampled network one by one
        for edge_for_substitution in edges_for_subs:
            # Sample a network for plugging in
            network = sampler.sample(x, y)
            edge_by_network_subs.substitute_edge_by_network(self, edge_for_substitution, network)

        # this is a dummy
        return self

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
        repr = 'Root Edge : %s \n' % self.root_half_edge.__repr__()
        repr += 'Vertices : %s' % self.vertices_list.__repr__()
        repr += 'Edges : %s' % self.edges_list.__repr__()
        return repr
