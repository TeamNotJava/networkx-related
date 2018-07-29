import networkx as nx

from framework.generic_classes import CombinatorialClass
from planar_graph_sampler.grammar.grammar_utils import Counter

from planar_graph_sampler.combinatorial_classes.halfedge import HalfEdge


class HalfEdgeGraph(CombinatorialClass):
    """
    Base class for all different flavours of graphs that show up in the decomposition:
    Bicolored binary trees, bicolored dissections, 3-connected maps, networks, 2-connected maps, 1-connected maps.

    Combinatorically, this simply represents the class of undirected graphs with labelled vertices and unlabelled edges,
    i.e. the l-size is the number of vertices and the u-size is the number of edges.

    Parameters
    ----------
    half_edge: HalfEdge
        A half-edge in the graph.
    """

    def __init__(self, half_edge):
        self._half_edge = half_edge

    @property
    def half_edge(self):
        """Returns the underlying half-edge for direct manipulation."""
        return self._half_edge

    @property
    def number_of_nodes(self):
        """Number of nodes in the graph."""
        return self._half_edge.get_number_of_nodes()

    @property
    def number_of_edges(self):
        """Number of edges in the graph."""
        return self._half_edge.get_number_of_edges()

    @property
    def number_of_half_edges(self):
        """Number of half-edges in the graph."""
        return len(self._half_edge.get_all_half_edges(include_unpaired=True, include_opp=True))

    @property
    def is_consistent(self):
        """Checks invariants (for debugging)."""
        return self._check_node_nr() #and self._check_no_double_edges()
        # TODO make more checks here

    def _check_node_nr(self, visited=None):
        """Check node_nr consistency."""
        if visited is None:
            visited = set()
        curr = self._half_edge
        visited.add(curr)
        incident = curr.incident_half_edges()
        if len(set([he.node_nr for he in incident])) > 1:
            return False
        for he in incident:
            if he.opposite is not None and he.opposite not in visited:
                if not HalfEdgeGraph(he.opposite)._check_node_nr(visited):
                    return False
        return True

    def _check_no_double_edges(self):
        # TODO
        return True

    # CombinatorialClass interface.

    @property
    def u_size(self):
        return self.number_of_edges

    @property
    def l_size(self):
        return self.number_of_nodes

    def u_atoms(self):
        raise NotImplementedError

    def l_atoms(self):
        raise NotImplementedError

    def replace_u_atoms(self, sampler, x, y, exceptions=None):
        """Maybe it's not so stupid to actually implement this here ... (same for l_subs)"""
        raise NotImplementedError

    def replace_l_atoms(self, sampler, x, y, exceptions=None):
        raise NotImplementedError

    def __str__(self):
        return "HalfEdgeGraph (Nodes: {}, Edges: {})".format(self.number_of_nodes, self.number_of_edges)

    # Networkx related functionality.

    @property
    def is_tree(self):
        return nx.is_tree(self.to_networkx_graph())

    @property
    def is_planar(self):
        return nx.check_planarity(self.to_networkx_graph())

    def is_connected(self, k=1):
        """
        Checks if the graph is k-connected.

        Parameters
        ----------
        k: int, optional (default=1)
            Check for k-connectivity.

        Returns
        -------
        bool
            True iff the graph is k-connected.
        """
        # TODO Check if this works the way intended.
        connectivity_dict = nx.k_components(self.to_networkx_graph())
        return len(connectivity_dict[k][0]) == self.number_of_nodes

    def planar_embedding(self, embedding=None):
        """Converts to format needed by planar graph drawer."""
        if embedding is None:
            embedding = {}
        node_nr = self._half_edge.node_nr
        if node_nr in embedding:
            res = nx.PlanarEmbedding()
            res.set_data(embedding)
            return res
        incident = self._half_edge.incident_half_edges()
        incident_node_nrs = [he.opposite.node_nr for he in incident if he.opposite is not None]
        embedding[node_nr] = incident_node_nrs
        for he in incident:
            if he.opposite is not None:
                HalfEdgeGraph(he.opposite).planar_embedding(embedding)
        res = nx.PlanarEmbedding()
        res.set_data(embedding)
        return res

    def to_networkx_graph(self, include_unpaired=False):
        """Transforms the graph into a networkx graph."""
        # Get the counter in case we have to create node for leaves (= unpaired half-edges).
        counter = Counter()
        # Get all edges (one half-edge per edge).
        half_edges = self.half_edge.get_all_half_edges(include_opp=False, include_unpaired=include_unpaired)
        G = nx.Graph()
        while len(half_edges) > 0:
            half_edge = half_edges.pop()
            if half_edge.opposite is not None:
                G.add_edge(half_edge.node_nr, half_edge.opposite.node_nr)
            else:
                G.add_edge(half_edge.node_nr, next(counter))
        return G

    def plot(self, **kwargs):
        """Plots the graph.

        Parameters
        ----------
        G: networkx.Graph


        """
        G = None
        with_labels = False
        use_planar_drawer = False
        node_size = 100
        if 'G' in kwargs:
            G = kwargs['G']
        if 'with_labels' in kwargs:
            with_labels = kwargs['with_labels']
        if 'use_planar_drawer' in kwargs:
            use_planar_drawer = kwargs['use_planar_drawer']
        if 'node_size' in kwargs:
            node_size = kwargs['node_size']

        if G is None:
            G = self.to_networkx_graph()
        # Generate planar embedding or use default algorithm.
        pos = None
        if use_planar_drawer:
            emb = self.planar_embedding()
            pos = nx.combinatorial_embedding_to_pos(emb, fully_triangulate=False)
        # Take color attributes on the nodes into account.
        colors = nx.get_node_attributes(G, 'color').values()
        if len(colors) == G.number_of_nodes():
            nx.draw(G, pos=pos, with_labels=with_labels, node_color=list(colors), node_size=node_size)
        else:
            nx.draw(G, pos=pos, with_labels=with_labels, node_size=node_size)


def color_scale(hex_str, factor):
    """Scales a hex string by ``factor``. Returns scaled hex string."""
    hex_str = hex_str.strip('#')
    if factor < 0 or len(hex_str) != 6:
        return hex_str
    r, g, b = int(hex_str[:2], 16), int(hex_str[2:4], 16), int(hex_str[4:], 16)

    def clamp(val, min=0, max=255):
        if val < min:
            return min
        if val > max:
            return max
        return int(val)

    r = clamp(r * factor)
    g = clamp(g * factor)
    b = clamp(b * factor)

    return "#%02x%02x%02x" % (r, g, b)
