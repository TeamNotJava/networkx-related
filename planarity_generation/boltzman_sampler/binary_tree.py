# -*- coding: utf-8 -*-
#    Copyright (C) 2018 by
#    Marta Grobelna <marta.grobelna@rwth-aachen.de>
#    Petre Petrov <petrepp4@gmail.com>
#    Rudi Floren <rudi.floren@gmail.com>
#    Tobias Winkler <tobias.winkler1@rwth-aachen.de>
#    All rights reserved.
#    BSD license.
#
# Authors:  Marta Grobelna <marta.grobelna@rwth-aachen.de>
#           Petre Petrov <petrepp4@gmail.com>
#           Rudi Floren <rudi.floren@gmail.com>
#           Tobias Winkler <tobias.winkler1@rwth-aachen.de>

from random import random
from .utils import bern_choice
import networkx as nx
from collections import deque
from copy import copy

# Based on the short paper
class BinaryTreeSampler():
    """Sampler Class for Binary Trees.
    """

    # Holds the probabilites for our samplers
    probabilities = dict()

    # Tree Metadata
    # type => dict('num_black': num_black, 'num_white': num_white, 'total': total)
    # Type one of 'function' or 'derivate'
    # Todo: Come up with better naming.
    tree_metadata = dict()

    random_function = random

    def set_random(self, random_function):
        """Sets the used random function
        """
        self.random_function = random_function

    def set_probabilities(self, probabilities):
        """Sets the used probabilities
        """
        self.probabilities = probabilities


    def binary_tree(self, n, epsilon=None):
        """Sample a binary tree with size n.
        If epsilon is not None the size can be between n(1-epsilon) and n(1+epsilon)
        Returns a Networkx graph
        """
        # Todo: Setup Probablities based on n and epsilon
        # Here are some dummy values from values_GF_binary_trees.num
        self.set_probabilities({
            'black_rooted_tree': [0.50000000000000000000000000000000000000000000000001], # This value is not right
            '1_or_white_rooted_tree': [0.29444027241668624677334211446066783047187327275181], # 4th vector, ch_1_or_v
            '1_or_black_rooted_tree': [0.64599880333411088336319322928710639835896803889376], # 5th vecotr, ch_1_or_u
            'black_rooted_pointed_tree': [0.24414175944453005274066900998117727717575865253963], # 1st vector, ch_pU_pV
            'ch_U_or_pVV_or_VpV' : [0.00092404846499279191822170512841994980389724172358518, 0.50046227400160916426729702710187096162745453264042], # 2nd vector
            'white_rooted_pointed_tree': [0.50000000000000000000000000000000000000000000000001] # 3rd vector, ch_pUU_or_UpU
        })

        # Reset
        self.tree_metadata = {'num_black': 0, 'num_white': 0, 'total': 0}
        
        tree =  self.___binary_tree()
        for key in self.tree_metadata:
            tree.set_attributes(key, self.tree_metadata[key])

        stack = deque([tree])
        G=nx.empty_graph(self.tree_metadata['total'])

        while stack:
            node = stack.pop()
            label_node = node.attributes['label']
            G.nodes[label_node]['color'] = node.get_attribute('color')
            if node.left() is not None:
                left = node.left()
                stack.append(left)
                label_left = left.attributes['label']
                G.add_edge(label_node, label_left)
            if node.right() is not None:
                right = node.right()
                stack.append(right)
                label_right = right.attributes['label']
                G.add_edge(label_node, label_right)

        return G

    def binary_tree_sampler(self):
        """Binary tree function for use in other samples. 
        Returns a BinaryTree 
        """


        self.set_probabilities({
            'black_rooted_tree': [0.50000000000000000000000000000000000000000000000001], # This value is not right
            '1_or_white_rooted_tree': [0.29444027241668624677334211446066783047187327275181], # 4th vector, ch_1_or_v
            '1_or_black_rooted_tree': [0.64599880333411088336319322928710639835896803889376], # 5th vecotr, ch_1_or_u
            'black_rooted_pointed_tree': [0.24414175944453005274066900998117727717575865253963], # 1st vector, ch_pU_pV
            'ch_U_or_pVV_or_VpV' : [0.00092404846499279191822170512841994980389724172358518, 0.50046227400160916426729702710187096162745453264042], # 2nd vector
            'white_rooted_pointed_tree': [0.50000000000000000000000000000000000000000000000001] # 3rd vector, ch_pUU_or_UpU
        })

        # Reset
        self.tree_metadata = {'num_black': 0, 'num_white': 0, 'total': 0}
        tree =  self.___binary_tree()
        for key in self.tree_metadata:
            tree.set_attributes(key, self.tree_metadata[key])
        return tree


    # binary tree
    # GF: black rooted tree + white rooted tree
    # Sampler:
    # bern(black rooted tree / (black rooted + white rooted)) than 
    #   (black rooted tree) 
    # else 
    #   (white rooted tree)
    def ___binary_tree(self):
        if bern_choice(self.probabilities['black_rooted_tree'], self.random_function) is 0:
            tree = self.___black_rooted_tree()
        else:
            tree = self.___white_rooted_tree()

        return tree
        

    # black rooted tree
    # empty set it the 1 atom, we can just return None for that child
    # GF: black root * (0 + white rooted tree) * (0 + white rooted tree)
    # Sampler:
    # bern() then 1 else (white rooted tree) *
    # bern() then 1 else (white rooted tree)
    def ___black_rooted_tree(self):
        tree = BinaryTree()
        tree.set_attributes('color', 'black')
        tree.set_attributes('label', copy(self.tree_metadata['total']))
        # increase black nodes
        self.tree_metadata['num_black'] = self.tree_metadata['num_black'] + 1
        # increase total nodes
        self.tree_metadata['total'] = self.tree_metadata['total'] + 1
        # left is 0 or white rooted
        tree.leftChild = self.___empty_or_white_rooted()
        # right is 0 or white rooted
        tree.rightChild = self.___empty_or_white_rooted()
        
        return tree

    # Empty or black rooted tree
    # GF: 0 + black rooted tree
    # Sampler:
    # bern() then 0 else (black rooted tree)
    def ___empty_or_black_rooted(self):
        if bern_choice(self.probabilities['1_or_black_rooted_tree'], self.random_function) is 0:
            tree = None
        else:
            tree = self.___black_rooted_tree()

        return tree


    # white rooted tree
    # GF: white root * (0 + black rooted tree) * (0 + black rooted tree)
    # Sampler:
    # bern(0.1/ (0.1 + black rooted tree) ) then 0 else (black rooted tree) *
    # bern() then 0 else (black rooted tree)
    def ___white_rooted_tree(self):
        # Create Binary Tree
        tree = BinaryTree()
        tree.set_attributes('color', 'white')
        tree.set_attributes('label', copy(self.tree_metadata['total']))
        # increase black nodes
        self.tree_metadata['num_white'] = self.tree_metadata['num_white'] + 1
        # increase total nodes
        self.tree_metadata['total'] = self.tree_metadata['total'] + 1
        # left is 0 or white rooted
        tree.leftChild = self.___empty_or_black_rooted()
        # right is 0 or white rooted
        tree.rightChild = self.___empty_or_black_rooted()
        
        return tree

    # Empty or white rooted tree
    # GF: 0 + white rooted tree
    # Sampler:
    # bern() then 0 else (white rooted tree)
    def ___empty_or_white_rooted(self):
        if bern_choice(self.probabilities['1_or_white_rooted_tree'], self.random_function) is 0:
            tree = None
        else:
            tree = self.___white_rooted_tree()

        return tree

    # black pointed tree
    # GF: x_b * derivative of binary tree
    # Sampler:
    # bern(black rooted tree / (black rooted + white rooted)) than 
    #   (black rooted tree) 
    # else 
    #   (white rooted tree)
    def black_pointed_binary_tree(self):
        """Similar entry point like self.binary_tree() but black pointed
        Returns a networkx graph
        """
        # Reset
        self.tree_metadata = {'num_black': 0, 'num_white': 0, 'total': 0}
        
        tree =  self.___black_pointed_binary_tree()
        for key in self.tree_metadata:
            tree.attributes[key] = self.tree_metadata[key]

        # Todo: Create networkx graph from Tree.
        return tree

    def black_pointed_binary_tree_sampler(self):
        """Binary tree function for use in other samples. 
        Returns a BinaryTree 
        """

        # Reset
        self.tree_metadata = {'num_black': 0, 'num_white': 0, 'total': 0}
        tree =  self.___black_pointed_binary_tree()
        for key in self.tree_metadata:
            tree.attributes[key] = self.tree_metadata[key]
        return tree

    # Don't know just return the dx one.
    def ___black_pointed_binary_tree(self):
        return self.___dx_black_pointed_binary_tree()

    # derivatives of binary tree
    def ___dx_black_pointed_binary_tree(self):
        if bern_choice(self.probabilities['black_rooted_pointed_tree'], self.random_function) is 0:
            tree = self.___dx_black_pointed_black_rooted()
        else:
            tree = self.___dx_black_pointed_white_rooted()

        return tree
    
    def ___dx_black_pointed_white_rooted(self):
        # Create Binary Tree
        tree = BinaryTree()
        tree.attributes['color'] = 'white'
        tree.attributes['label'] = self.tree_metadata['total']
        # increase black nodes
        self.tree_metadata['num_white'] = self.tree_metadata['num_white'] + 1
        # increase total nodes
        self.tree_metadata['total'] = self.tree_metadata['total'] + 1
        if bern_choice(self.probabilities['white_rooted_pointed_tree'], self.random_function) is 0:
            # left is 0 or black rooted
            tree.leftChild = self.___empty_or_black_rooted()
            # right is "dxu"
            tree.rightChild = self.___dx_black_pointed_black_rooted()
        else:
            tree.leftChild = self.___dx_black_pointed_black_rooted()
            tree.rightChild = self.___empty_or_black_rooted()
        
        return tree
    
    def ___dx_black_pointed_black_rooted(self):
        case = bern_choice(self.probabilities['ch_U_or_pVV_or_VpV'], self.random_function)
        if case is 0:
            return self.___black_rooted_tree()
        else:
            tree = BinaryTree()
            tree.attributes['color'] = 'black'
            tree.attributes['label'] = self.tree_metadata['total']
            self.tree_metadata['num_black'] = self.tree_metadata['num_black'] + 1
            self.tree_metadata['total'] = self.tree_metadata['total'] + 1
            if case is 1:
                tree.leftChild = self.___empty_or_white_rooted()
                tree.rightChild = self.___dx_black_pointed_white_rooted()
            else:
                tree.leftChild = self.___dx_black_pointed_white_rooted()
                tree.rightChild = self.___empty_or_white_rooted()
        return tree

    # white pointed tree
    def dy_binary_tree_sampler(self):
        """Similar entry point like self.binary_tree() but white pointed
        """
        self.tree_metadata = {'num_black': 0, 'num_white': 0, 'total': 0}

        tree = self.__dy_binary_tree()
        for key in self.tree_metadata:
            tree.attributes[key] = self.tree_metadata[key]

        # Todo: Create networkx graph from Tree.
        return tree

    # We don't know if we need it later.
    #TODO I am not sure that the naming should be like this .. since the derivative is with respect to y
    def __dy_binary_tree(self):
        if bern_choice(self.probabilities['ch_dyu_or_dyv'], self.random_function) is 0:
            tree = self.___dy_black_rooted()
        else:
            tree = self.___dy_white_rooted()

        return tree
    
    def ___dy_black_rooted(self):
        case = bern_choice(self.probabilities['choose_vector_dyu'], self.random_function)
        if case is 0:
            return self.___black_rooted_tree()
        else:
            tree = BinaryTree()
            tree.attributes['color'] = 'white'
            tree.attributes['label'] = self.tree_metadata['total']
            self.tree_metadata['num_black'] = self.tree_metadata['num_black'] + 1
            self.tree_metadata['total'] = self.tree_metadata['total'] + 1
            if case is 1:
                tree.leftChild = self.___empty_or_black_rooted()
                tree.rightChild = self.___dx_black_pointed_black_rooted()
            else:
                tree.leftChild = self.___dx_black_pointed_black_rooted()
                tree.rightChild = self.___empty_or_black_rooted()
        return tree

    def ___dy_white_rooted(self):
        case = bern_choice(self.probabilities['choose_vector_dyv'], self.random_function)
        if case is 0:
            return self.___white_rooted_tree()
        else:
            tree = BinaryTree()
            tree.set_attributes('color', 'white')
            tree.set_attributes('label', self.tree_metadata['total'])
            self.tree_metadata['num_white'] = self.tree_metadata['num_white'] + 1
            self.tree_metadata['total'] = self.tree_metadata['total'] + 1
            if case is 1:
                tree.leftChild = self.___empty_or_black_rooted()
                tree.rightChild = self.___dx_black_pointed_black_rooted()
            else:
                tree.leftChild = self.___dx_black_pointed_black_rooted()
                tree.rightChild = self.___empty_or_black_rooted()
        return tree


class BinaryTree():
    """A Binary Tree representation
    """

    def __init__(self):
        self.attributes = dict()
        # Left Child
        leftChild = None
        # Right Child
        rightChild = None

    def right(self):
        return self.rightChild

    def left(self):
        return self.leftChild

    def set_attributes(self, key, val):
        self.attributes[key] = val
    
    def get_attributes(self):
        return self.attributes

    def get_attribute(self, key):
        return self.attributes[key]

    def __str__(self):
        repr = '['
        if self.left() == None:
            repr = repr + '0'
        else:
            repr = repr + self.right().__str__()

        if 'color' in self.attributes:
            if self.attributes['color'] is 'white':
                repr = repr + 'w'
            if self.attributes['color'] is 'black':
                repr = repr + 'b'
                
        if self.right() == None:
            repr = repr + '0'
        else:
            repr = repr + self.right().__str__()
        repr = repr + ']'
        return repr
    
# Shorthand version to just get a 
def binary_tree_sampler(n, **kwargs):
    return BinaryTreeSampler().binary_tree(n, **kwargs)