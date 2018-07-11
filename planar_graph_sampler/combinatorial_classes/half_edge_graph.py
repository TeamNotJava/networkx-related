import networkx as nx

from framework.generic_classes import CombinatorialClass
from framework.utils import Counter


class HalfEdgeGraph(CombinatorialClass):
    """
    Base class for all different flavours of graphs that show up in the decomposition:
    Bicolored binary trees, bicolored dissections, 3-connected maps, networks, 2-connected maps, 1-connected maps.

    Combinatorically, this simply represents the class of undirected graphs with labelled vertices and unlabelled edges,
    i.e. the l-size is the number of vertices and the u-size is the number of edges.
    """

    def __init__(self, half_edge):
        """

        :param half_edge:
        """
        self.half_edge = half_edge

    def is_consistent(self):
        """
        Checks invariants (for debugging).
        :return:
        """
        return self.check_node_nr()
        # TODO make more checks here

    def check_node_nr(self, visited=set()):
        """
        Check node_nr consistency.

        :return:
        """
        curr = self.half_edge
        visited.add(curr)
        incident = curr.incident_half_edges()
        if len(set([he.node_nr for he in incident])) > 1:
            return False
        for he in incident:
            if he.opposite is not None and he.opposite not in visited:
                if not HalfEdgeGraph(he.opposite).check_node_nr(visited):
                    return False
        return True

    def get_half_edge(self):
        """
        :return:
        """
        return self.half_edge

    def number_of_nodes(self):
        """

        :return:
        """
        return self.half_edge.get_number_of_nodes()

    def number_of_edges(self):
        """

        :return:
        """
        return self.half_edge.get_number_of_edges()

    def number_of_half_edges(self):
        """

        :return:
        """
        return len(self.half_edge.list_half_edges())

    def u_atoms(self):
        pass

    def l_atoms(self):
        pass

    # CombinatorialClass interface.

    def get_u_size(self):
        return self.number_of_edges()

    def get_l_size(self):
        return self.number_of_nodes()

    def replace_u_atoms(self, sampler, x, y):
        """
        Maybe it's not so stupid to actually implement this here ... (same for l_subs)
        :param sampler:
        :param x:
        :param y:
        :return:
        """
        raise NotImplementedError

    def replace_l_atoms(self, sampler, x, y):
        raise NotImplementedError

    def __str__(self):
        repr = ""
        try:
            repr += "L-size: {0}\n".format(self.get_l_size())
        except NotImplementedError:
            pass
        try:
            repr += "U-size: {0}\n".format(self.get_u_size())
        except NotImplementedError:
            pass
        return repr

    # Networkx based functionality.

    def is_tree(self):
        return nx.is_tree(self.to_networkx_graph())

    def is_planar(self):
        return nx.check_planarity(self.to_networkx_graph())

    def is_connected(self, k=1):
        """
        Checks if the graph is k-connected.

        :param k: default 1
        :return: True iff the graph is k-connected.
        """
        pass #TODO

    def to_networkx_graph(self, include_unpaired=False):
        """
        Transforms a list of planar map half-edged into a networkx graph.
        :return:
        """
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

    def plot(self):
        """

        :param colors:
        :return:
        """
        G = self.to_networkx_graph()
        colors = nx.get_node_attributes(G, 'color').values()
        if len(colors) == G.number_of_nodes():
            nx.draw(G, with_labels=True, node_color=list(colors))
        else:
            nx.draw(G, with_labels=True)


def color_scale(hexstr, factor):
    """
    Scales a hex string by ``factor``. Returns scaled hex string.

    To darken the color, use a float value between 0 and 1.
    To brighten the color, use a float value greater than 1.

    >>> color_scale("#DF3C3C", .5)
    #6F1E1E
    >>> color_scale("#52D24F", 1.6)
    #83FF7E
    >>> color_scale("#4F75D2", 1)
    #4F75D2
    """

    hexstr = hexstr.strip('#')

    if factor < 0 or len(hexstr) != 6:
        return hexstr

    r, g, b = int(hexstr[:2], 16), int(hexstr[2:4], 16), int(hexstr[4:], 16)

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
