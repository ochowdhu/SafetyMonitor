#!/usr/bin/python
##
##
## @author Aaron Kane
##
## Starting a clean monitor for new performance data
##	 Full file is getting a little crowded

import sys
import signal

# Get some stuff out of here, easier to deal with
from monUtils import *
from timer import Timer

# global constants
delim = ','
algChoose = None 
# benchmarking variables
TimeData = monTimeData()
# time/count for total execution time
looptime = 0
loopcount = 0
# time/count for incrementing structure
incrtime = 0
incrcount = 0
# count for total time to reduce residues 
redtime = 0
redcount = 0
# maximum # of residues carried
max_rescount = 0
# memory count (add up bytes here?)
memorycount = 0

###### Keeping this script compatible with resMonitor for now
def main():
	global algChoose
	# do setup
	signal.signal(signal.SIGINT, signal_handler)
	#### Handle input parameters
	##############################
	if len(sys.argv) > 3:
		inFormula = eval(sys.argv[1])	# DANGEROUS. DON'T PASS ME ARBITRARY CODE
		inFile = open(sys.argv[2], "r")
		algChoose = sys.argv[3]
	else:
		print "Bad Usage: python monitor.py <formula> <tracefile> <algChoose>"
		sys.exit(1)
	print "using %s" % (inFormula)

	##############################
	# build traceOrder
	traceOrder = []
	names = inFile.readline().strip().split(delim)
	# allow comments above names
	while (names[0].startswith("#")):
		names = inFile.readline().strip().split(delim)
	for n in names:
		traceOrder.append(n)
	print "TraceOrder is: %s" % (traceOrder,)

	###### All set up, call one of the monitoring algorithms	
	print "############## Finished setting up"
	print "############## Beginning monitor algorithm: %s" % algChoose
	#mon_residue(inFile, inFormula, traceOrder)
	if (algChoose == "res"):
		algChoose = ALG_RES
		mon_residue(inFile, inFormula, traceOrder)
	elif (algChoose == "purecons"):
		algChoose = ALG_PURECONS
		mon_purecons(inFile, inFormula, traceOrder)
	else:
		print "No algorithm chosen, quitting..."
############# END MAIN ############
##################################

############## BEGIN MONITOR FUNCTIONS ###########
def mon_purecons(inFile, inFormula, traceOrder):
	global TimeData		# timing data container
	allPass = True
	FastDie = False
	cstate = {}
	history = {}
	WD = wdelay(inFormula)
	PD = past_delay(inFormula)
	D = delay(inFormula)
	#
	eptr = 0
	cptr = 0
	#
	dprint("Using WD: %s D: %s, PD: %s" % (WD,D,PD))
	#
	for line in inFile:
		with Timer() as mytimer:
			updateState(cstate, traceOrder, line)
			history[cptr] = cstate.copy()
			#
			dprint("current state is %s" % (cstate,), DBG_SMON)
			#
			cptime = tau(history, cptr)
			while ((eptr <= cptr) and (cptime - tau(history,eptr) >= WD)):
				dprint("checking step %s" % eptr, DBG_SMON)
				mon = smon_purecons(eptr, history, inFormula)
				#
				allPass = allPass and mon
				if (bool(mon) == False):
					dprint("!!!!FORMULA VIOLATED %s@%s -- %s@%s" % (eptr, cptr, tau(history, eptr), tau(history,cptr)), DBG_SAT)
					# quit if we want
					#if (FastDie):
					#	sys.exit(5)
				eptr = eptr + 1
			TimeData.addMemSize(len(history))
			# clean history
			histremove = [k for k in history if (cptime - tau(history,k) > (PD+D))]	
			for k in histremove:
				del history[k]
			# increment current pointer
			cptr = cptr + 1
		TimeData.addLoopTime(mytimer.secs)
	####
	# Done, print performance results and sat/viol
	dprint("TimeData: %s" % TimeData)
	if allPass:
		print "#### Trace Satisfied formula ###"
	else:
		print "### Trace Violated formula ###"

def smon_purecons(cstep, history, formula):
	# just return True if checking something before we have state
	# this is essentially initialization -- protects us from failing due to 
	# past time invariants that look past the beggining of the trace
	formtype = ftype(formula)
	if (cstep < 0):
		return True
	elif (formtype == PROP_T):
		return history[cstep][rchild(formula)]
	elif (formtype == NOT_T):
		return not smon_purecons(cstep, history, rchild(formula))
	elif (formtype == OR_T):
		return smon_purecons(cstep, history, lchild(formula)) or smon_purecons(cstep, history, rchild(formula))
	elif (formtype == UNTIL_T): 
		l = tau(history, cstep) + formula[1]
		h = tau(history, cstep) + formula[2]
		end = None

		for i in history:
			if (tau(history,i) > h):
				break
			elif (l <= tau(history,i)): # guaranteed <= h
				if smon_purecons(i, history, untilP2(formula)):
					end = i
					break
		# didn't find the event in the bounds
		if (end is None):
			return False

		# found P2, check always P1
		l = tau(history, cstep)
		h = tau(history, end)
		for i in history:
			if (tau(history, i) > h):
				break
			#elif (l <= tau(history,i)): # guaranteed tau <= h 
			# apparently the usual semantics is l < tau, so using that
			elif (l < tau(history,i)): # guaranteed tau <= h 
				if not smon_purecons(i, history, untilP1(formula)):
					return False
		# didn't find point where subform was false
		return True
	elif (formtype == SINCE_T):
		l = tau(history, cstep) - formula[2]
		h = tau(history, cstep) - formula[1]
		start = None

		for i in history:
			if (tau(history, i) > h):
				break
			elif (l <= tau(history,i)): # guaranteed tau <= h due to test above
				if smon_purecons(i, history, untilP2(formula)):
					start = i
					# don't break - we want the most recent P1
					#break
		# didn't find the event in the bounds
		if (start is None):
			return False

		# found P2, check always P1
		l = tau(history, start)
		h = tau(history, cstep)

		for i in history:
			if (tau(history, i) > h):
				break
			#elif (l <= tau(history,i)): # guaranteed tau <= h due to test above
			### making this < instead of <= because that's what Omar has
			elif (l < tau(history,i)): # guaranteed tau <= h due to test above
				if not smon_purecons(i, history, untilP1(formula)):
					return False
		# didn't find point where subform was false
		return True
	else:
		print "INVALID smon_purecons: got formula %s" % formula
		return INVALID_T


def mon_residue(inFile, inFormula, traceOrder):
	global TimeData
	# some algorithm local variables
	cstate = {}
	formulas = []
	Struct = {}
	# build struct and save delay
	#D = delay(inFormula)
	#DP = past_delay(inFormula)
	WD = wdelay(inFormula)
	with Timer() as t:
		build_structure(Struct, inFormula)
	print "Build Structure took %s ms" % (t.msecs,)

	dprint("Struct is: ", DBG_STRUCT)
	for s in Struct:
		dprint("%s" % (Struct[s],), DBG_STRUCT)
		
	dprint("Formula wait delay %d" % (WD,), DBG_SMON)
	#dprint("Formula delay is %d, %d :: wait delay %d" % (D,DP,WD), DBG_SMON)
	# wait for new data...
	for line in inFile:
			with Timer() as tt:
				dprint("###### New event received",DBG_SMON)
				updateState(cstate, traceOrder, line)
				with Timer() as t:
					incr_resStruct(Struct, cstate)
				TimeData.addStIncTime(t.secs)

				dprint("Adding current formula", DBG_SMON)
				formulas.append((cstate["time"], inFormula))
				dprint(formulas, DBG_SMON)
				dprint("reducing all formulas", DBG_SMON)
				for i,f in enumerate(formulas[:]):
					#formulas[i] = (f[0], reduce(substitute_as(Struct, cstate, f)))
					formulas[i] = ag_reduce(Struct, cstate, f)
				dprint(formulas, DBG_SMON)
				dprint("removing finished formulas and check violations...", DBG_SMON)
				# count avg reduction time
				rform = [f[0] for f in formulas if f[1] == True]
				for i in rform:
					TimeData.addReduceTime(int(cstate["time"] - int(i)))
				# check for max number of carried residues before we remove good ones
				TimeData.checkMaxRes(len(formulas))
				# remove any True formulas from the list
				formulas[:] = [f for f in formulas if f[1] != True]
				# skip actually checking while we see if struct build works
				for i,f in enumerate(formulas[:]):
					if (f[1] == False):
							#dprint("TimeData: %s" % TimeData, DBG_TIME)
							print "Violator %s" % (f,)
							del formulas[i]
							#sys.exit(1)
					else:	# eventually never satisfied
						if (f[0]+WD <= cstate["time"]):
							#dprint("TimeData: %s" % TimeData, DBG_TIME)
							print "VIOLATOR: %s" % (f,)
							print "!!!! VIOLATION DETECTED AT %s@%s" % (f[0],cstate["time"],)
							del formulas[i]
							#sys.exit(1)
			TimeData.addLoopTime(tt.secs)
	dprint("TimeData: %s" % TimeData, DBG_TIME)
	print "#### finished, trace satisfies formula"



def simplify(formula):
	if (ftype(formula) == VALUE_T):
		return formula
	elif (ftype(formula) == PROP_T):
		dprint("shouldn't get here, already sub'd", DBG_ERROR)
		return cstate[formula[1]]
	elif (ftype(formula) == NOT_T):
		child = simplify(formula[1])
		if (ftype(child) == VALUE_T):
			return not child
		else:
			return ['notprop', child]
	elif (ftype(formula) == OR_T):
		child1 = simplify(formula[1])
		child2 = simplify(formula[2])
		if (child1 == True or child2 == True):
			return True
		elif (child1 == False and child2 == False):
			return False
		else:
			return ['orprop', child1, child2]
	elif (ftype(formula) == UNTIL_T): 
		## Fill in with check and return formula if not sure yet
		return formula
	elif (ftype(formula) == SINCE_T):
		return formula
	else:
		return INVALID_T


def ag_reduce(Struct, cstate, formula_entry):
	ctime = cstate["time"]
	formtime = formula_entry[0]
	formula = formula_entry[1]
	formtype = ftype(formula)
	if (formtype == VALUE_T):
		return (formtime, formula)
	elif (formtype == PROP_T):
		if (cstate[formula[1]]):
			return (formtime, True)
		else:
			return (formtime, False)
	elif (formtype == NOT_T):
		child = ag_reduce(Struct, cstate, (formtime, formula[1]))
		child = simplify(['notprop', child[1]])
		return (formtime, child)
	elif (formtype == OR_T):
		child1 = ag_reduce(Struct, cstate, (formtime, formula[1]))
		child2 = ag_reduce(Struct, cstate, (formtime, formula[2]))
		ans = simplify(['orprop', child1[1], child2[1]])
		return (formtime, ans)
	elif (formtype == UNTIL_T): 
		tags = get_tags(formula)
		st_alpha = Struct[tags[0]].residues
		st_beta = Struct[tags[1]].residues
		st_betatime = Struct[tags[1]].ctime
		#hst_alpha = st_alpha.history
		#hst_beta = st_beta.history
		h = hbound(formula) + formtime
		l = lbound(formula) + formtime

		# get spot alpha is alive until
		st_alpha_bound = sorted([i for i in st_alpha if formtime <= rstep(i) and rstep(i) <= h])
		st_beta_bound = sorted([i for i in st_alpha if l <= rstep(i) and rstep(i) <= h])

		# find the spot alpha could be true until
		a_alive = None
		for i in st_alpha_bound:
			if (rform(i) == False):
				a_alive = rstep(i)
				break
		# get spot alpha is true until
		a_until = None
		for i in st_alpha_bound:
			if (rform(i) == True):
				a_until = rstep(i)
			else:
				break	# quit once we find a not-true
		# find the lowest possible time for beta
		b_alive = None
		for i in st_beta_bound:
			if (rform(i) != False):
				b_alive = rstep(i)
				break
		# find the lowest actual beta
		b_actual = None
		for i in st_beta_bound:
			if (rform(i) == True):
				b_actual = rstep(i)
				break
		# all beta's false?
		b_none = None
		if (ctime > h):
			b_none = True
			for i in st_beta_bound:
				if (rform(i) != False):
					b_none = False
					break
		if (b_actual is not None and a_until is not None and b_actual <= a_until):
			return (formtime, True)
		elif (b_alive is not None and a_alive is not None and a_alive <= b_alive):
			return (formtime, False)
		elif (b_none == True):
			return (formtime, False)
		else:
			return (formtime, formula)
	elif (formtype == SINCE_T):
		tags = get_tags(formula)
		st_alpha = Struct[tags[0]].residues
		st_beta = Struct[tags[1]].residues
		st_betatime = Struct[tags[1]].ctime
		#hst_alpha = st_alpha.history
		#hst_beta = st_beta.history
		h = formtime - lbound(formula)
		l = formtime - hbound(formula)

		# get spot alpha is alive until
		st_alpha_bound = sorted([i for i in st_alpha if l <= rstep(i) and rstep(i) <= formtime])
		st_beta_bound = sorted([i for i in st_alpha if l <= rstep(i) and rstep(i) <= h])

		st_alpha_bound.reverse()	
		st_beta_bound.reverse()
		# find the spot alpha could be true since (highest false in range)
		a_alive = None
		for i in st_alpha_bound:
			if (rform(i) == False):
				a_alive = rstep(i)
				break
		# get spot alpha is true since (lowest value in chain of true's)
		a_since = None
		for i in st_alpha_bound:
			if (rform(i) == True):
				a_since = rstep(i)
			else:
				break	# quit once we find a not-true
		# find the most recent possible time for beta (highest)
		b_alive = None
		for i in st_beta_bound:
			if (rform(i) != False):
				b_alive = rstep(i)
				break
		# find the most recent actual beta (highest)
		b_actual = None
		for i in st_beta_bound:
			if (rform(i) == True):
				b_actual = rstep(i)
				break
		# all beta's false?
		b_none = None
		if (ctime > h):
			b_none = True
			for i in st_beta_bound:
				if (rform(i) != False):
					b_none = False
					break
		if (b_actual is not None and a_since is not None and b_actual >= a_since):
			return (formtime, True)
		elif (b_alive is not None and a_alive is not None and a_alive >= b_alive):
			return (formtime, False)
		elif (b_none == True):
			return (formtime, False)
		else:
			return (formtime, formula)
	else:
		return INVALID_T

def incr_resStruct(Struct, cstate):
	ctime = cstate["time"]
	taglist = list(Struct.keys())
	taglist.sort()
	taglist.reverse()
	# in increasing formula size...
	for t in taglist:
		cStruct = Struct[t]
		# add (ctime, formula) to struct
		cStruct.addRes(ctime, cStruct.formula)
		# call reduce on all residues
		cStruct.incrRes(Struct, cstate)
		# remove old stuff
		cStruct.cleanRes()
		dprint("Incremented and cleaned: %s" % (cStruct,), DBG_STRUCT)
	return

def build_structure(Struct, formula, extbound=0):
	if (ftype(formula) == PROP_T):
		dprint("BUILDING: got a prop, returning", DBG_STRUCT)
		return True
	elif (ftype(formula) == NOT_T):
		dprint("BUILDING: got a not, recursing", DBG_STRUCT)
		build_structure(Struct, rchild(formula), extbound)
		return True
	elif (ftype(formula) == OR_T):
		dprint("BUILDING: got an or, recursing both", DBG_STRUCT)
		build_structure(Struct, lchild(formula), extbound)
		build_structure(Struct, rchild(formula), extbound)
		return True
	elif (ftype(formula) == UNTIL_T): 
		dprint("BUILDING: got an until, ADDING STRUCT and recursing both", DBG_STRUCT)
		# Tags get put into formula[2] so tagging P2 then P1 makes formula into
		# [bound, bound, tagP1, tagP2, P1, P2]
		d = hbound(formula) + extbound
		# do P2
		cTag = tag_formula(formula)
		add_struct(Struct, cTag, d, untilP2(formula))
		# do P1
		cTag = tag_formula(formula)
		add_struct(Struct, cTag, d, untilP1(formula))
		build_structure(Struct, untilP1(formula), extbound=d)
		build_structure(Struct, untilP2(formula), extbound=d)
		return True
	elif (ftype(formula) == PALWAYS_T):
		dprint("BUILDING: got a past always, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		d = past_delay(formula) + extbound
		add_struct(Struct, cTag, d, rchild(formula))
		return build_structure(Struct, rchild(formula), extbound=d)
	elif (ftype(formula) == PEVENT_T):
		dprint("BUILDING: got a past eventually, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		d = past_delay(formula) + extbound
		add_struct(Struct, cTag, d, rchild(formula))
		return build_structure(Struct, rchild(formula), extbound=d)
	elif (ftype(formula) == SINCE_T):
		dprint("BUILDING: got a since, ADDING BOTH STRUCTS and recursing both", DBG_STRUCT)
		# Tags get put into formula[2] so tagging P2 then P1 makes formula into
		# [bound, bound, tagP1, tagP2, P1, P2]
		d = past_delay(formula) + extbound
		# do P2
		cTag = tag_formula(formula)
		add_struct(Struct, cTag, d, untilP2(formula))
		# do P1
		cTag = tag_formula(formula)
		add_struct(Struct, cTag, d, untilP1(formula))
		build_structure(Struct, untilP1(formula), extbound=d)
		build_structure(Struct, untilP2(formula), extbound=d)
		return True
	else:
		dprint("BUILDING ERROR: Got unmatched AST node while building", DBG_STRUCT);
		return False
	# shouldn't get here
	return False

def add_struct(Struct, tag, delay, formula):
	global algChoose
	if (algChoose == ALG_RES):
		newSt = resStructure(formula, delay)
	else:
		dprint("!!!!SHOULD NOT GET HERE....!!!", DBG_ERROR)
		sys.exit(2)
	# Add interval that fills entire past bound 
	for i in range(0-delay, 0):
		newSt.addRes(i, True)
	Struct[tag] = newSt
	dprint("Added %s to %s" % (newSt, Struct), DBG_STRUCT)
	return

def updateState(cstate, traceOrder, line):
	vals = line.strip().split(delim)
	for i in range(0, len(vals)):
		dprint("%d| Updating %s to %s" % (i, traceOrder[i], vals[i]), DBG_STATE)
		cstate[traceOrder[i]] = int(vals[i])

def signal_handler(signal, frame):
	print "Caught ctrl-c, exiting..."
	sys.exit(1)

if __name__ == "__main__":
	main()
