#!/usr/bin/python
###
# Basic configuration for running Vivaldi.
# n: number of nodes
# K: number of neighbors
# num_iterations: number of iterations for adjusting the coordinates
# d: number of dimensions (network coordinates)
#
# The following parameters can be used to weight the movement and the error estimation.
# However, this depends also on your implementation.
# If you do not use them, remove them.
#
# delta: scale factor of the movement
# ce: precision weight in error estimation
# precision: for the relative error
# 
###
class Configuration():
	def __init__(self, n, K, num_iterations, d=3, delta=0.25, ce=0.25, precision=1000):
		self.num_nodes = n
		self.num_neighbors = K
		self.num_interations = num_iterations
		self.num_dimension = d
		self.delta = delta
		self.ce = ce
		self.precision = precision
	
	# Getter methods
	def getNumInterations(self):
		return self.num_interations
		
	def getNumNodes(self):
		return self.num_nodes
		
	def getNumNeighbors(self):
		return self.num_neighbors
	
	def getNumDimension(self):
		return self.num_dimension
	
	def getDelta(self):
		return self.delta
	
	def getCe(self):
		return self.ce
		
	def getPrecision(self):
		return self.precision
	
