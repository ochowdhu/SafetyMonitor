#!/bin/python
#### generate a satisfying/violating trace given a formula

from monUtils import *
import sys
import random
from csv import DictWriter
from distutils.util import strtobool


### starting simple, just 4 predetermined props and a table


#SATISFY = True
Trace = {}
conflict = []
rseed = "AGMON"
override = False

def main():
	global override
	SATISFY = True
	NUMSTEPS = 0
	STEP = -1 
	propset = set()
	vsteps = []
	#random.seed(rseed)

	if len(sys.argv) < 1:
		print "Usage: formTraceGen.py <formula> <step/range> <satisfy> <vsteps>"
		exit(1)
	if (len(sys.argv) > 2):
		inRange = int(sys.argv[2])
	else:
		inRange = 0
	if (len(sys.argv) > 3):
		SATISFY = bool(strtobool(sys.argv[3]))
		if sys.argv[4] != "":
			vsteps = sys.argv[4].split(",")

	# grab formula
	inForm = eval(sys.argv[1])
	# grab props
	getProps(inForm, propset)
	proplist = list(propset)
	proplist.insert(0, "time")
	writer = DictWriter(sys.stdout, fieldnames=proplist, delimiter=",", restval=0)
	if (inRange < 0):
		NUMSTEPS = -inRange
	else:
		STEP = inRange


	if STEP >= 0:
		gen(STEP, inForm, SATISFY)
		gen(STEP+delay(inForm), inForm, SATISFY)
	else:
		for i in range(0,NUMSTEPS):
			gen(i, inForm, SATISFY)
		gen(NUMSTEPS+delay(inForm), inForm, SATISFY)
		override = True
		for i in vsteps:
			gen(int(i), inForm, False)
	# need to add a late step to guarantee full check
	##### done generating, print it


	# have to do this manually in some pythons
	#writer.writeheader()
	writer.writerow(dict((fn,fn) for fn in proplist))
	for i in sorted(Trace):
		Trace[i]['time'] = i
		writer.writerow(Trace[i])
	sys.stderr.write("any conflicts?: %s\n" % conflict)

def consgen(i, form, sat):
	formtype = ftype(form)
	if (formtype == VALUE_T):
		return 0
	elif (formtype == PROP_T):
		setprop(i,rchild(form), sat)
	elif (formtype == NOT_T):
		# gen the opposite...
		gen(i, rchild(form), not sat)
	elif (formtype == OR_T):
			# conservative, just do both either false or true
			gen(i, lchild(form), sat)
			gen(i, rchild(form), sat)
	elif (formtype == UNTIL_T): 
		# conservative -- either fill true or just have no B
		if (sat):
			ttime = random.randint(lbound(form),hbound(form)) + i
			gen(ttime, untilP2(form), sat)
			for t in range(i, ttime):
				gen(t, untilP1(form), sat)
		else:
			for t in range(i+lbound(form), i+hbound(form)):
				gen(t, untilP2(form), not sat)
			return
	elif (formtype == SINCE_T):
		# conservative -- either fill true or just have no B
		if (sat):
			ttime = i - random.randint(lbound(form), hbound(form))
			gen(ttime, untilP2(form), sat)
			for t in range(ttime+1, i+1):
				gen(t, untilP1(form), sat)
		else:
			for t in range(i-hbound(form), i):
				gen(t, untilP1(form), sat)
	else:
		pass

def gen(i, form, sat):
	# quick steal
	#consgen(i, form, sat)
	#return
#############################
	formtype = ftype(form)
	if (formtype == VALUE_T):
		return 1
	elif (formtype == PROP_T):
		return setprop(i,rchild(form), sat)
	elif (formtype == NOT_T):
		# gen the opposite...
		return gen(i, rchild(form), not sat)
	elif (formtype == OR_T):
		if (sat == False):
			gen(i, lchild(form), sat)
			gen(i, rchild(form), sat)
		else:
			children = [lchild(form), rchild(form)]
			random.shuffle(children)
			try1 = gen(i, children[0], sat)
			if (not try1):
				try2 = gen(i, children[1], sat)
				if not try2:
					failGen()
					return False
			elif (random.randint(0,1)):
				gen(i, children[1], sat)
		return True

# 			# flip a coin and set depending on flip
#			choice = random.randint(0,5)
#			# 0 -- both true
#			if (choice < 4):
#				gen(i, lchild(form), sat)
#				gen(i, rchild(form), sat)
#			# 1, just left
#			elif (choice == 4):
#				gen(i, lchild(form), sat)
#				gen(i, rchild(form), not sat)
#			# 2, just right
#			elif (choice == 5):
#				gen(i, lchild(form), not sat)
#				gen(i, rchild(form), sat)
	elif (formtype == UNTIL_T): 
		if (sat):
			ttime = None
			r = range(i+lbound(form),i+hbound(form)+1)
			random.shuffle(r)
			for t in r:
				try1 = gen(t, untilP2(form), sat)
				if try1:
					ttime = t
					break
			if ttime == None:
				failGen()

			try1 = True
			for t in range(i, ttime):
				try1 = try1 and gen(t, untilP1(form), sat)
			return try1
		else:
			try1 = True
			for t in range(i+lbound(form), i+hbound(form)+1):
				try1 = gen(t, untilP2(form), sat) and try1
			return try1
###
### just bail for now
###
			# kill both for now -- just don't do anything
			# make a decision - missing a, missing b, 
			lb = lbound(form)
			hb = hbound(form)
			failure = random.randint(0,1)
			# can't do bad a failure if no room
			if (lb == 0 and hb == 0):
				failure = 1
			elif (lb == 0):
				lb = 1
			if (failure == 0):
				# bad a -- pick a b
				# gotta watch out that we don't accidently satisfy with an immediate b
				ttime = random.randint(lb,hb) + i
				gen(ttime, untilP2(form), sat)
				# pick missing a
				# for now let's do no a -- can get trickier later
				# just make one a false for now -- less potential conflicts
				t = random.randint(i,ttime)
				gen(t, untilP1(form), not sat)
				#for t in range(i, ttime):
				#	gen(t, untilP1(form), not sat)
				#for t in range(i, random.randint(i,ttime-2)):
				#	gen(t, untilP1(form), sat)
			elif (failure == 1):
				# no b
				#for t in range(i, i+hbound(form)):
				#	gen(t, untilP1(form), sat)
				for t in range(i+lbound(form), i+hbound(form)):
					gen(t, untilP2(form), not sat)
	elif (formtype == SINCE_T):
		if (sat):
			ttime = i - random.randint(lbound(form), hbound(form))
			try1 = gen(ttime, untilP2(form), sat)
			if not try1:
				failGen()
			try1 = True
			for t in range(ttime+1, i+1):
				try1 = gen(t, untilP1(form), sat) and try1
			return try1
		else:
			try1 = True
			for t in range(i-hbound(form), i):
				try1 = gen(t, untilP1(form), sat) and try1
			return try1
### just bail for now
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

def getProps(form, set):
	formtype = ftype(form)
	if (formtype == VALUE_T):
		return
	elif (formtype == PROP_T):
		set.add(rchild(form))
	elif (formtype == NOT_T):
		getProps(rchild(form), set)
	elif (formtype == OR_T):
		getProps(lchild(form), set)
		getProps(rchild(form), set)
	elif (formtype == UNTIL_T): 
		getProps(untilP1(form), set)
		getProps(untilP2(form), set)
	elif (formtype == SINCE_T):
		getProps(untilP1(form), set)
		getProps(untilP2(form), set)
	else:
		pass

def setprop(i, prop, sat):
	global override
	if i in Trace:
		#print "trace[i] is %s" % Trace[i]
		if prop in Trace[i]:
		#if Trace[i][prop] != -1:
			if override:
				Trace[i][prop] = int(sat)
				return True
			elif Trace[i][prop] != int(sat):
				conflict.append("%s: %s" % (i, prop))
				return False
		else:
			Trace[i][prop] = int(sat)
			return True
	else:
		Trace[i] = dict()
		Trace[i][prop] = int(sat)
		return True

def failGen():
	sys.stderr.write("UNAVOIDABLE COLLISION, FAIL!\n")
	sys.exit(-1)

if __name__ == "__main__":
	main()
