from ..combinatorial_classes.generic_classes import CombinatorialClass

class BinaryTree(CombinatorialClass):
    _id = 0

    def __init__(self, left, right, **kwargs):
        self.left = left
        self.right = right
        self.attributes = kwargs
        self._id = BinaryTree._id
        BinaryTree._id += 1

    def get_attribute(self, key):
        return self.attributes[key]

    def get_attributes(self):
        return self.attributes
    
    def get_u_size(self):
        return self.get_attribute('numleafs')

    def get_l_size(self):
        return self.get_attribute('numblacknodes')
    # Todo: hacky stuff following
    def random_l_atom(self):
        return None
    
    def random_u_atom(self):
        return None


    def __repr__(self):
        repr = '['
        if self.left is None:
            repr += '0'
        else:
            repr += str(self.left)

        if 'color' in self.attributes:
            if self.attributes['color'] is 'white':
                repr += 'w'
            if self.attributes['color'] is 'black':
                repr += 'b'
                
        if self.right is None:
            repr += '0'
        else:
            repr += str(self.right)
        repr += ']'
        return repr
    def __str__(self):
        return self.__repr__()
    
    def pretty(self, indent='', direction='updown'):
        label = "{0} ({1})".format(self._id, self.get_attribute('color'))
        if type(self.right) is BinaryTree:
            next_indent = '{0}{1}{2}'.format(indent, ' ' if 'up' in direction else '│', ' ' * len(label))
            self.right.pretty(next_indent, direction='up')
        else:
            print('{0}{1}{2}┌-'.format(indent, ' ' if 'up' in direction else '│', ' ' * len(label)))

        if direction == 'up': start_shape = '┌'
        elif direction == 'down': start_shape = '└'
        elif direction == 'updown': start_shape = ' '
        else: start_shape = '├'


        print('{0}{1}{2}{3}'.format(indent, start_shape, label, '┤'))

        if type(self.left) is BinaryTree:
            next_indent = '{0}{1}{2}'.format(indent, ' ' if 'down' in direction else '│', ' ' * len(label))
            self.left.pretty(next_indent, direction='down')
        else:
            print('{0}{1}{2}└-'.format(indent, ' ' if 'down' in direction else '│', ' ' * len(label)))



class Leaf(CombinatorialClass):
    def __init__(self):
        super()
