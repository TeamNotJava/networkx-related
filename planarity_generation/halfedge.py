#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


	#Represents a half-edge as a tuple (opposite, next, prior, color)	
	def __str__(self):
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
			repr = repr + '0'
		else:
			if self.color == 0:
				repr = repr + "black"
			else:
				repr = repr + "white"
		repr = repr + ')'
		
		return repr
		