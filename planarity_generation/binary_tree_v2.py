# -*- coding: utf-8 -*-

numb_nodes = 0
numb_black_nodes = 0
numb_white_nodes = 0


import random
from oracle import bern


##################################################################
#  THIS SAMPLER IS BASED ON THE PAPER "QUADRATIC EXACT-SIZE AND  #
#   LINEAR APPROXIMATE-SIZE RANDOM GENERATION OF PLANAR GRAPHS"  #
##################################################################


# BOLTZMANN SAMPLER FOR BICOLORED BINARY TREES




#Boltzmann sampler for rooted bicolored binary trees
#Generating function: T(x_black, x_white) = T_black(x_black, x_white) + T_white(x_black, x_white)
#Corresponds to draw_dyb(r)
def draw_binary_tree():
    #This probabiliy has to be calculated ---> just a dummy here
    dummy = random.uniform(0, 1)
    if bern([dummy]) == 0:
       BinaryTree.generated_black_root_node = True
       return draw_black_rooted_btree()
    else:
       BinaryTree.generated_black_root_node = false
       return draw_white_rooted_btree()



#Boltzmann sampler for black-rooted binary trees
#Generating function: T(x_black, x_white) = x_black(1 + T_white(x_black, x_white))^2
#Corresponds to draw_u
def draw_back_rooted_btree():
    #Update the number of black nodes and so the whole number of nodes
    self.numb_black_nodes += 1
    self.numb_nodes += 1

    #The sampler can either decide for an empty left (right) child or for new
    #children on the left (rigth)
    left_child = draw_empty_or_rooted_btree(1)
    right_child = draw_empty_or_rooted_btree(1)

    return BinaryTree(left_child, right_child)



#Boltzmann sampler for white-rooted binary trees
#Generating function: T(x_black, x_white) = x_white(1 + T_black(x_balck, x_white))^2
#Corresponds to draw_v
def draw_white_rooted_btree():
    #Update the number of black nodes and so the whole number of nodes
    self.numb_white_nodes += 1
    self.numb_nodes += 1
    
    #The sampler can either decide for an empty left (right) child or for new
    #children on the left (rigth)
    left_child = draw_empty_or_rooted_btree(0)
    right_child = draw_empty_or_rooted_btree(0)
    
    return BinaryTree(left_child, right_child)


#-------------------------------------------------------------------------------------------------
# Setting x_black = x * y and x_white = y, the correspondence of Proposition 4 (paper) transports
# a Boltzmann sampler GT(x_black, x_white), as defined in Lemma 7, into a sampler for rooted
# 3-connected maps. Thus, new generating function for bicolored binary trees look like this:
# T(x * y, y) = T_black(x*y, y) + T_white(x*y, y)
# T_black(x*y, y) = x * y * (1 + T_white(x*y, y))^2
# T_white(x*y, y) = y * (1 + T_black(x*y, y))^2
# LATER: Has to be evaluated at (x * D,D) see paper "Uniform random sampling of
# planar graphs in linear time" page 48
#------------------------------------------------------------------------------------------------

#Boltzmann sampler for derived rooted bicolored binary trees with respect to x
#Generating function: T(x * y, y) d/dx = T_black(x * y, y)d/dx + T_white(x*y, y)d/dx
#Corresponds to draw_dxb
def draw_binary_tree_dx():
    dummy = random.uniform(0, 1)
    if bern([dummy]) == 0:
        BinaryTree.generated_black_root_node = True
        return draw_black_rooted_btree_dx()
    else:
        BinaryTree.generated_black_root_node = False
        return draw_white_rooted_btree_dx()




#Boltzmann sampler for derived black-rooted binary trees with respect to x
#Generating function: T_black(x * y, y)d/dx = y * (1 + T_white(x*y, y))^2
#                       + x*y * T_white(x*y, y)d/dx * (1 + T_white(x*y,y))
#                       + x*y * (1 +T_white(x*y, y)) * T_white(x*y,y)d/dx
#Corresponds to draw_dxu
def draw_black_rooted_btree_dx():
    dummy_1 = random.uniform(0, 1)
    dummy_2 = (1 - dummy_1) * 1/3
    dummy_3 = (1 - dummy_1) * 2/3
    decision = bern([dummy_1, dummy_2, dummy_3])

    if decision == 0:
        return draw_black_rooted_btree()
    else:
        self.numb_black_nodes += 1
        self.numb_nodes += 1
        left_child = None
        right_child = None

        if decision == 1:
            left_child = draw_empty_or_rooted_btree(1)
            right_child = draw_white_rooted_btree_dx()
        else:
            left_child = draw_white_rooted_btree_dx()
            right_child = draw_empty_or_rooted_btree(1)

    return BinaryTree(left_child, right_child)






#Boltzmann sampler for derived white-rooted binary trees with respect to x
#Generating function: T_white(x_black, x_white)d/dx = y * T_black(x*y, y)d/dx
# * (1 + T_black(x*y,y)) + y * (1 + T_black(x*y,y)) * T_black(x*y, y)d/dx
#Corresponds to draw_dxv
def draw_white_rooted_btree_dx():
    dummy_1 = random.uniform(0, 1)
    decision = bern([dummy_1])

    self.numb_white_nodes += 1
    self.numb_nodes += 1
    left_child = None
    right_child = None

    if decision == 0:
        left_child = draw_empty_or_rooted_btree(0)
        right_child = draw_black_rooted_btree_dx()
    else:
        left_child = draw_black_rooted_btree_dx()
        right_child = draw_empty_or_rooted_btree(0)

    return BinaryTree(left_child, right_child)






#Boltzmann sampler for derived rooted bicolored binary trees with respect to y
#Generating function: T(x * y, y) d/dy = T_black(x * y, y)d/dy + T_white(x*y, y)d/dy
#Corresponds to draw_dyb
def draw_binary_tree_dy():
    dummy = random.uniform(0, 1)
    if bern([dummy]) == 0:
        BinaryTree.generated_black_root_node = True
        return draw_black_rooted_btree_dy()
    else:
        BinaryTree.generated_black_root_node = False
        return draw_white_rooted_btree_dy()



#Boltzmann sampler for derived black-rooted binary trees with respect to y
#Generating function: T_black(x*y, y)d/dy = x * (1 + T_white(x*y,y))^2
#                                   + x*y * T_white(x*y,y)d/dy * (1 + T_white(x*y, y))
#                                   + x*y * (1 + T_white(x*y, y)) * T_white(x*y,y)d/dy
#Corresponds to draw_dyu
def draw_black_rooted_btree_dy():
    dummy_1 = random.uniform(0, 1)
    dummy_2 = (1 - dummy_1) * 1/3
    dummy_3 = (1 - dummy_1) * 2/3
    decision = bern([dummy_1, dummy_2, dummy_3])

    if decision == 0:
        return draw_black_rooted_btree()
    else:
        self.numb_black_nodes += 1
        self.numb_nodes += 1
        left_child = None
        right_child = None

        if decision == 1:
            left_child = draw_empty_or_rooted_btree(1)
            right_child = draw_white_rooted_btree_dy()
        else:
            left_child = draw_white_rooted_btree_dy()
            right_child = draw_empty_or_rooted_btree(1)

    return BinaryTree(left_child, right_child)





#Boltzmann sampler for derived white-rooted binary trees with respect to y
#Generating function: T_white(x*y,y)d/dy = (1 + T_black(x*y,y))^2
#                                   + y * T_black(x*y,y)d/dy * (1 + T_black(x*y,y))
#                                   + y * (1 + T_black(x*y,y)) * T_black(x*y,y)d/dy
#Correspnds to draw_dyv
def draw_white_rooted_btree_dy():
    dummy_1 = random.uniform(0, 1)
    dummy_2 = (1 - dummy_1) * 1/3
    dummy_3 = (1 - dummy_1) * 2/3
    decision = bern([dummy_1, dummy_2, dummy_3])
    
    if decision == 0:
        return draw_white_rooted_btree()
    else:
        self.numb_white_nodes += 1
        self.numb_nodes += 1
        left_child = None
        right_child = None
        
        if decision == 1:
            left_child = draw_empty_or_rooted_btree(0)
            right_child = draw_black_rooted_btree_dy()
        else:
            left_child = draw_black_rooted_btree_dy()
            right_child = draw_empty_or_rooted_btree(0)

    return BinaryTree(left_child, right_child)




#Make decision between an emypty tree and a new black-rooted/white-rooted binary tree
#input: color: 0 is black-rooted, 1 is white-rooted
def draw_empty_or_rooted_btree(color):
    dummy = random.uniform(0, 1)
    decision_1 = bern([dummy])
    
    if decision_1 == 0:
        #Empty left child
        return  None
    else:
        if color == 0:
            #Generate new black-rooted binary tree
            return draw_black_rooted_btree()
        else:
            #Generate new white-rooted binary tree
            return draw_white_rooted_btree()




class BinaryTree:
    
    left_child = None
    right_child = None
    generated_black_root_node = True

    def __init__(self, left, right):
        self.left_child = left
        self.right_child = right
    
    def __str__(self):
        if self.left_child == None and self.right_child == None:
            return "[[][]]"
        if self.left_child == None:
            return "[[]" + self.right_child.__str__() + "]"
        if self.right_child == None:
            return "[" + self.left_child.__str__() + "[]]"
        
        return "[" + self.left_child.__str__() + self.right_child.__str__() + "]"
    
    def count(self):
        if self.left_child == None and self.right_child == None:
            return 1
        if self.left_child == None:
            return self.right_child.count() + 1
        if self.right_child == None:
            return self.left_child.count() + 1
        return self.left_child.count() + self.right_child.count() + 1






