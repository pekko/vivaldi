#!/usr/bin/python

from Graph import Graph
from Configuration import Configuration
from Vivaldi import Vivaldi

import sys, random
from matplotlib.pyplot import *

def buildgraph(rows):
	g = Graph(len(rows))
	for node in range(len(rows)):
		arr = rows[node].strip().split(" ")
		rtts = [float(x) for x in arr if len(x) > 0]
		for neighbor in range(len(rtts)):
			g.addVertex(node,neighbor,rtts[neighbor])
	
	return g
	
def table(data, title=""):
	print
	print "="*30
	print title
	print "-"*len(title)

	length = len(data)
	data = sorted(data)

	print "Average %4d" % (float(sum(data))/length )
	print "Median  %4d" % (data[int(length/2)] )
	print "Min     %4d" % (min(data) )
	print "Max     %4d" % (max(data) )
	print "="*30
	

def update_runs_completed(completed, total):
	sys.stdout.write("\r({}/{})".format(completed, total))
	sys.stdout.flush()

def finish_runs_completed(total):
	update_runs_completed(total, total)
	print

def computeCDF(input_):
	x = sorted(input_)
	y = map(lambda x: x / float((len(input_) + 1)), range(len(input_)))
	return x,y

def plot_rerr(rerr, conf):
	color = ['b', 'g', 'r', 'b+', 'g+', 'r+', 'b.', 'g.', 'r.']
	for i in range(len(rerr)):
		x, y = computeCDF(rerr[i])
		plot(x, y, color[i%len(color)], label=conf[i])

	legend(loc="lower right") #lower, upper, left, right
	show()


def simulate():
	random.seed(1234)
	num_neighbors_options = [3, 10, 20]
	num_iterations_options = [20, 200, 1000]
	runs_per_config = 1

	total_runs = len(num_neighbors_options) * len(num_iterations_options) * runs_per_config
	runs_done = 0
	rerr = [None]*(len(num_neighbors_options)*len(num_iterations_options))
	conf = [None]*(len(num_neighbors_options)*len(num_iterations_options))
	curr_conf = 0

	for num_neighbors in num_neighbors_options:
		for num_iterations in num_iterations_options:
			c = Configuration(num_nodes, num_neighbors, num_iterations)

			conf_rerr = [0]*num_nodes
			conf[curr_conf] = "K: {}, i: {}".format(num_neighbors, num_iterations)
			update_runs_completed(runs_done, total_runs)
			for run in xrange(runs_per_config):
				v = Vivaldi(init_graph, c)
				v.run()
				predicted = v.getRTTGraph()
				temp_rerr = v.getRelativeError(predicted)

				for i in xrange(num_nodes):
					conf_rerr[i] += temp_rerr[i]

				runs_done += 1
				update_runs_completed(runs_done, total_runs)

			for i in xrange(num_nodes):
				conf_rerr[i] = conf_rerr[i] / runs_per_config
			rerr[curr_conf] = conf_rerr
			curr_conf += 1
			
	finish_runs_completed(runs_per_config)
	return rerr, conf

if __name__== "__main__":
	if len(sys.argv) != 2:
		print "Usage: %s <rtt_file>"%sys.argv[0]
		sys.exit(0)
	
	
	rttfile = sys.argv[1]
	infile = open(rttfile, 'r')
	rows = infile.readlines()
	num_nodes = len(rows)
	infile.close()

	init_graph = buildgraph(rows)

	rerr, conf = simulate()
	#print rerr[0]

	
	table([100*x for x in rerr[0]], "RELATIVE ERROR (%)")
	plot_rerr(rerr, conf);

	#x,y = computeCDF(rerr)
	#plot(x,y)
	#show()



