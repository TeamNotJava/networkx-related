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

"""This class is needed for transformation of a Boltzmann sampler for bicolored binary trees
into a Boltzmann sampler for 3-connected planar graphs.
"""

import networkx as nx
import matplotlib.pyplot as plt
import sys
import os
from ..bijections.halfedge import HalfEdge
from ..combinatorial_classes import BinaryTree

class Closure:

    #Converts a binary tree into a planar map
    def ___btree_to_planar_map(self, btree):
        init_half_edge = HalfEdge()
        self.___construct_planar_map(btree, init_half_edge)
        #Destroy the initial half-edge as it is only needed to construct its opposite
        init_half_edge.opposite.opposite = None
        return init_half_edge.opposite

    # Constructs planar map of the binary tree
    def ___construct_planar_map(self, btree, init_half_edge):
        half_edge_1 = HalfEdge()
        half_edge_2 = HalfEdge()
        half_edge_3 = HalfEdge()

        half_edge_1.opposite = init_half_edge
        init_half_edge.opposite = half_edge_1

        if init_half_edge.index == -1:
            half_edge_index = 0
        else:
            #half_edge_index = self.___get_max_half_edge_index(init_half_edge) + 1
            half_edge_index = init_half_edge.get_max_half_edge_index() + 1

        #Set the indices of the half-edges
        half_edge_1.index = half_edge_index 
        half_edge_2.index = half_edge_index + 1
        half_edge_3.index = half_edge_index + 2

        #Next edge is the one in ccw order around the incident vertex
        half_edge_1.next = half_edge_2
        half_edge_2.next = half_edge_3
        half_edge_3.next = half_edge_1
       
        #Prior edge is the one in cw order around the incident vertex
        half_edge_1.prior = half_edge_3
        half_edge_3.prior = half_edge_2
        half_edge_2.prior = half_edge_1

        #Set the colors of the half-edges
        color = btree.get_attribute('color')
        half_edge_1.color = color
        half_edge_2.color = color
        half_edge_3.color = color

        #Set the number of node the edges asre assigned to
        half_edge_1.node_nr = btree._id
        half_edge_2.node_nr = btree._id
        half_edge_3.node_nr = btree._id

        #Construct the planar map on the children
        if btree.left is not None:
            self.___construct_planar_map(btree.left, half_edge_2)
        if btree.right is not None:
            self.___construct_planar_map(btree.right, half_edge_3)
        return

    #Performs bicolored partial closure on a binary tree. When possible build
    #new edges in order to get faces of degree 4.
    def ___bicolored_partial_closure(self, init_half_edge):
        print("PARTIAL CLOSURE")
        stack = []
        stack.append(init_half_edge)
        break_edge = init_half_edge
        current_half_edge = init_half_edge

        while True:
            print(current_half_edge)
            current_half_edge = current_half_edge.next

            if current_half_edge.opposite is None:
                if len(stack) == 0:
                    break_edge = current_half_edge
                if current_half_edge is break_edge and len(stack) > 0:
                    break
                stack.append(current_half_edge)
            else:
                current_half_edge = current_half_edge.opposite
                if len(stack) > 0:
                    top_half_edge = stack.pop()
                    print("Pop edge: ",format(top_half_edge))
                    top_half_edge.number_proximate_inner_edges += 1

                    if top_half_edge.number_proximate_inner_edges == 3:
                        new_half_edge = HalfEdge()
                        #new_half_edge.index = self.___get_max_half_edge_index(init_half_edge) + 1
                        new_half_edge.index = init_half_edge.get_max_half_edge_index() + 1
                        new_half_edge.node_nr = current_half_edge.node_nr
                        new_half_edge.color = current_half_edge.color

                        top_half_edge.opposite = new_half_edge
                        new_half_edge.opposite = top_half_edge

                        new_half_edge.next = current_half_edge.next
                        new_half_edge.prior = current_half_edge
                        current_half_edge.next.prior = new_half_edge
                        current_half_edge.next = new_half_edge

                        current_half_edge = top_half_edge.prior
                        print("New half edge: {}",format(new_half_edge))
                        print("Look next at: {}",format(current_half_edge))

                    else:
                        stack.append(top_half_edge)

        print("Partial closure list:")
        #list_closure = self.list_half_edges(init_half_edge, [])
        list_closure = init_half_edge.list_half_edges([])
        for i in list_closure:
            print(i)
        #return_edge = self.___return_smallest_half_edge(init_half_edge)
        return_edge = init_half_edge.get_min_half_edge()
        print("Partial closure returns the edge: {}".format(return_edge.index))

        #Check partial closure
        self.___test_partial_closure(return_edge)
        return return_edge



    #Performs bicolored complete closure on a planar map of a binary tree in order to obtain
    #a dissection of the hexagon with quadrangular faces
    #input: init_half_edge is the half-edge that we get when we convert a binary tree into
    #a planar map
    def ___bicolored_complete_closure(self, init_half_edge):
        print("BICOLORED COMPLETE CLOSURE")
        hexagon_nodes_visited = 0
        starting_half_edge = self.___bicolored_partial_closure(init_half_edge)

        hexagon = [HalfEdge() for i in range(12)]
        #index = self.___get_max_half_edge_index(starting_half_edge) + 1
        index = starting_half_edge.get_max_half_edge_index() + 1
        hexagon_start_half_edge = self.___construct_hexagon(hexagon, starting_half_edge, index)

        #Connect the starting half-edge of our planar map with the first node of the hexagon
        #index = self.___get_max_half_edge_index(hexagon_start_half_edge) + 1
        index = hexagon_start_half_edge.get_max_half_edge_index() + 1
        new_half_edge = HalfEdge()
        #prior_half_edge, next_half_edge, opposite_half_edge, fresh_half_edge, index
        self.___add_new_half_edge(hexagon_start_half_edge, hexagon[11], starting_half_edge, new_half_edge, index, True)

        index = index + 1
        
        connecting_half_edge = new_half_edge

        print("Connecting hexagon and partal with: {}".format(new_half_edge))
        
        #Now traverse the planar map. Depending on the distance between a new inner edge and
        #the next half-edge one can assign the new half edge to a certain hexagon node
        distance = 0
        hexagon_iter = hexagon_start_half_edge
        current_half_edge = starting_half_edge
        first_time = True
        hexagon_first_node = hexagon[0].node_nr
        while True:
            current_half_edge = current_half_edge.next
            if current_half_edge is starting_half_edge:
                break
            if current_half_edge.opposite is None:
                fresh_half_edge = HalfEdge()
                fresh_half_edge.opposite = current_half_edge
                current_half_edge.opposite = fresh_half_edge

                if distance == 0:
                    #Move 4 hexagon half-edges further
                    pos = (hexagon_iter.index - hexagon_start_half_edge.index + 4) % 12
                    if hexagon_iter.index - hexagon_start_half_edge.index + 4 >= 13:
                        print("Current half-edge:",end=" ")
                        print(current_half_edge)
                        print("Hexagon iter:",end=" ")
                        print(hexagon_iter)
                    assert (hexagon_iter.index - hexagon_start_half_edge.index + 4 < 13)
                    hexagon_iter = hexagon[pos]
                elif distance == 1:
                    #Move 2 hexagon half-edges further
                    pos = (hexagon_iter.index - hexagon_start_half_edge.index + 2) % 12
                    if hexagon_iter.index - hexagon_start_half_edge.index + 4 >= 13:
                        print("Current half-edge:",end=" ")
                        print(current_half_edge)
                        print("Hexagon iter:",end=" ")
                        print(hexagon_iter)
                    assert (hexagon_iter.index - hexagon_start_half_edge.index + 2 < 13)
                    hexagon_iter = hexagon[pos]
                else:
                    #Stay at current hexagon half-edge
                    pass

                if hexagon_nodes_visited > 0 and hexagon_iter.node_nr == hexagon[0].node_nr:
                    hexagon_nodes_visited = 6
                else:
                    hexagon_nodes_visited = hexagon_iter.node_nr - hexagon_first_node   

                if hexagon_nodes_visited == 6:
                    last_added_edge = connecting_half_edge.next
                    self.___add_new_half_edge(connecting_half_edge, last_added_edge, current_half_edge, fresh_half_edge, index, True)
                else:
                    last_added_edge = hexagon_iter.next
                    self.___add_new_half_edge(hexagon_iter, last_added_edge, current_half_edge, fresh_half_edge, index, True)

                index += 1
                distance = 0
            else:
                current_half_edge = current_half_edge.opposite
                distance += 1

        print("Complete closure list:")
        #list_closure = self.list_half_edges(hexagon[0], [])
        list_closure = hexagon[0].list_half_edges([])
        for i in list_closure:
            print(i)
        print("Complete closure returns the edge: {}".format(hexagon[0].index))
        return hexagon[0]

                
    #Adds the fresh half edge to the closure between the prior and the next half-edge
    def ___add_new_half_edge(self, prior_half_edge, next_half_edge, opposite_half_edge, new_half_edge, index, closure_edge):
        new_half_edge.opposite = opposite_half_edge
        opposite_half_edge.opposite = new_half_edge
        new_half_edge.color = prior_half_edge.color
        new_half_edge.node_nr = prior_half_edge.node_nr
        new_half_edge.index = index
        if closure_edge:
            new_half_edge.added_by_comp_clsr = True

        new_half_edge.prior = prior_half_edge
        prior_half_edge.next = new_half_edge
        new_half_edge.next = next_half_edge
        next_half_edge.prior = new_half_edge
        print("new half-edge: {}".format(new_half_edge))
        


    # #Returns the smalles half-edge in the graph
    # def ___return_smallest_half_edge(self, init_half_edge):
    #     half_edge_list = self.list_half_edges(init_half_edge, [])
    #     min_half_edge = None 

    #     for edge in half_edge_list:
    #         if min_half_edge is None and edge.opposite is None:
    #             min_half_edge = edge
    #         elif min_half_edge is not None and edge.opposite is None and edge.index < min_half_edge.index:
    #             min_half_edge = edge 

    #     return min_half_edge



    #Constructs a hexagon from a list of half_edges. 
    def ___construct_hexagon(self, hexagon_half_edges, partial_closure_edge, index):
        inv_color = None
        color = partial_closure_edge.color
        if color is 'white':
            inv_color = 'black'
        else:
            inv_color = 'white'


        #Indicate that they belong to the hexagon
        for i in range(12):
            hexagon_half_edges[i].is_hexagonal = True

        #Set opposite edges
        iter = 0
        while iter < 11:
            hexagon_half_edges[iter].opposite = hexagon_half_edges[iter+1]
            hexagon_half_edges[iter+1].opposite = hexagon_half_edges[iter]
            iter += 2

        #Set next and prior half-edges. Here prior and next are the same
        iter = 1
        while iter < 12:
            hexagon_half_edges[iter].next = hexagon_half_edges[(iter+1)%12]
            hexagon_half_edges[iter].prior = hexagon_half_edges[(iter+1)%12]
            hexagon_half_edges[(iter+1)%12].next = hexagon_half_edges[iter]
            hexagon_half_edges[(iter+1)%12].prior = hexagon_half_edges[iter]
            iter += 2

        #Set node number.
        #node_num = self.___get_max_node_nr(partial_closure_edge) + 1
        node_num = partial_closure_edge.get_max_node_nr() + 1
        current_half_edge = hexagon_half_edges[11]
        while True:
            current_half_edge.node_nr = node_num
            current_half_edge.next.node_nr = node_num
            current_half_edge = current_half_edge.next.opposite
            node_num += 1
            if current_half_edge is hexagon_half_edges[11]:
                break

        even_color = None
        odd_color = None
        if hexagon_half_edges[0].node_nr % 2 == 0:
            #Then all even nodes have to have the inverse color
            even_color = inv_color
            odd_color = color
        else:
            even_color = color
            odd_color = inv_color

        #Set color
        for i in range(12):
            if hexagon_half_edges[i].node_nr % 2 == 0:
                hexagon_half_edges[i].color = even_color
            else:
                hexagon_half_edges[i].color = odd_color


        #Set indeces for half-edges
        current_half_edge = hexagon_half_edges[0]
        while True:
            current_half_edge.index = index
            current_half_edge.opposite.index = index + 1
            current_half_edge = current_half_edge.opposite.next
            index += 2
            if current_half_edge is hexagon_half_edges[0]:
                break

        print("Hexagon list:")
        #list_closure = self.list_half_edges(hexagon_half_edges[0], [])
        list_closure = hexagon_half_edges[0].list_half_edges([])
        for i in list_closure:
            print(i)


        #Return the starting half-edge
        print("Hexagon returns the edge: {}".format(hexagon_half_edges[0].index))
        return hexagon_half_edges[0]


    #Makes the outer face of the irreducible dissection quadrangular by adding a new edge
    #between two opposite nodes of the hexagon
    #Look for faces with degree larger than 4 and quadrangulate them
    def ___quadrangulate(self, init_half_edge):
        #Add the outer edge
        new_half_edge = HalfEdge()
        new_half_edge.next = init_half_edge
        new_half_edge.prior = init_half_edge.prior
        init_half_edge.prior.next = new_half_edge 
        init_half_edge.prior = new_half_edge
        #index = self.___get_max_half_edge_index(init_half_edge) + 1
        index = init_half_edge.get_max_half_edge_index() + 1
        new_half_edge.index = index
        index += 1
        new_half_edge.node_nr = init_half_edge.node_nr
        new_half_edge.color = init_half_edge.color
        return_edge = new_half_edge

    
        #Iterate to the opposite node of the hexagon node 
        count = 0
        current_half_edge = new_half_edge
        while True:
            current_half_edge = current_half_edge.prior.opposite
            count += 1
            if count == 3:
                break

        fresh_half_edge = HalfEdge()
        fresh_half_edge.opposite = new_half_edge
        new_half_edge.opposite = fresh_half_edge

        fresh_half_edge.prior = current_half_edge.prior
        fresh_half_edge.next = current_half_edge
        current_half_edge.prior.next = fresh_half_edge
        current_half_edge.prior = fresh_half_edge

        fresh_half_edge.index = index 
        fresh_half_edge.node_nr = current_half_edge.node_nr
        fresh_half_edge.color = current_half_edge.color

        if return_edge.color is not 'black':
            return_edge = fresh_half_edge
        print("Quadrangulation returns the edge: {}".format(return_edge))
        return return_edge

    #Quadrangulates inner faces
    def ___quadrangulate_inner_faces(self, init_half_edge):
        print("QUADRANGULATE INNER FACES")
        #Look for faces with degree higher than 4
        edge_list = self.list_half_edges(init_half_edge, [])

        for half_edge in edge_list:
            edges_to_remove = []
            current_half_edge = half_edge.next
            print("Check: ",format(current_half_edge))
            cycle_degree = 0
            edges_to_remove.append(half_edge)
            edges_to_remove.append(current_half_edge)
            while True:
                current_half_edge = current_half_edge.opposite
                if current_half_edge not in edges_to_remove:
                    edges_to_remove.append(current_half_edge)
                cycle_degree += 1
                if current_half_edge is half_edge:
                    if cycle_degree != 4:
                        #Check if it is possible to quadrangulate
                        if cycle_degree < 4:
                            raise Exception("Face degree too small.")

                        num_edges_to_add = int(cycle_degree/3)
                        check_number = cycle_degree + num_edges_to_add - (num_edges_to_add * 4 - num_edges_to_add)
                        if check_number != 4:
                            print("cycle degree: ", format(cycle_degree))
                            raise Exception("Cannot quadrangulate an inner face!")
                        #Quadrangulate
                        current_half_edge = half_edge
                        #Add an edge after three edges                  
                        #Go three edges further 
                        current_half_edge = current_half_edge.next          
                        for j in range(3):
                            current_half_edge = current_half_edge.opposite
                            current_half_edge = current_half_edge.next
                        #Add new edge between "current_half_edge" and "half_edge"
                        self.___add_new_edge(current_half_edge, half_edge)
                        #Add an edge after two edges
                        for i in range(num_edges_to_add - 1):
                            #Go two edges further           
                            for j in range(2):
                                current_half_edge = current_half_edge.opposite
                                current_half_edge = current_half_edge.next
                            #Add new edge between "current_half_edge" and "half_edge"
                            self.___add_new_edge(current_half_edge, half_edge)
                        #Remove the edges form the edge list
                        for rm_edge in edges_to_remove:
                            edge_list.remove(rm_edge)
                    else:
                        break
                else:
                    current_half_edge = current_half_edge.next
                    if current_half_edge not in edges_to_remove:  
                        edges_to_remove.append(current_half_edge)      
                        

    # def ___add_new_edge(self, left_half_edge, right_half_edge):
    #     new_half_edge_1 = HalfEdge()
    #     new_half_edge_2 = HalfEdge()
    #     index = self.___get_max_half_edge_index(left_half_edge) + 1

    #     new_half_edge_1.opposite = new_half_edge_2
    #     new_half_edge_2.opposite = new_half_edge_1

    #     #Setup the first new half edge
    #     new_half_edge_1.color = left_half_edge.color
    #     new_half_edge_1.node_nr = left_half_edge.node_nr
    #     new_half_edge_1.index = index
    #     new_half_edge_1.next = left_half_edge.next
    #     new_half_edge_1.prior = left_half_edge
    #     left_half_edge.next.prior = new_half_edge_1
    #     left_half_edge.next = new_half_edge_1

    #     #Setup the second new half edge
    #     new_half_edge_2.color = right_half_edge.color
    #     new_half_edge_2.node_nr = right_half_edge.node_nr
    #     new_half_edge_2.index = index
    #     new_half_edge_2.next = right_half_edge.next
    #     new_half_edge_2.prior = right_half_edge
    #     right_half_edge.next.prior = new_half_edge_2
    #     right_half_edge.next = new_half_edge_2


    # #Returns a list with half-edges
    # def list_half_edges(self, init_half_edge, edge_list):       
    #     edge_list.append(init_half_edge)
    #     current_half_edge = init_half_edge
    #     assert (current_half_edge is not None)
    #     while True:
    #         if current_half_edge.next is not None:
    #             current_half_edge = current_half_edge.next
    #             if current_half_edge is not init_half_edge and current_half_edge not in edge_list:
    #                 edge_list.append(current_half_edge)
    #                 if current_half_edge.opposite is not None:
    #                     if current_half_edge.opposite not in edge_list:
    #                         self.list_half_edges(current_half_edge.opposite, edge_list)
    #             else:
    #                 break
    #         else:
    #             break
    #     return edge_list



    # #Transforms a list of planar map half-edged into a networkx graph
    # def half_edges_to_graph(self, init_half_edge):
    #     half_edge_list = self.list_half_edges(init_half_edge, [])

    #     #Remove all unpaired half-edges
    #     half_edge_list = [x for x in half_edge_list if not x.opposite is None]
    #     G = nx.Graph()
    #     while len(half_edge_list) > 0:
    #         half_edge = half_edge_list.pop()
    #         G.add_edge(half_edge.node_nr, half_edge.opposite.node_nr)
    #         G.nodes[half_edge.node_nr]['color'] = half_edge.color
    #         half_edge_list.remove(half_edge.opposite)
    #     return G

    def closure_node_number(self, init_half_edge):
        #G = self.half_edges_to_graph(init_half_edge)
        G = init_half_edge.to_networkx_graph()
        closure_nodes = len(list(G.nodes))
        return closure_nodes
        


    # #Returns the highest index of the current graph
    # def ___get_max_half_edge_index(self, init_half_edge):    
    #     assert (init_half_edge is not None)    
    #     edge_list = self.list_half_edges(init_half_edge, [])
    #     max_index = 0
    #     for x in edge_list:
    #         if x.index > max_index:
    #             max_index = x.index
    #     return max_index


    # #Returns the highest node number of the current graph
    # def ___get_max_node_nr(self, init_half_edge):
    #     edge_list = self.list_half_edges(init_half_edge, [])
    #     max_node = 0
    #     for x in edge_list:
    #         if x.node_nr > max_node:
    #             max_node = x.node_nr
    #     return max_node

    # Checks if the planar map is correct.
    def check_planar_map(self, init_half_edge, current_half_edge):
        edge_list = self.list_half_edges(init_half_edge, [])

        #Check if each edge is listed exactly once
        counter = 0
        for edge in edge_list:
            if edge.index == current_half_edge.index:
                counter = counter + 1
                assert (counter == 1)

    # Disable print
    def blockPrint(self):
        sys.stdout = open(os.devnull, 'w')

    # Enable print again
    def enablePrint(self):
        sys.stdout = sys.__stdout__

    #Checks if every half-edge occurs exactly once in the list
    def ___test_planar_map(self, init_half_edge):
        liste = self.list_half_edges(init_half_edge.opposite, [])

        for l in liste:
            count = 0
            for i in liste:
                if l.index == i.index:
                    count += 1
                    if count > 1:
                        print(l)
                    assert (count < 2) 

        

    # Checks if there is any stem that has three full edges as successors
    def ___test_partial_closure(self, init_half_edge):
        #edge_list = self.list_half_edges(init_half_edge, [])
        edge_list = init_half_edge.list_half_edges([])
        stem_list = []

        for edge in edge_list:
            if edge.opposite is None:
                stem_list.append(edge)

        # Check for each stem if it has at most two full edges as successors
        for stem in stem_list:
            count = 0
            current_half_edge = stem
            while True:
                current_half_edge = current_half_edge.next
                if current_half_edge is stem:
                    break
                if current_half_edge.opposite is not None:
                    current_half_edge = current_half_edge.opposite
                    print("current: ",format(current_half_edge))
                    count = count + 1            
                    if count > 2:
                        print("ERROR: partial closure failed at: ", format(stem))
                    assert(count < 3)
                else:
                    break

        print("Partial closure is okay.")


    #Checks if quadrangulation is correct
    def ___test_quadrangulation(self, init_half_edge):
        #Check if every cycle is of degree 4
        #edge_list = self.list_half_edges(init_half_edge, [])
        edge_list = init_half_edge.list_half_edges([])

        for half_edge in edge_list:
            current_half_edge = half_edge
            print("Check: ",format(current_half_edge))
            cycle_degree = 0
            while True:
                current_half_edge = current_half_edge.next
                print(current_half_edge)
                cycle_degree += 1
                print("Cycle degree: ",format(cycle_degree))
                assert (current_half_edge.opposite is not None)
                if current_half_edge is half_edge:
                    break
                assert(cycle_degree < 5)
                current_half_edge = current_half_edge.opposite
                if current_half_edge is half_edge:
                    break
                print(current_half_edge)
        print("Quadrangulation is okay")
            
    #Check if the connections between the edges are correct
    def ___test_connections_between_half_edges(self, init_half_edge): 
        #edge_list = self.list_half_edges(init_half_edge, [])
        edge_list = init_half_edge.list_half_edges([])

        for edge in edge_list:
            assert (edge is edge.next.prior)
            assert (edge is edge.prior.next)
            assert (edge is edge.opposite.opposite)

    #Checks if half edges at every node are planar
    def ___test_planarity_of_embedding(self, init_half_edge):
        #edge_list = self.list_half_edges(init_half_edge, [])
        edge_list = init_half_edge.list_half_edges([])

        #Check if there are two different edges that have the same prior/next half-edge
        for edge in edge_list:
            for i in edge_list:
                if i.index != edge.index and (i.prior is edge.prior or i.next is edge.next):
                    raise Exception("There are two different edges with the samp prior/next.")


    def closure(self, binary_tree):
        """This function implements the bijection between the binary trees
        and the irreducible dissections. It first perfomrs the
        partial closure by adding a new edge to three inner edges of the
        binary tree (every face in the binary tree has now four edges).
        Afterwards, the complete closure is performed, where the partialy
        closed binary tree is integrated into a hexagon (dissection of hexagon).
        The last step is to make the outer face of the graph to a four-edge
        face (quadrangulation of the hexagon).
        """
        self.blockPrint()
        init_half_edge = self.___btree_to_planar_map(binary_tree)
        init_half_edge = self.___bicolored_complete_closure(init_half_edge)
        init_half_edge = self.___quadrangulate(init_half_edge)
        self.___test_connections_between_half_edges(init_half_edge)
        self.___test_planarity_of_embedding(init_half_edge)
        self.___test_quadrangulation(init_half_edge)
        self.enablePrint()
        return init_half_edge
