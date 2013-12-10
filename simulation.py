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
	print "Var     %4d" % (variance(data) )
	print "Max     %4d" % (max(data) )
	print "Min     %4d" % (min(data) )
	print "-----------"
	print "Percentiles:"
	print "50      %4d" % (percentile(data, 0.5) )
	print "90      %4d" % (percentile(data, 0.9) )
	print "99      %4d" % (percentile(data, 0.99) )
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

	title("Relative error for each node, CDF")
	legend(loc="lower right") #lower, upper, left, right
	show()

def plot_error_history(history, conf):
	color = ['b', 'g', 'r', 'b+', 'g+', 'r+', 'b.', 'g.', 'r.']
	for i in xrange(len(history)):
		x, y = (range(len(history[i])), history[i])
		plot(x, y, color[i%len(color)], label=conf[i])

	#yscale('log')
	title("Average of absolute error for each iteration")
	legend(loc="upper right") #lower, upper, left, right
	show()

def plot_move_dist_history(history, conf):
	color = ['b', 'g', 'r', 'b+', 'g+', 'r+', 'b.', 'g.', 'r.']
	for i in xrange(len(history)):
		x, y = (range(len(history[i])), history[i])
		plot(x, y, color[i%len(color)], label=conf[i])

	#yscale('log')
	title("Average of length of movement per node for each iteration")
	legend(loc="upper right") #lower, upper, left, right
	show()


def listadd(list, other):
	for i in xrange(len(list)):
		list[i] += other[i]

def listdiv(list, divisor):
	for i in xrange(len(list)):
		list[i] /= divisor

def variance(data):
	avg = float(sum(data))/len(data)
	return sum([(x-avg)*(x-avg) for x in data])/ (len(data) - 1)

def percentile(data, gamma):
	x, y = computeCDF(data)
	for i in xrange(len(x)):
		if (y[i] > gamma):
			return x[i]
	return -1

def simulate():
	random.seed(1234)
	#num_neighbors_options = [3, 10, 20]
	num_neighbors_options = [3, 10, 20]
	# reverse order because of plot_error_history
	#num_iterations_options = [1000, 200, 20]
	num_iterations_options = [1000]
	runs_per_config = 3

	total_runs = len(num_neighbors_options) * len(num_iterations_options) * runs_per_config
	runs_done = 0
	rerr = [None]*(len(num_neighbors_options)*len(num_iterations_options))
	error_history = [None]*(len(num_neighbors_options)*len(num_iterations_options))
	conf = [None]*(len(num_neighbors_options)*len(num_iterations_options))
	curr_conf = 0
	move_length_history = [None]*(len(num_neighbors_options)*len(num_iterations_options))

	for num_neighbors in num_neighbors_options:
		for num_iterations in num_iterations_options:
			c = Configuration(num_nodes, num_neighbors, num_iterations)

			conf_rerr = [0]*num_nodes
			conf_error_history = [0]*num_iterations
			conf_move_len = [0]*num_iterations

			conf[curr_conf] = "K: {}, i: {}".format(num_neighbors, num_iterations)
			update_runs_completed(runs_done, total_runs)
			for run in xrange(runs_per_config):
				v = Vivaldi(init_graph, c)
				v.run()
				predicted = v.getRTTGraph()
				temp_rerr = v.getRelativeError(predicted)

				listadd(conf_rerr, temp_rerr)
				listadd(conf_error_history, v.error_history)
				listadd(conf_move_len, v.move_len_history)

				runs_done += 1
				update_runs_completed(runs_done, total_runs)

			listdiv(conf_rerr, runs_per_config)
			listdiv(conf_error_history, runs_per_config)
			listdiv(conf_move_len, runs_per_config)

			rerr[curr_conf] = conf_rerr
			error_history[curr_conf] = conf_error_history
			move_length_history[curr_conf] = conf_move_len

			curr_conf += 1

	finish_runs_completed(runs_per_config)
	return {
		'rerr' : rerr,
		'error_history': error_history,
		'move_length_history': move_length_history
	}, conf

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

	simulation_data, conf = simulate()
	#print rerr[0]

	table([float(100*x) for x in simulation_data['rerr'][0]], "RELATIVE ERROR (%)")


	plot_rerr(simulation_data['rerr'], conf)
	plot_error_history(simulation_data['error_history'], conf)
	plot_move_dist_history(simulation_data['move_length_history'], conf)
	#x,y = computeCDF(rerr)
	#plot(x,y)
	#show()



