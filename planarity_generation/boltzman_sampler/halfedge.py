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
	
	#Contains the opposite half-edge
	opposite = None
	#Contains the next half-edge in ccw order around the incident node
	next = None
	#Contains the prior half-edge in cw order around the incident node
	prior = None
	#Number of inner edges following after the stem		
	number_proximate_inner_edges = 0
	#Color that indicates what color the incident node has (0 - black, 1 -white)
	color = None
	#Node the half-edge is  assigned to
	node_nr = -1
	#Index
	index = 0

	# def __init__(self, opp = None, nex = None, pri = None, prox = 0, col = None, num = -1):
	# 	self.opposite = opp
	# 	self.next = nex
	# 	self.prior = pri
	# 	self.number_proximate_inner_edges = prox
	# 	self.color = col
	# 	self.node_nr = num 

	#Represents a half-edge as a tuple (opposite, next, prior, color)	
	def __repr__(self):
		repr = '('
		if self.opposite == None:
			repr = repr  + '0'
		else:	
			repr =  repr + '1'
		repr = repr + ", "

		if self.next == None:
			repr = repr + '0'
		else:
			repr = repr + '1'
		repr = repr + ", "
	
		if self.prior == None:
			repr = repr + '0'
		else:
			repr = repr + '1'
		if self.color == None:
			repr = repr + ", 0"
		else:
			if self.color == 0:
				repr = repr + ", black"
			else:
				repr = repr + ", white"
		repr = repr + ", "
		repr = repr + node_nr
		repr = repr + ", "
		repr = repr + index
		repr = repr + ')'
		
		return repr
		
