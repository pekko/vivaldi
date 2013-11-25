#!/usr/bin/python
# Basic Vivaldi implementation

from math import sqrt
import random
import sys

# from Graph import Graph
# from Configuration import Configuration

# from matplotlib import pyplot

def vadd(a,b):
	return [a[i]+b[i] for i in xrange(len(a))]

def vsub(a,b):
	return [a[i]-b[i] for i in xrange(len(a))]

def vmul(v,factor):
	return [factor*a for a in v]

def vdiv(v, divisor):
	return [a/divisor for a in v]

def norm(v):
	return sqrt(sum([a*a for a in v]))




class Vivaldi():
	def __init__(self, graph, configuration):
		self.graph = graph
		self.configuration = configuration
		self.d = configuration.getNumDimension()
		
		# initialize positions with zero arrays
		self.positions = [[0]*self.d for _ in xrange(self.configuration.getNumNodes())]
		self.errors = [0]*self.configuration.getNumNodes()
	
	def _random_direction(self):
		return [random.randint(0,10) for _ in xrange(self.d)]

	def _unit_vector(self, vector):
		if all(vector) == 0:
			return vector
		return vdiv(vector, norm(vector))

	def _update_progress(self, progress):
		length = 50
		done = int(progress*length)
		left = length-done

		sys.stdout.write("\r[" + "="*done + " "*left + "] " + str(int(100*progress)) + " % ")
		sys.stdout.flush()

	def _clear_progress(self):
		sys.stdout.write("\r")
		sys.stdout.flush()
		print

	# Core of the Vivaldi algorithm
	def run(self):
		#TODO: Vivaldi run

		# for each iteration
		iters = self.configuration.getNumInterations()
		ce = self.configuration.getCe()
		for i in xrange(iters):
			rtt_prediction = self.getRTTGraph()
			
			# for each node pick up K random neighbors
			for (node, neighbors) in self.graph.getAdjacentList().iteritems():
				random_neighbors = [random.choice(neighbors) for _ in xrange(self.configuration.getNumNeighbors())]
				
				# check how much the node has to "move" in terms of RTT towards/away his neighbors
				movement = [0]*self.d
				error_sum = 0

				for (neighbor, rtt_measured) in random_neighbors:
					if self.errors[node] == 0: # "divide by zero"
						remote_confidence = 0.01
					else:
						remote_confidence = self.errors[node] / (self.errors[node] + self.errors[neighbor])

					# Error is always >= 0. Direction will be get with vector calculations
					absolute_error = abs(rtt_prediction[node][neighbor] - rtt_measured)
					relative_error =  absolute_error / rtt_measured
					
					error_sum += (relative_error * ce * remote_confidence) + (self.errors[node] * (1 - ce * remote_confidence))

					# If we are at the same position but want to move, let's go to random direction
					# This happens at the very beginning, when all at position [0,0,0]
					direction = vsub(self.positions[neighbor], self.positions[node])
					if all(direction) == 0:
						direction = self._random_direction()
					direction = self._unit_vector(direction)

					# delta = self.configuration.getDelta()
					delta = .1 * remote_confidence
					movement = vadd(movement, vmul(direction, delta * absolute_error))

				# compute the new coordinates following the Vivaldi algorithm
				self.positions[node] = vadd(self.positions[node], movement)
				self.errors[node] = error_sum / len(neighbors)

			self._update_progress(float(i)/iters)
		self._clear_progress()

	# get the predicted RTT graph following Vivaldi.
	def getRTTGraph(self):
		# 2d-array, key node_id_from, 2nd key node_id_to value rtt)
		prediction = [0] * self.configuration.getNumNodes()

		for (nid, neighbors) in self.graph.getAdjacentList().iteritems():
			prediction[nid] = [0] * self.configuration.getNumNodes()
			for (neighbor, rtt) in neighbors:
				prediction[nid][neighbor] = norm(vsub(self.positions[nid], self.positions[neighbor]))

		return prediction

	# get the position of a node 
	def getPositions(self, node):
		return self.positions[node]

	# Relative error of the predicted graph wrt real RTT graph
	def getRelativeError(self, predicted_graph):
		rerr = []
		i = 0
		for neighbors in predicted_graph:
			r = 0
			j = 0
			for rtt_predicted in neighbors:
				rtt_measured = self.graph.getRTT(i, j)
				if rtt_measured != 0:
					r += abs((rtt_predicted - rtt_measured) / rtt_measured)
				j += 1
			rerr.append(r/j)
			i += 1
		return rerr
	
	# basic CDF computation
	def computeCDF(self, input_):
		x = sorted(input_)
		y = map(lambda x: x / float((len(input_) + 1)), range(len(input_)))
		return x,y
