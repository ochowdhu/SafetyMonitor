#!/bin/python
#### generate a satisfying/violating trace given a formula

from monUtils import *
import sys
import random


### starting simple, just 4 predetermined props and a table


SATISFY = True
Trace = {}
conflict = []
rseed = "AGMON"

def main():
	NUMSTEPS = 0
	STEP = -1 
	#random.seed(rseed)
	if len(sys.argv) < 1:
		print "Usage: formTraceGen.py <formula> <step/range>"
		exit(1)
	elif (len(sys.argv) > 2):
		inRange = int(sys.argv[2])
	else:
		inRange = 0
	# grab formula
	inForm = eval(sys.argv[1])

	if (inRange < 0):
		NUMSTEPS = -inRange
	else:
		STEP = inRange


	if STEP >= 0:
		gen(STEP, inForm, SATISFY)
	else:
		for i in range(0,NUMSTEPS):
			gen(i, inForm, SATISFY)
	##### done generating, print it
	print "Trace is:"
	for i in Trace:
		print "%s: %s" % (i,Trace[i])
	print "any conflicts?: %s" % conflict


def gen(i, form, sat):
	formtype = ftype(form)
	if (formtype == VALUE_T):
		return 0
	elif (formtype == PROP_T):
		setprop(i,rchild(form), sat)
	elif (formtype == NOT_T):
		# gen the opposite...
		gen(i, rchild(form), not sat)
	elif (formtype == OR_T):
		# flip a coin? for now try both
		gen(i, lchild(form), sat)
		gen(i, rchild(form), sat)
	elif (formtype == UNTIL_T): 
		if (sat):
			ttime = random.randint(lbound(form),hbound(form)) + i
			gen(ttime, untilP2(form), sat)
			for t in range(i, ttime):
				gen(t, untilP1(form), sat)
		else:
			# kill both for now -- just don't do anything
			# make a decision - missing a, missing b, 
			failure = random.randint(0,1)
			if (failure == 0):
				# bad a -- pick a b
				ttime = random.randint(lbound(form),hbound(form)) + i
				gen(ttime, untilP2(form), sat)
				# pick missing a
				for t in range(i, random.randint(i,ttime)):
					gen(t, untilP1(form), sat)
			elif (failure == 1):
				# no b
				for t in range(i, i+hbound(form)):
					gen(t, untilP1(form), sat)
				for t in range(i+lbound(form), i+hbound(form)):
					gen(t, untilP2(form), not sat)
	elif (formtype == SINCE_T):
		if (sat):
			ttime = i - random.randint(lbound(form), hbound(form))
			gen(ttime, untilP2(form), sat)
			for t in range(ttime+1, i+1):
				gen(t, untilP1(form), sat)
		else:
			# kill both for now -- just don't do anything
			# make a decision - missing a, missing b, 
			failure = random.randint(0,1)
			if (failure == 0):
				# bad a -- pick a b
				ttime = i - random.randint(lbound(form),hbound(form))
				gen(ttime, untilP2(form), sat)
				# pick missing a
				for t in range(ttime+1, random.randint(ttime+1,i)):
					gen(t, untilP1(form), sat)
			elif (failure == 1):
				# no b
				for t in range(i-hbound(form), i):
					gen(t, untilP1(form), sat)

	else:
		pass

def setprop(i, prop, sat):
	if i in Trace:
		#print "trace[i] is %s" % Trace[i]
		if prop in Trace[i]:
		#if Trace[i][prop] != -1:
			if Trace[i][prop] != int(sat):
				conflict.append("%s: %s" % (i, prop))
		else:
			Trace[i][prop] = int(sat)
	else:
		Trace[i] = dict()
		Trace[i][prop] = int(sat)


if __name__ == "__main__":
	main()
