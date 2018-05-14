# -*- coding: utf-8 -*-

import random
import math as m


#Bernoulli generator
#Make a Bernoulli choice for vector size two. For
#larger vectors choose randomly (according to random
#variable u) the highest probability
def bern(values):
    u = random.uniform(0, 1)
    i = 0;
    while True:
        if u <= values[i]:
             return i
        i += 1
        if i >= len(values):
             return len(values)



#Poisson generator
def pois(p, k):
	s = m.exp(-p)
	for i in range(1, k):
		s = p * s * (1/(i + 1))
	return s



