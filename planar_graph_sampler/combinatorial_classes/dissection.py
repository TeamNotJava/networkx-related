import random as rnd

from framework.generic_classes import CombinatorialClass


class IrreducibleDissection(CombinatorialClass):
    """
    Composition instead of inheritance here for now.
    """

    def __init__(self, half_edge):
        """

        :param half_edge: Half-edge on hexagon boundary in ccw direction.
        """
        print(half_edge.node_nr)
        print(half_edge.opposite.node_nr)
        assert half_edge.is_hexagonal
        if half_edge.color is not 'black':
            half_edge = half_edge.opposite.next
        assert half_edge.color is 'black'
        self.half_edge = half_edge

    def get_root(self):
        return self.half_edge

    def get_hexagonal_edges(self):
        first = self.half_edge
        res = [first]
        second = first.opposite.next.opposite.next
        res.append(second)
        third = second.opposite.next.opposite.next
        res.append(third)
        for he in res:
            assert he.is_hexagonal and he.color is 'black'
        return res

    def root_at_random_hexagonal_edge(self):
        self.half_edge = rnd.choice(self.get_hexagonal_edges())

    def get_u_size(self):
        raise NotImplementedError

    def get_l_size(self):
        raise NotImplementedError

    def u_atoms(self):
        pass

    def l_atoms(self):
        pass

    def replace_u_atoms(self, sampler, x, y):
        pass

    def replace_l_atoms(self, sampler, x, y):
        pass

    def plot(self):
        return self.half_edge.plot()

    def __str__(self):
        pass
