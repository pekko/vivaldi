#!/usr/bin/python
# Basic Vivaldi implementation

from math import sqrt
import random
import sys
from matplotlib import pyplot

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
		#random.seed(1337)
		self.graph = graph
		self.configuration = configuration
		self.d = configuration.getNumDimension()
		
		# initialize positions with zero arrays
		self.positions = [[0]*self.d for _ in xrange(self.configuration.getNumNodes())]
		self.errors = [1]*self.configuration.getNumNodes()
		self.error_history = [0] * self.configuration.getNumInterations()
		self.move_len_history = [0] * self.configuration.getNumInterations()
	
	def _random_direction(self):
		return [random.randint(0,10) for _ in xrange(self.d)]

	def _unit_vector(self, vector):
		if all(vector) == 0:
			return vector
		return vdiv(vector, norm(vector))

	def _update_progress(self, progress):
		length = 50
		done = int(round(progress*length))
		left = length-done

		sys.stdout.write("\r[" + "="*done + ">" +" "*left + "] " + str(int(100*progress)) + " % ")
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
			# rtt_prediction = self.getRTTGraph()
			
			temp_error_history = 0.0
			# for each node pick up K random neighbors
			for (node, neighbors) in self.graph.getAdjacentList().iteritems():
				random_neighbors = [random.choice(neighbors) for _ in xrange(self.configuration.getNumNeighbors())]
				
				error_sum = 0
				move_len = 0
				for (neighbor, rtt_measured) in random_neighbors:
					remote_confidence = self.errors[node] / (self.errors[node] + self.errors[neighbor])

					absolute_error = (self.distance(node, neighbor) - rtt_measured)
					relative_error = abs(absolute_error) / rtt_measured
					
					error_sum += (relative_error * ce * remote_confidence) + (self.errors[node] * (1 - ce * remote_confidence))
					temp_error_history += abs(absolute_error)

					# If we are at the same position but want to move, let's go to random direction
					# This happens at the very beginning, when all at position [0,0,0]
					direction = vsub(self.positions[neighbor], self.positions[node])
					if all(direction) == False:
						direction = self._random_direction()
					direction = self._unit_vector(direction)

					delta = ce * remote_confidence
					
					# check how much the node has to "move" in terms of RTT towards/away his neighbors
					# compute the new coordinates following the Vivaldi algorithm
					movement = vmul(direction, delta*absolute_error)
					move_len += norm(movement)
					self.positions[node] = vadd(self.positions[node], movement)

				self.errors[node] = error_sum / len(random_neighbors)
				self.move_len_history[i] += move_len / (self.configuration.getNumNodes() * len(random_neighbors))
			self.error_history[i] = (temp_error_history / (self.configuration.getNumNodes() * self.configuration.getNumNeighbors()))
			#self._update_progress(float(i)/iters)
		#self._clear_progress()
		
		#pyplot.plot(range(len(errorplot)), errorplot)
		#pyplot.ylim(ymin=0)
		#pyplot.show()

	# get the predicted RTT graph following Vivaldi.
	def getRTTGraph(self):
		# 2d-array, key node_id_from, 2nd key node_id_to value rtt)
		prediction = [0] * self.configuration.getNumNodes()

		for (nid, neighbors) in self.graph.getAdjacentList().iteritems():
			prediction[nid] = [0] * self.configuration.getNumNodes()
			for (neighbor, rtt) in neighbors:
				prediction[nid][neighbor] = norm(vsub(self.positions[nid], self.positions[neighbor]))

		return prediction

	def distance(self, fr, to):
		return norm(vsub(self.positions[fr], self.positions[to]))

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
