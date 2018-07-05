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

test_mode = True

class Closure:

    # Converts a binary tree into a planar map
    def ___btree_to_planar_map(self, btree):
        global test_mode
        init_half_edge = HalfEdge()
        self.___construct_planar_map(btree, init_half_edge)
        # Destroy the initial half-edge as it is only needed to construct its opposite
        init_half_edge.opposite.opposite = None

        return init_half_edge.opposite

    # Constructs planar map of the binary tree
    def ___construct_planar_map(self, btree, init_half_edge):
        half_edge_1 = HalfEdge()
        half_edge_2 = HalfEdge()
        half_edge_3 = HalfEdge()

        half_edge_1.opposite = init_half_edge
        init_half_edge.opposite = half_edge_1

        # Next edge is the one in ccw order around the incident vertex
        half_edge_1.next = half_edge_2
        half_edge_2.next = half_edge_3
        half_edge_3.next = half_edge_1
       
        # Prior edge is the one in cw order around the incident vertex
        half_edge_1.prior = half_edge_3
        half_edge_3.prior = half_edge_2
        half_edge_2.prior = half_edge_1

        # Set the colors of the half-edges
        color = btree.get_attribute('color')
        half_edge_1.color = color
        half_edge_2.color = color
        half_edge_3.color = color

        #Set the number of node the edges asre assigned to
        half_edge_1.node_nr = btree._id
        half_edge_2.node_nr = btree._id
        half_edge_3.node_nr = btree._id

        # Construct the planar map on the children
        if btree.left is not None:
            self.___construct_planar_map(btree.left, half_edge_2)
        if btree.right is not None:
            self.___construct_planar_map(btree.right, half_edge_3)
        return

    # Performs bicolored partial closure on a binary tree. When possible build
    # new edges in order to get faces of degree 4.
    def ___bicolored_partial_closure(self, init_half_edge):
        global test_mode
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

        return_edge = init_half_edge.get_min_half_edge()

        if test_mode:
            print("Partial closure list:")
            list_closure = init_half_edge.list_half_edges([])
            for i in list_closure:
                print(i)
                print("Partial closure returns the edge: {}".format(id(return_edge)))
            # Check partial closure
            self.___test_partial_closure(return_edge)

        return return_edge


    # Performs bicolored complete closure on a planar map of a binary tree in order to obtain
    # a dissection of the hexagon with quadrangular faces
    # input: init_half_edge is the half-edge that we get when we convert a binary tree into
    # a planar map
    def ___bicolored_complete_closure(self, init_half_edge):
        starting_half_edge = self.___bicolored_partial_closure(init_half_edge)

        # Construct hexagon
        hexagon = [HalfEdge() for i in range(12)]
        hexagon_start_half_edge = self.___construct_hexagon(hexagon, starting_half_edge)

        # Connect the starting half-edge of our planar map with the first node of the hexagon
        new_half_edge = HalfEdge()
        self.___add_new_half_edge(hexagon_start_half_edge, hexagon[11], starting_half_edge, new_half_edge, True)
        
        connecting_half_edge = new_half_edge

        print("Connecting hexagon and partal with: {}".format(new_half_edge))
        
        # Now traverse the planar map. Depending on the distance between a new inner edge and
        # the next half-edge one can assign the new half edge to a certain hexagon node
        distance = 0
        hexagon_iter = hexagon_start_half_edge
        current_half_edge = starting_half_edge
        hexagon_first_node = hexagon[0].node_nr
        hexagon_iter_index = 0
        # This variable is needed in order to check if we already visited more than one node of the hexagon
        visited_more = False
        while True:
            current_half_edge = current_half_edge.next

            if current_half_edge is starting_half_edge:
                break

            # If the opposite is None then we have to assign it to one of the hexagon nodes
            if current_half_edge.opposite is None:
                fresh_half_edge = HalfEdge()
                fresh_half_edge.opposite = current_half_edge
                current_half_edge.opposite = fresh_half_edge

                if distance == 0:
                    # Move 4 hexagon half-edges further
                    hexagon_iter_index = (hexagon.index(hexagon_iter) + 4) % 12
                    hexagon_iter = hexagon[hexagon_iter_index]
                elif distance == 1:
                    # Move 2 hexagon half-edges further
                    hexagon_iter_index = (hexagon.index(hexagon_iter) + 2) % 12
                    hexagon_iter = hexagon[hexagon_iter_index]
                else:
                    # Stay at current hexagon half-edge
                    pass

                assert(hexagon_iter_index < 13)

                if hexagon_iter.node_nr is not hexagon[0].node_nr:
                    visited_more = True
                
                if visited_more and id(hexagon_iter) == id(hexagon[0]):
                    last_added_edge = connecting_half_edge.next
                    self.___add_new_half_edge(connecting_half_edge, last_added_edge, current_half_edge, fresh_half_edge, True)
                else:
                    last_added_edge = hexagon_iter.next
                    self.___add_new_half_edge(hexagon_iter, last_added_edge, current_half_edge, fresh_half_edge, True)

                distance = 0
            else:
                current_half_edge = current_half_edge.opposite
                distance += 1

        if test_mode:
            print("Complete closure list:")
            list_closure = hexagon[0].list_half_edges([])
            for i in list_closure:
                print(i)
            print("Complete closure returns the edge: {}".format(id(hexagon[0])))

        return hexagon[0]

    # Adds the fresh half edge to the closure between the prior and the next half-edge
    def ___add_new_half_edge(self, prior_half_edge, next_half_edge, opposite_half_edge, new_half_edge, closure_edge):
        new_half_edge.opposite = opposite_half_edge
        opposite_half_edge.opposite = new_half_edge
        new_half_edge.color = prior_half_edge.color
        new_half_edge.node_nr = prior_half_edge.node_nr
        if closure_edge:
            new_half_edge.added_by_comp_clsr = True

        new_half_edge.prior = prior_half_edge
        prior_half_edge.next = new_half_edge
        new_half_edge.next = next_half_edge
        next_half_edge.prior = new_half_edge
        print("new half-edge: {}".format(new_half_edge))
    

    # Constructs a hexagon from a list of half_edges. 
    def ___construct_hexagon(self, hexagon_half_edges, partial_closure_edge):
        global test_mode
        inv_color = None
        color = partial_closure_edge.color
        if color is 'white':
            inv_color = 'black'
        else:
            inv_color = 'white'

        # Indicate that they belong to the hexagon
        for i in range(12):
            hexagon_half_edges[i].is_hexagonal = True

        # Set opposite edges
        iter = 0
        while iter < 11:
            hexagon_half_edges[iter].opposite = hexagon_half_edges[iter+1]
            hexagon_half_edges[iter+1].opposite = hexagon_half_edges[iter]
            iter += 2

        # Set next and prior half-edges. Here prior and next are the same
        iter = 1
        while iter < 12:
            hexagon_half_edges[iter].next = hexagon_half_edges[(iter+1)%12]
            hexagon_half_edges[iter].prior = hexagon_half_edges[(iter+1)%12]
            hexagon_half_edges[(iter+1)%12].next = hexagon_half_edges[iter]
            hexagon_half_edges[(iter+1)%12].prior = hexagon_half_edges[iter]
            iter += 2

        # Set node number.
        node_num = partial_closure_edge.get_max_node_nr().node_nr + 1
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
            # Then all even nodes have to have the inverse color
            even_color = inv_color
            odd_color = color
        else:
            even_color = color
            odd_color = inv_color

        # Set color
        for i in range(12):
            if hexagon_half_edges[i].node_nr % 2 == 0:
                hexagon_half_edges[i].color = even_color
            else:
                hexagon_half_edges[i].color = odd_color

        if test_mode:
            print("Hexagon list:")
            list_closure = hexagon_half_edges[0].list_half_edges([])
            for i in list_closure:
                print(i)
            # Return the starting half-edge
            print("Hexagon returns the edge: {}".format(id(hexagon_half_edges[0])))

        return hexagon_half_edges[0]



    # Makes the outer face of the irreducible dissection quadrangular by adding a new edge
    # between two opposite nodes of the hexagon
    # Look for faces with degree larger than 4 and quadrangulate them
    def ___quadrangulate(self, init_half_edge):
        # Add the outer edge
        new_half_edge = HalfEdge()
        new_half_edge.next = init_half_edge
        new_half_edge.prior = init_half_edge.prior
        init_half_edge.prior.next = new_half_edge 
        init_half_edge.prior = new_half_edge

        new_half_edge.node_nr = init_half_edge.node_nr
        new_half_edge.color = init_half_edge.color
        return_edge = new_half_edge

    
        # Iterate to the opposite node of the hexagon node 
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

        fresh_half_edge.node_nr = current_half_edge.node_nr
        fresh_half_edge.color = current_half_edge.color

        if return_edge.color is not 'black':
            return_edge = fresh_half_edge
        print("Quadrangulation returns the edge: {}".format(return_edge))
        return return_edge

  

    def closure_node_number(self, init_half_edge):
        G = init_half_edge.to_networkx_graph()
        closure_nodes = len(list(G.nodes))
        return closure_nodes
        

    # Checks if the planar map is correct.
    def test_planar_map(self, init_half_edge):
        edge_list = init_half_edge.list_half_edges( [])
        node_list = init_half_edge.get_node_list()

        print("List node dictonary")
        for node in node_list:
            print(node,end=" ")
            print(node_list[node])

        # Node list should has the same number of nodes as the
        # binary tree

        # Check if each edge is listed exactly once
        counter = 0
        for edge in edge_list:
            for ref in edge_list:
                if id(edge) == id(ref):
                    counter += 1
                    assert (counter == 1)

        # Check if every node has exactly three half-edges    
        for node in node_list:
            num_half_edges = len(node_list[node])
            assert (num_half_edges == 3)

    # Disable print
    def blockPrint(self):
        sys.stdout = open(os.devnull, 'w')

    # Enable print again
    def enablePrint(self):
        sys.stdout = sys.__stdout__

    # Checks if every half-edge occurs exactly once in the list
    def ___test_planar_map(self, init_half_edge):
        liste = self.list_half_edges(init_half_edge.opposite, [])

        for l in liste:
            count = 0
            for i in liste:
                if id(l) == id(i):
                    count += 1
                    if count > 1:
                        print(l)
                    assert (count < 2) 

        

    # Checks if there is any stem that has three full edges as successors
    def ___test_partial_closure(self, init_half_edge):
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
                        raise Exception("partial closure failed")
                    assert(count < 3)
                else:
                    break

        print("Partial closure is okay.")


    # Checks if quadrangulation is correct
    def ___test_quadrangulation(self, init_half_edge):
        # Check if every cycle is of degree 4
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
            
    # Check if the connections between the edges are correct
    def ___test_connections_between_half_edges(self, init_half_edge): 
        # edge_list = self.list_half_edges(init_half_edge, [])
        edge_list = init_half_edge.list_half_edges([])

        for edge in edge_list:
            assert (edge is edge.next.prior)
            assert (edge is edge.prior.next)
            assert (edge is edge.opposite.opposite)
            assert (edge.opposite is not None)

    # Checks if half edges at every node are planar
    def ___test_planarity_of_embedding(self, init_half_edge):
        edge_list = init_half_edge.list_half_edges([])

        # Check if there are two different edges that have the same prior/next half-edge
        for edge in edge_list:
            for i in edge_list:
                if id(i) != id(edge) and (i.prior is edge.prior or i.next is edge.next):
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
        global test_mode
        # Here you can switch to test mode
        test_mode = False

        if not test_mode:
            self.blockPrint()

        init_half_edge = self.___btree_to_planar_map(binary_tree)
        init_half_edge = self.___bicolored_complete_closure(init_half_edge)
        init_half_edge = self.___quadrangulate(init_half_edge)
        self.___test_connections_between_half_edges(init_half_edge)
        self.___test_planarity_of_embedding(init_half_edge)
        self.___test_quadrangulation(init_half_edge)

        if not test_mode:
            self.enablePrint()

        return init_half_edge
