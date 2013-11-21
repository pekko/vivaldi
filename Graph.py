#!/usr/bin/python

# The RTT matrix is represented by a graph, where vertices are the nodes in the network,
# and the edge connecting the nodes represents the RTT between the nodes.

class Graph():
	# n: number of nodes
	# adjacentList: a dictionary where the key is the node (e.g., v) , and the value is a list of tuple (w, RTTuw)
	def __init__(self, n):
		self.N = n
		self.adjacentList = {}
	
	def addVertex(self,v,w,rtt):
		assert rtt >= 0 # We don't want negative RTTs 
		if v == w:
			return
		if v not in self.adjacentList.keys():
			self.adjacentList[v] = [(w,rtt)]
		else:
			self.adjacentList[v].append((w,rtt))
	
	
	# Getter methods
	
	def getAdjacent(self,v):
		return self.adjacentList[v]
	
	def getRTT(self,v,w):
		if v == w:
			return 0
		for z,rtt in self.adjacentList[v]:
			if z == w:
				return rtt
		return None
	
	def getGraphSize(self):
		return self.N

	def getAdjacentList(self):
		return self.adjacentList

