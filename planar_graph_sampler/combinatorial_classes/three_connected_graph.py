from framework.generic_classes import CombinatorialClass

from planar_graph_sampler.bijections.network_substitution import EdgeByNetworkSubstitution
from planar_graph_sampler.combinatorial_classes.half_edge_graph import HalfEdgeGraph


class EdgeRootedThreeConnectedPlanarGraph(HalfEdgeGraph):
    def __init__(self, root_half_edge, vertices=None, edges=None):
        # All of the vertices in the graph represented as half-edges.
        # Do not contain the vertices which are part from the root edge.
        #self.vertices_list = list(vertices)
        # the edges list not contain the root edge!
        #self.edges_list = list(edges)
        # Only one part from the root edge. The other can be accessed through the opposite pointer.
        #self.root_half_edge = root_half_edge
        super().__init__(root_half_edge)

    def get_u_size(self):
        # root edge does not count
        # see 3.4.2.
        #return len(self.edges_list)
        return self.number_of_edges() - 1

    def get_l_size(self):
        # The root vertices are not part from the vertices list, therefore we don't have to subtract 2.
        # see 3.4.2.
        # return len(self.vertices_list)
        return self.number_of_nodes() - 2

    # we need this. in the network decomposition we have to replace the u atoms with networks
    def replace_u_atoms(self, sampler, x, y):
        # Get the edges for substitution in a separate list
        #edges_for_subs = list(self.edges_list)
        edges_for_subs = self.half_edge.get_all_half_edges(include_opp=False, include_unpaired=False)
        # Don't substitute the root edge.
        edges_for_subs.remove(self.half_edge)
        edges_for_subs.remove(self.half_edge.opposite)

        # Instantiate an object from the substitute worker class
        edge_by_network_subs = EdgeByNetworkSubstitution()

        # Substitute the edges with a newly sampled network one by one
        for edge_for_substitution in edges_for_subs:
            # Sample a network for plugging in
            network = sampler(x, y)
            edge_by_network_subs.substitute_edge_by_network(edge_for_substitution, network)

        return self

    def __str__(self):
        repr = 'Root Edge : %s \n' % self.root_half_edge.__repr__()
        repr += 'Vertices : %s\n' % self.vertices_list.__repr__()
        repr += 'Edges : %s' % self.edges_list.__repr__()
        return repr
