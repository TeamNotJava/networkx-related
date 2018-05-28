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
from framework.bijections.halfedge import HalfEdge
from framework.binary_tree_decomposition import BinaryTree
import numpy as np
import matplotlib.pyplot as plt

class Closure:

    #Convert a binary tree int o planar map
    def ___btree_to_planar_map(self, btree):
        init_half_edge = HalfEdge()
        self.___construct_planar_map(btree, init_half_edge, 0, 0)
        #Destroy the initial half-edge as it is only needed to construct its opposite
        init_half_edge.opposite.opposite = None
        print("btree to planar return: ")
        print(init_half_edge.opposite)
        return init_half_edge.opposite



    #Consturct planer map out of a binary tree, i.e., make the binary tree
    #tri-oriented
    def ___construct_planar_map(self, btree, init_half_edge, node_nr, half_edge_index):
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
        color = btree.get_attribute('color')
        if color == "white":
            color = 1
        else:
            color = 0
        half_edge_1.color = color
        half_edge_2.color = color
        half_edge_2.color = color

        #Set the number of node the edges asre assigned to
        half_edge_1.node_nr = node_nr
        half_edge_2.node_nr = node_nr
        half_edge_3.node_nr = node_nr

        #Set the indices of the half-edges
        half_edge_1.index = half_edge_index 
        half_edge_2.index = half_edge_index + 1
        half_edge_3.index = half_edge_index + 2

        #Construct the planar map on the children
        if btree.left() != None:
            return self.___construct_planar_map(btree.left(), half_edge_2, node_nr+1, half_edge_index+3)
        if btree.right() != None:
            return self.___construct_planar_map(btree.right(), half_edge_3, node_nr+1, half_edge_index+3)



    # #Performs bicolored partial closure on a binary tree. When possible build
    # #new edges in order to get faces with 4 edges
    # def ___bicolored_partial_closure(self, init_half_edge):
    def ___bicolored_partial_closure(self, init_half_edge):
        stack = []
        stack.append(init_half_edge)
        break_edge = init_half_edge
        current_half_edge = init_half_edge

        while True:
            current_half_edge = current_half_edge.next

            if current_half_edge.opposite == None:
                if len(stack) == 0:
                    break_edge = current_half_edge
                if current_half_edge == break_edge:
                    break
                stack.append(current_half_edge)
            else:
                current_half_edge = current_half_edge.opposite
                if len(stack) > 0:
                    top_half_edge = stack.pop()
                    top_half_edge.number_proximate_inner_edges += 1

                    if top_half_edge.number_proximate_inner_edges == 3:
                        new_half_edge = HalfEdge()
                        new_half_edge.index = self.___get_max_half_edge_index(init_half_edge) + 1
                        new_half_edge.node_nr = current_half_edge.node_nr
                        new_half_edge.color = current_half_edge.color

                        top_half_edge.opposite = new_half_edge
                        new_half_edge.opposite = top_half_edge

                        new_half_edge.next = current_half_edge.next
                        new_half_edge.prior = current_half_edge
                        current_half_edge.next.prior = new_half_edge
                        current_half_edge.next = new_half_edge

                        current_half_edge = top_half_edge.prior
                    else:
                        stack.append(top_half_edge)

        # print("Partial closure list:")
        # list_closure = self.list_half_edges(init_half_edge, [])
        # for i in list_closure:
        #     print(i)
        return init_half_edge



    #Performs bicolored complete closure on a planar map of a binary tree in order to obtain
    #a dissection of the hexagon with quadrangular faces
    #input: init_half_edge is the half-edge that we get when we convert a binary tree into
    #a planar map
    def ___bicolored_complete_closure(self, init_half_edge):
        #For each node of the hexagon save the half-edge order
        stack = [[] for i in range(6)]
        starting_half_edge = self.___bicolored_partial_closure(init_half_edge)
        # print("Partial closure list:")
        # list_partial = self.list_half_edges(init_half_edge, [])
        # for i in list_partial:
        #     print(i)

        hexagon = [HalfEdge() for i in range(12)]
        index = self.___get_max_half_edge_index(starting_half_edge) + 1
        hexagon_start_half_edge = self.___construct_hexagon(hexagon, starting_half_edge, index)
        # print("Hexagon list:")
        # list_hexagon = self.list_half_edges(hexagon_start_half_edge, [])
        # for i in list_hexagon:
        #     print(i)

        #Init stack
        current_half_edge = hexagon_start_half_edge
        while True:
            current_node = current_half_edge.node_nr - hexagon[0].node_nr
            # print("Current node:",end=" ")
            # print(current_node)         
            stack[current_node].insert(0, current_half_edge)
            stack[current_node].insert(1, current_half_edge.next)
            current_half_edge = current_half_edge.opposite.next
            if current_half_edge == hexagon_start_half_edge:
                break

        #Connect the starting half-edge of our planar map with the first node of the hexagon
        new_half_edge = HalfEdge()
        starting_half_edge.opposite = new_half_edge
        new_half_edge.opposite = starting_half_edge
        new_half_edge.prior = hexagon_start_half_edge
        new_half_edge.next = hexagon[11]        
        hexagon_start_half_edge.next = new_half_edge
        hexagon[11].prior = new_half_edge
        
        index = self.___get_max_half_edge_index(hexagon_start_half_edge) + 1
        new_half_edge.index = index
        new_half_edge.node_nr = hexagon[11].node_nr
        new_half_edge.color = hexagon[11].color
        index = index + 1

        stack[0].insert(1, new_half_edge)
        # print("Stack: ")
        # for s in stack:
        #     print(s)

        # print("Connecting hexagon and partial with: ",end=" ")
        # print(new_half_edge)

        #Now traverse the planar map. Depending on the distance between a new inner edge and
        #the next half-edge one can assign the new half edge to a certain hexagon node
        distance = 0
        hexagon_iter = 0
        current_half_edge = starting_half_edge
        while True:
            current_half_edge = current_half_edge.next 
            if current_half_edge == starting_half_edge:
                break
            if current_half_edge.opposite == None:
                fresh_half_edge = HalfEdge()
                fresh_half_edge.opposite = current_half_edge
                current_half_edge.opposite = fresh_half_edge

                if distance == 0:
                    # print("Distance 0")
                    hexagon_iter += 3
                    connected_edges = stack[hexagon[hexagon_iter].node_nr - hexagon[0].node_nr]
                elif distance == 1:
                    # print("Distance 1")
                    hexagon_iter += 1
                    connected_edges = stack[hexagon[hexagon_iter].node_nr - hexagon[0].node_nr]             
                else: 
                    # print("Distance 2")
                    connected_edges = stack[hexagon[hexagon_iter].node_nr - hexagon[0].node_nr]

                if connected_edges[0].index == hexagon[hexagon_iter].index:
                    #We can insert the new edge between the left hexagon edge and the last inserted edge
                    fresh_half_edge.next = connected_edges[1]
                    fresh_half_edge.prior = hexagon[hexagon_iter]
                    hexagon[hexagon_iter].next = fresh_half_edge
                    connected_edges[1].prior = fresh_half_edge
                    fresh_half_edge.index = index
                    fresh_half_edge.node_nr = hexagon[hexagon_iter].node_nr
                    fresh_half_edge.color = hexagon[hexagon_iter].color
                    #Update stack
                    connected_edges.insert(1, fresh_half_edge)
                    # print("At stack number:",end=" ")
                    # print(hexagon[hexagon_iter].node_nr - hexagon[0].node_nr)

                else:
                    #We can insert the new edge between the right hexagon edge and the first inserted edge
                    pos = len(connected_edges) - 1 
                    fresh_half_edge.next = connected_edges[pos]
                    fresh_half_edge.prior = connected_edges[pos-1]
                    connected_edges[pos].prior = fresh_half_edge
                    connected_edges[pos-1].next = fresh_half_edge
                    fresh_half_edge.index = index
                    fresh_half_edge.node_nr = connected_edges[pos].node_nr
                    fresh_half_edge.color = connected_edges[pos].color
                    #Update stack
                    connected_edges.insert(pos, fresh_half_edge)
                    # print("At stack number:",end=" ")
                    # print(hexagon[hexagon_iter].node_nr - hexagon[0].node_nr)

                # print("adding fresh edge:", end=" ")
                # print(fresh_half_edge)
                # print("Stack: ")
                # for s in stack:
                #     print(s)

                if distance == 0 or distance == 1:
                    hexagon_iter += 1

                index += 1
                distance = 0
            else:
                current_half_edge = current_half_edge.opposite
                distance += 1

        # print("Complete closure list:")
        # list_closure = self.list_half_edges(hexagon[0], [])
        # for i in list_closure:
        #     print(i)
        return hexagon[0]

        


    #Constructs a hexagon from a list of half_edges. 
    def ___construct_hexagon(self, hexagon_half_edges, partial_closure_edge, index):
        inv_color = None
        color = partial_closure_edge.color
        if color == 1:
            inv_color = 0
        else:
            inv_color = 1

        #Set color
        for i in range(12):
            if i % 2 == 0:
                hexagon_half_edges[i].color = inv_color
            else:
                hexagon_half_edges[i].color = color

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

        #Set number of nodes.
        node_num = self.___get_max_node_nr(partial_closure_edge) + 1
        current_half_edge = hexagon_half_edges[11]
        while True:
            current_half_edge.node_nr = node_num
            current_half_edge.next.node_nr = node_num
            current_half_edge = current_half_edge.next.opposite
            node_num += 1
            if current_half_edge == hexagon_half_edges[11]:
                break

        #Set indeces for half-edges
        current_half_edge = hexagon_half_edges[0]
        while True:
            current_half_edge.index = index
            current_half_edge.opposite.index = index + 1
            current_half_edge = current_half_edge.opposite.next
            index += 2
            if current_half_edge == hexagon_half_edges[0]:
                break

        # print("Hexagon list:")
        # list_closure = self.list_half_edges(hexagon_half_edges[0], [])
        # for i in list_closure:
        #     print(i)


        #Return the starting half-edge
        return hexagon_half_edges[0]



    def ___reject(self, init_half_edge):
        pass

    #Makes the outer face of the irreducible dissection quadrangular by adding a new edge
    #between two opposite nodes of the hexagon
    def ___quadrangulate(self, init_half_edge):
        new_half_edge = HalfEdge()
        new_half_edge.next = init_half_edge
        new_half_edge.prior = init_half_edge.prior
        index = self.___get_max_half_edge_index(init_half_edge) + 1
        print(index)
        new_half_edge.iter = index
        index += 1
        new_half_edge.node_nr = init_half_edge.node_nr
        new_half_edge.color = init_half_edge.color

        #Iterate to the opposite node of the hexagon node 
        count = 0
        current_half_edge = new_half_edge
        while True:
            current_half_edge = current_half_edge.next
            current_half_edge = current_half_edge.opposite
            count += 1
            if count == 5:
                break

        fresh_half_edge = HalfEdge()
        fresh_half_edge.opposite = new_half_edge
        new_half_edge.opposite = fresh_half_edge

        fresh_half_edge.prior = current_half_edge
        fresh_half_edge.next = current_half_edge.next
        current_half_edge.next.prior = new_half_edge
        current_half_edge.next = fresh_half_edge

        fresh_half_edge.index = index 
        fresh_half_edge.node_nr = current_half_edge.node_nr
        fresh_half_edge.color = current_half_edge.color

        # print("New Half Edge:",end=" ")
        # print(fresh_half_edge)

        return new_half_edge


    #Construct the tree map for a given qundrangulation.
    def ___make_irreducible(self, init_half_edge):
        # Used for the half_edges in the 3-map that corresponds to the half-edges in the quadrangulation.
        associated_half_edge_in_3_map = {}
        self.___quadrangulation_to_3_map_rec(init_half_edge, associated_half_edge_in_3_map)
        return associated_half_edge_in_3_map[init_half_edge.next]


    #Recursivly transform the quadrangulation to a 3-map where the next and prev pointers are kept as
    #before, but the opposite pointer in the half edge is pointing to the opposite half-edge in the face.
    def ___make_irreducible_rec(self, init_half_edge, associated_half_edges_in_3_map):
        # Associate the initial half edge
        initial_half_edge_association = HalfEdge()
        initial_half_edge_association.index = init_half_edge.index
        associated_half_edges_in_3_map[init_half_edge] = initial_half_edge_association

        # Associate the half edges that are on the same vertex as tie initial one.
        walker_half_edge = init_half_edge.next
        while walker_half_edge is not init_half_edge:
            walker_association = HalfEdge()
            walker_association.index = walker_half_edge.index
            associated_half_edges_in_3_map[walker_half_edge] = walker_association

            # Connect the association with the association of the prev half-edge
            walker_association.prior = associated_half_edges_in_3_map[walker_half_edge.prior]
            associated_half_edges_in_3_map[walker_half_edge.prior].next = walker_association

            # Continue with the next edges
            walker_half_edge = walker_half_edge.next

        # Add the final connection
        initial_half_edge_association.prior = associated_half_edges_in_3_map[init_half_edge.prior]
        associated_half_edges_in_3_map[init_half_edge.prior].next = initial_half_edge_association

        # Make the opposite pointer of the half edge to point to the opposite half edge in the face.
        skipFirst = True
        walker_half_edge = init_half_edge
        while walker_half_edge is not init_half_edge and skipFirst is True:
            skipFirst = False
            opposite_half_edge_in_face = walker_half_edge.next.opposite.next.opposite

            # Check for already processed half edges
            if opposite_half_edge_in_face not in associated_half_edges_in_3_map:
                self.___quadrangulation_to_3_map_rec(opposite_half_edge_in_face, associated_half_edges_in_3_map)

            # Make the actual opposite connection between the associations
            associated_half_edges_in_3_map[opposite_half_edge_in_face].opposite = associated_half_edges_in_3_map[walker_half_edge]
            associated_half_edges_in_3_map[walker_half_edge].opposite = associated_half_edges_in_3_map[opposite_half_edge_in_face]

            # Continue with the next edges
            walker_half_edge =walker_half_edge.next



    #Returns a list with half-edges
    def list_half_edges(self, init_half_edge, edge_list):       
        edge_list.append(init_half_edge)
        current_half_edge = init_half_edge

        while True:
            current_half_edge = current_half_edge.next
            if current_half_edge != init_half_edge and current_half_edge not in edge_list:
                edge_list.append(current_half_edge)
                if current_half_edge.opposite != None:
                    if current_half_edge.opposite not in edge_list:
                        self.list_half_edges(current_half_edge.opposite, edge_list)
            else:
                break
        return edge_list



    #Transforms a list of planar map half-edged into a networkx graph
    def half_edges_to_graph(self, init_half_edge):
        half_edge_list = self.list_half_edges(init_half_edge, [])

        #Remove all unpaired half-edges
        half_edge_list = [x for x in half_edge_list if not x.opposite == None]

        G = nx.Graph()

        while len(half_edge_list) > 0:
            half_edge = half_edge_list.pop()
            G.add_edge(half_edge.node_nr, half_edge.opposite.node_nr)
            half_edge_list.remove(half_edge.opposite)
        return G



    def ___get_max_half_edge_index(self, init_half_edge):        
        edge_list = self.list_half_edges(init_half_edge, [])
        max_index = 0
        for x in edge_list:
            if x.index > max_index:
                max_index = x.index
        return max_index



    def ___get_max_node_nr(self, init_half_edge):
        edge_list = self.list_half_edges(init_half_edge, [])
        max_node = 0
        for x in edge_list:
            if x.index > max_node:
                max_node = x.index
        return max_node


    def closure(self, binary_tree):
        """This function implements the bijection between the binary trees
        and the edge-rooted 3-connected planar graphs. It first perfomrs the 
        partial closure by adding a new edge to three inner edges of the
        binary tree (every face in the binary tree has now four edges).
        Afterwards, the complete closure is performed, where the partialy
        closed binary tree is integrated into a hexagon (dissection of hexagon).
        The last step is to make the outer face of the graph to a four-edge
        face (quadrangulation of the hexagon).
        """
        init_half_edge = self.___btree_to_planar_map(binary_tree)
        init_half_edge = self.___bicolored_complete_closure(init_half_edge)
        if self.___reject(init_half_edge):
            return None
        init_half_edge = self.___quadrangulate(init_half_edge)
        init_half_edge = self.___quadrangulation_to_3_map(init_half_edge)
        return init_half_edge

    def test_closure(self):
        # print("Start test...")
        half_edges = [HalfEdge() for i in range(24)]

        #Set indices
        for i in range(24):
            half_edges[i].index = i

        #Set node_nrs
        half_edges[0].node_nr = 0
        half_edges[1].node_nr = 0
        half_edges[2].node_nr = 0
        half_edges[3].node_nr = 1
        half_edges[4].node_nr = 1
        half_edges[5].node_nr = 1
        half_edges[6].node_nr = 3
        half_edges[7].node_nr = 3
        half_edges[8].node_nr = 3
        half_edges[9].node_nr = 6
        half_edges[10].node_nr = 6
        half_edges[11].node_nr = 6
        half_edges[12].node_nr = 2
        half_edges[13].node_nr = 2
        half_edges[14].node_nr = 2
        half_edges[15].node_nr = 4
        half_edges[16].node_nr = 4
        half_edges[17].node_nr = 4
        half_edges[18].node_nr = 5
        half_edges[19].node_nr = 5
        half_edges[20].node_nr = 5
        half_edges[21].node_nr = 7
        half_edges[22].node_nr = 7
        half_edges[23].node_nr = 7

        #Set colors
        half_edges[0].color = 0
        half_edges[1].color = 0
        half_edges[2].color = 0
        half_edges[3].color = 1
        half_edges[4].color = 1
        half_edges[5].color = 1
        half_edges[6].color = 0
        half_edges[7].color = 0
        half_edges[8].color = 0
        half_edges[9].color = 1
        half_edges[10].color = 1
        half_edges[11].color = 1
        half_edges[12].color = 1
        half_edges[13].color = 1
        half_edges[14].color = 1
        half_edges[15].color = 0
        half_edges[16].color = 0
        half_edges[17].color = 0
        half_edges[18].color = 0
        half_edges[19].color = 0
        half_edges[20].color = 0
        half_edges[21].color = 1
        half_edges[22].color = 1
        half_edges[23].color = 1


        #Set opposite half-edges
        half_edges[1].opposite = half_edges[3]
        half_edges[3].opposite = half_edges[1]
        half_edges[2].opposite = half_edges[12]
        half_edges[12].opposite = half_edges[2]
        half_edges[4].opposite = half_edges[6]
        half_edges[6].opposite = half_edges[4]
        half_edges[8].opposite = half_edges[9]
        half_edges[9].opposite = half_edges[8]
        half_edges[13].opposite = half_edges[15]
        half_edges[15].opposite = half_edges[13]
        half_edges[14].opposite = half_edges[18]
        half_edges[18].opposite = half_edges[14]
        half_edges[19].opposite = half_edges[21]
        half_edges[21].opposite = half_edges[19]

        #Set next and prior
        half_edges[0].next = half_edges[1]
        half_edges[0].prior = half_edges[2]
        half_edges[1].next = half_edges[2]
        half_edges[1].prior = half_edges[0]
        half_edges[2].next = half_edges[0]
        half_edges[2].prior = half_edges[1]
        half_edges[3].next = half_edges[4]
        half_edges[3].prior = half_edges[5]
        half_edges[4].next = half_edges[5]
        half_edges[4].prior = half_edges[3]
        half_edges[5].next = half_edges[3]
        half_edges[5].prior = half_edges[4]
        half_edges[6].next = half_edges[7]
        half_edges[6].prior = half_edges[8]
        half_edges[7].next = half_edges[8]
        half_edges[7].prior = half_edges[6]
        half_edges[8].next = half_edges[6]
        half_edges[8].prior = half_edges[7]
        half_edges[9].next = half_edges[10]
        half_edges[9].prior = half_edges[11]
        half_edges[10].next = half_edges[11]
        half_edges[10].prior = half_edges[9]
        half_edges[11].next = half_edges[9]
        half_edges[11].prior = half_edges[10]
        half_edges[12].next = half_edges[13]
        half_edges[12].prior = half_edges[14]
        half_edges[13].next = half_edges[14]
        half_edges[13].prior = half_edges[12]
        half_edges[14].next = half_edges[12]
        half_edges[14].prior = half_edges[13]
        half_edges[15].next = half_edges[16]
        half_edges[15].prior = half_edges[17]
        half_edges[16].next = half_edges[17]
        half_edges[16].prior = half_edges[15]
        half_edges[17].next = half_edges[15]
        half_edges[17].prior = half_edges[16]
        half_edges[18].next = half_edges[19]
        half_edges[18].prior = half_edges[20]
        half_edges[19].next = half_edges[20]
        half_edges[19].prior = half_edges[18]
        half_edges[20].next = half_edges[18]
        half_edges[20].prior = half_edges[19]
        half_edges[21].next = half_edges[22]
        half_edges[21].prior = half_edges[23]
        half_edges[22].next = half_edges[23]
        half_edges[22].prior = half_edges[21]
        half_edges[23].next = half_edges[21]
        half_edges[23].prior = half_edges[22]

        # print("Planar map list:")
        # list_closure = self.list_half_edges(half_edges[0], [])
        # for i in list_closure:
        #     print(i)
        # closure_start_half_edge = self.___bicolored_complete_closure(half_edges[0])

        # quadrangulated_start_half_edge = self.___quadrangulate(closure_start_half_edge)

        # G = self.half_edges_to_graph(quadrangulated_start_half_edge)
        # nx.draw(G)
        # plt.show()

        


