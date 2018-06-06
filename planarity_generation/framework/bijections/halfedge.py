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

class HalfEdge:

	def __init__(self):
		#Contains the opposite half-edge
		self.opposite = None
		#Contains the next half-edge in ccw order around the incident node
		self.next = None
		#Contains the prior half-edge in cw order around the incident node
		self.prior = None
		#Number of inner edges following after the stem
		self.number_proximate_inner_edges = 0
		#Color that indicates what color the incident node has (0 - black, 1 -white)
		self.color = None
		#Node the half-edge is  assigned to
		self.node_nr = -1
		#Index
		self.index = 0
		#Indicates if the half-edge belongs to the hexagon
		self.is_hexagonal = False
		#Indicates if the half-edge is an edge added by the complete closure
		self.added_by_comp_clsr = False


	#Represents a half-edge as a tuple (index, node_nr, opposite, next, prior, color, number_proximate)	
	def __repr__(self):
		repr = '('
		repr = repr + str(self.index)
		repr = repr + ", "
		repr = repr + str(self.node_nr)
		repr = repr + ", "

		if self.opposite == None:
			repr = repr  + "None"
		else:	
			repr =  repr + str(self.opposite.index)
		repr = repr + ", "

		if self.next == None:
			repr = repr + "None"
		else:
			repr = repr + str(self.next.index)
		repr = repr + ", "
	
		if self.prior == None:
			repr = repr + "None"
		else:
			repr = repr + str(self.prior.index)
		if self.color == None:
			repr = repr + ", None"
		else:
			if self.color == 0:
				repr = repr + ", black"
			else:
				repr = repr + ", white"
		repr = repr + ", "
		repr = repr + str(self.number_proximate_inner_edges)
		if self.is_hexagonal == False:
			repr = repr + ", NOT hexagonal"
		else:
			repr = repr + ", hexagonal"

		if self.added_by_comp_clsr == False:
			repr = repr + ", NOT added by clsr"
		else:
			repr = repr + ", added by clsr"
			
		repr = repr + ')'
		
		return repr
		
