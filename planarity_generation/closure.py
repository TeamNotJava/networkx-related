#This is needed for transformation of a Boltzmann sampler for bicolored binary trees
# into a Boltzmann sampler for 3-connected planar graphs.


##################################################################
#  THIS IS BASED ON THE PAPER "DISSECTIONS AND TREES, WITH WITH  #
#  APPLICATIONS TO OPTIMAL MESH ENCODING AND TO RANDOM SAMPLING" #
##################################################################

from binary_tree_v2 import BinaryTree


class Halfedge:

    opposite = None
    next = None
    prior = None
    number_proximate_inner_edges = 0


#Convert a binary tree int o planar map
def btree_to_planar_map(btree):
    init_half_edge = Halfedge()
    construct_planar_map(btree, init_half_edge)
    #Destroy the initial half-edge as it is only needed to construct its opposite
    init_half_edge.opposite.opposite = None
    return init_half_edge.opposite



#Consturct planer map out of a binary tree, i.e., make the binary tree
#tri-oriented
def construct_planar_map(btree, init_half_edge):
    half_edge_1 = Halfedge()
    half_edge_2 = Halfedge()
    half_edge_3 = Halfedge()

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

    #Construct the planar map on the children
    if btree.left_child != None:
        return construct_planar_map(btree.left_child, half_edge_2)
    if btree.right_child != None:
        return construct_planar_map(btree.right_child, half_edge_3)



#Performs bicolored partial closure on a binary tree. When possible build
#new edges in order to get faces with 4 edges
#Input: initial half-edge and a list that is used as a stack
def bicolored_partial_closure(init_half_edge, stack, origin_is_black):
    origin_of_current_half_edge = origin_is_black
    break_half_edge = init_half_edge
    #Travelse the tree ccw
    while True:
        current_half_edge = init_half_edge.next
        #Check if the incident vertex is a leaf
        if current_half_edge.next == None:
            #It is a leaf
            if len(stack) == 0:
                #We have to remember the half-edge in order to break the loop
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
            origin_of_current_half_edge = not origin_of_current_half_edge
            if len(stack) != 0:
                last_visited_steam = stack.pop()
                last_visited_steam.number_proximate_inner_edges += 1
                #If the steam is followed by three inner edges we can perform local closure
                if last_visited_steam.number_proximate_inner_edges == 3:
                    steam_opposite = Halfedge()
                    
                    last_visited_steam.opposite = steam_opposite
                    steam_opposite.opposite = last_visited_steam
                    
                    #Set pointers of the new half-edge
                    steam_opposite.prior = current_half_edge
                    steam_opposite.next = current_half_edge.next
                    
                    #Update the pointer of the old edges
                    current_half_edge.next = steam_opposite
                    current_half_edge.next.prior = steam_opposite

                    stack.pop()
                    current_half_edge = last_visited_steam.prior
                    origin_of_current_half_edge = not origin_of_current_half_edge
                        
    return origin_of_current_half_edge


#Performs bicolored complete closure on a planar map of a binary tree in order to obtain
#a dissection of the hexagon with quadrangular faces
def bicolored_complete_closure(init_half_edge, stack, origin_is_black):
    stack = []
    


