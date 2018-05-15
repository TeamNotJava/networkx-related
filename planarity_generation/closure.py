#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This class is needed for transformation of a Boltzmann sampler for bicolored binary trees
into a Boltzmann sampler for 3-connected planar graphs.
"""


##################################################################
#  THIS IS BASED ON THE PAPER "DISSECTIONS AND TREES, WITH WITH  #
#  APPLICATIONS TO OPTIMAL MESH ENCODING AND TO RANDOM SAMPLING" #
##################################################################

from binary_tree import BinaryTreeSampler
from halfedge import HalfEdge

class Closure:

    number_proximate_inner_edges = 0


#Convert a binary tree int o planar map
def ___btree_to_planar_map(btree):
    init_half_edge = HalfEdge()
    construct_planar_map(btree, init_half_edge)
    #Destroy the initial half-edge as it is only needed to construct its opposite
    init_half_edge.opposite.opposite = None
    return init_half_edge.opposite



#Consturct planer map out of a binary tree, i.e., make the binary tree
#tri-oriented
def ___construct_planar_map(btree, init_half_edge):
    half_edge_1 = HalfEdge()
    half_edge_2 = HalfEdge()
    half_edge_3 = HalfEdge()

    half_edge_1.opposite = init_half_edge
    init_half_edge.opposite = half_edge_1
    
    #Next edge is the one in ccw order around the incident vertex
    half_edge_1.next = half_edge_2
    half_edge_2.next = half_edge_3
    half_edge_3.next = half_edge_1
    
    #Prior edge is the one in cw order around the incident vertex
    half_edge_1.prior = half_edge_3
    half_edge_3.prior = half_edge_2
    half_edge_2.prior = half_edge_1

    #Set the colors of the half-edges
    color = btree.attr['color']
    half_edge_1.color = color
    half_edge_2.color = color
    half_edge_2.color = color


    #Construct the planar map on the children
    if btree.left_child != None:
        return construct_planar_map(btree.left_child, half_edge_2)
    if btree.right_child != None:
        return construct_planar_map(btree.right_child, half_edge_3)



#Performs bicolored partial closure on a binary tree. When possible build
#new edges in order to get faces with 4 edges
#Input: initial half-edge, an empty stack that will contain unpaired half-edges
#and the color of the initial node
def ___bicolored_partial_closure(init_half_edge):
    break_half_edge = init_half_edge
    #Travelse the tree in ccw order
    while True:
        current_half_edge = current_half_edge.next
        #Check if the incident vertex is a leaf
        if current_half_edge.opposite == None:
            #It is a leaf
            if len(stack) == 0:
                #We have to remember the first stem in order to break the loop
                break_half_edge = current_half_edge
            else:
                if current_half_edge == break_half_edge:
                    #We finished the closure
                    break
            #The edge has to be stored in our stack in order to find a opposite for it
            stack.append(current_half_edge)
        else:
            #It is a node and its opposite incident vertex must be of the opposite color
            current_half_edge = current_half_edge.opposite
            if len(stack) != 0:
                last_visited_steam = stack.pop()
                last_visited_steam.number_proximate_inner_edges += 1
                #If the steam is followed by three inner edges we can perform local closure
                if last_visited_steam.number_proximate_inner_edges == 3:
                    steam_opposite = HalfEdge()
                    
                    last_visited_steam.opposite = steam_opposite
                    steam_opposite.opposite = last_visited_steam
                    
                    #Set pointers of the new half-edge
                    steam_opposite.prior = current_half_edge
                    steam_opposite.next = current_half_edge.next
                    
                    #Update the pointer of the old edges
                    current_half_edge.next = steam_opposite
                    current_half_edge.next.prior = steam_opposite

                    stack.pop()
                    #Next half-edge to check is the one prior to our former stem
                    current_half_edge = last_visited_steam.prior
                        
    return break_half_edge



#Performs bicolored complete closure on a planar map of a binary tree in order to obtain
#a dissection of the hexagon with quadrangular faces
#input: init_half_edge is the half-edge that we get when we convert a binary tree into
#a planar map
def ___bicolored_complete_closure(init_half_edge):
    stack = []
    hexagon = [HalfEdge() for i in range(12)]
    __construct_hexagon(hexagon)

    starting_half_edge = ___bicolored_partial_closure(init_half_edge)

    #Now the stack contains all unpaired half-edges that have to be distributed
    #among the nodes of the hexagon
    #Connect the starting half-edge of our planar map with the first node of the hexagon
    new_half_edge = HalfEdge()
    starting_half_edge.opposite = new_half_edge
    new_half_edge.next = hexagon[0]
    hexagon[0].prior = new_half_edge
    hexagon[11].next = new_half_edge
    new_half_edge.prior = hexagon[11]

    #Now traverse the planar map. Depending on the distance between a new inner edge and
    #the next half-edge one can assign the new half edge to a certain hexagon node
    distance = 0
    hexagon_iter = 0
    current_half_edge = starting_half_edge
    while True:
        current_half_edge = current_half_edge.next

        if current_half_edge == starting_half_edge:
            #We are finished as we are back again at our starting half-edge
            break
        
        if current_half_edge == None:
            #We have a stem

            if distance > 2:
                print("ERROR: distance is greater than 2 -> local closure was possible!")
                break
            if distance == 0:
                #In order to get faces having 4 edges we have to assign this half-edge to the 
                #node 2 nodes further then our hexagon iterator is pointing now
                hexagon_iter += 4

            if distance == 1:
                #This half-edge has to be assigned to the node 1 node further
                hexagon_iter += 2

            #If distance is equal 2 then we have to stay at current hexagon node

            fresh_half_edge = HalfEdge()
            current_half_edge.opposite = fresh_half_edge
            fresh_half_edge.opposite = current_half_edge

            fresh_half_edge.next = hexagon[hexagon_iter-1]
            fresh_half_edge.prior = hexagon[hexagon_iter]
            hexagon[hexagon_iter-1].prior = fresh_half_edge
            hexagon[hexagon_iter].next = fresh_half_edge

        else:
            distance += 1

#Constructs a hexagon out of a list of half_edges
def __construct_hexagon(hexagon_half_edges):

    #Set opposite edges
    iter = 0
    while iter < 11:
        hexagon_half_edges[iter].opposite = hexagon_half_edges[iter+1]
        hexagon_half_edges[iter+1].opposite = hexagon_half_edges[iter]
        iter += 2

    #Set next and prior half-edges. Here prior and next are the same
    iter = 1
    while iter < 12:
        hexagon_half_edges[iter].next = hexagon_half_edges[iter+1]
        hexagon_half_edges[iter].prior = hexagon_half_edges[iter+1]
        hexagon_half_edges[iter+1].next = hexagon_half_edges[iter]
        hexagon_half_edges[iter+1].prior = hexagon_half_edges[iter]
        iter +=2