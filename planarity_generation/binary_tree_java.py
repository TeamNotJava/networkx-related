# -*- coding: utf-8 -*-
#   Copyright (C) 2018 by
#   Rudolf-Andreas Floren <rudi.floren@gmail.com>
#   All rights reserved.
#   BSD license.

import random

# class BoltzmanSampler:
#     #graph = planar_embedding
#     def boltzman_n_sampler(size):
#         #p_g is the radius of convergence of x -> G(x,1)
#         x_n = (1 - 1/(2*size))*p_g
#         #repeat
#         self.graph = self.sample_planar(x_n,1)
#         #until len(self.graph.nodes) = size
#         return self.graph
#     def boltzman_ne_sampler(size, epsilon):
#         #p_g is the radius of convergence of x -> G(x,1)
#         x_n = (1 - 1/(2*size))*p_g
#         #repeat
#         self.graph = self.sample_planar(x_n,1)
#         #until len(self.graph.nodes) between size(1-epsilon) and size(1+epsilon)
#         return self.graph

#     def boltzman_nu_sampler(size, param1):
#         y_param1 = smth
#         x_n = (1-(1/(2*size)))*p_g(y_param1)
#         #repeat
#         self.graph = self.sample_planar(x_n, y_param1)
#         #until number_of_nodes == size and number_of_edges == floor(param1*size)
#         return self.graph

#     def boltzman_nue_sampler(size, param1, epsilon)
#         y_param1 = 'smth'
#         x_n = (1-(1/(2*size)))*p_g(y_param1)
#         #repeat
#         self.graph = self.sample_planar(x_n, y_param1)
#         #until number_of_nodes between size(1-epsilon) and size(1+epsilon) and number_of_edges/number_of_nodes between param1(1-epsilon) and param1(1+epsilon)
#         return self.graph

#     def sample_planar(x, y):
#         # call of boltzman_G''
#         (self.graph, star, star2) = boltzman_g_connected(x, y)
#         #label star with num_of_nodes+1
#         #label star2 with num_of_nodes+2
#         return self.graph


class ChooseVector:
    def __init__(self, values):
        self.values = values

    def choose(self, r):
        c = r.random()
        for i in range(len(self.values)):
            if c <= self.values[i]:
                return i
        return len(self.values)

class BoltzmanBinaryTree:

    countblacknodes = 0
    countwhitenodes = 0
    countnodes = 0
    rootNodeOfLastGeneratedTreeBlack = True
    

    ch_1_or_u = ChooseVector([0.6617244467515780200511702962325881919461])
    ch_1_or_v = ChooseVector([0.2858251517783132686093476090623008806938])
    ch_u_or_v = ChooseVector([0.1698436191398492749386028612247707092676])
    ch_dxu_or_dxv = ChooseVector([0.2321895767742127528955015279566147411533])
    ch_dxu = ChooseVector([0.03364843240680449808471298087340416706550, 0.5168242162034022490423564904367020835326])
    ch_dxv = ChooseVector([0.5])
    ch_dyu_or_dyv = ChooseVector([0.2285947884014483960930573391284945286581]) 
    ch_dyv = ChooseVector([0.02007003083676521369847607696835456844309, 0.5100350154183826068492380384841772842214])
    ch_dyu = ChooseVector([0.01385650199231473983487769712576176063940, 0.5069282509961573699174388485628808803199])

    def binary_tree(self):
        return self.draw_dyb()


    def draw_dyb(self):
        self.rootNodeOfLastGeneratedTreeBlack = True
        r = random
        # r.seed()
        c = self.ch_dyu_or_dyv.choose(r)
        if c == 0:
            # BinaryTree tree=draw_dyu(r);
            tree = self.draw_dyu(r)
            self.rootNodeOfLastGeneratedTreeBlack = True
            return tree
        else:
            # BinaryTree tree=draw_dyu(r);
            tree = self.draw_dyv(r)
            self.rootNodeOfLastGeneratedTreeBlack = False
            return tree


    def draw_dyv(self, r):
        print("draw_dyv")
        c = self.ch_dyv.choose(r)
        if c == 0:
            return self.draw_v(r)
        else:
            self.countnodes = self.countnodes + 1
            self.countwhitenodes = self.countwhitenodes + 1

            if c == 1:
                leftSon = self.draw_1_or_u(r)
                rightSon = self.draw_dyu(r)
            else:
                leftSon = self.draw_dyu(r)
                rightSon = self.draw_1_or_u(r)

            return BinaryTree(leftSon, rightSon)


    def draw_dyu(self, r):
        print("draw_dyu")
        '''DOC HERE'''
        c = self.ch_dyu.choose(r)
        if c == 0:
            return self.draw_u(r)
        else:
            self.countnodes = self.countnodes + 1
            self.countblacknodes = self.countblacknodes + 1

            if(c == 1):
                leftSon = self.draw_1_or_v(r)
                rightSon = self.draw_dyv(r)
            else:
                leftSon = self.draw_dyv(r)
                rightSon = self.draw_1_or_v(r)


            return BinaryTree(leftSon, rightSon)

    def draw_1_or_v(self, r):
        c = self.ch_1_or_v.choose(r)
        if c == 0:
            return None
        else:
            return self.draw_v(r)

    def draw_1_or_u(self, r):
        print("draw_1_or_u")
        c = self.ch_1_or_u.choose(r)
        if c == 0:
            return None
        else:
            return self.draw_u(r)

    def draw_u(self, r):
        print("draw_u")
        self.countblacknodes = self.countblacknodes + 1
        self.countnodes = self.countnodes + 1
        leftSon = self.draw_1_or_v(r)
        rightSon = self.draw_1_or_v(r)
        return BinaryTree(leftSon, rightSon)

    def draw_v(self, r):
        print("draw_v")
        self.countwhitenodes = self.countwhitenodes + 1
        self.countnodes = self.countnodes + 1
        leftSon = self.draw_1_or_u(r)
        rightSon = self.draw_1_or_u(r)
        return BinaryTree(leftSon, rightSon)



class BinaryTree:
    leftChild = None
    rightChild = None

    def __init__(self, left, right):
        self.leftChild = left
        self.rightChild = right

    def __str__(self):
        if self.leftChild == None and self.rightChild == None:
            return "[[][]]"
        if self.leftChild == None:
            return "[[]" + self.rightChild.__str__() + "]"
        if self.rightChild == None:
            return "[" + self.leftChild.__str__() + "[]]"
        
        return "[" + self.leftChild.__str__() + self.rightChild.__str__() + "]"

    def count(self):
        if self.leftChild == None and self.rightChild == None:
            return 1
        if self.leftChild == None:
            return self.rightChild.count() + 1
        if self.rightChild == None:
            return self.leftChild.count() + 1
        return self.leftChild.count() + self.rightChild.count() + 1





# def printer(tree)
#     if tree == None:
#         print("[]")
# 	else:
#         print("(")
#         print(printer(tree.leftSon))
#         print(printer(tree.rightSon))
#         print(")")

if __name__ == "__main__":
    print("Running Boltzman Binary Tree Sampler")
    tree = BoltzmanBinaryTree().binary_tree()
    print(tree)
    print(tree.leftChild.count())
    print(tree.rightChild.count())