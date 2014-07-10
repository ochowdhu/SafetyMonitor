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
					if (FastDie):
						sys.exit(5)
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
	D = delay(inFormula)
	DP = past_delay(inFormula)
	WD = wdelay(inFormula)
	with Timer() as t:
		build_structure(Struct, inFormula)
	print "Build Structure took %s ms" % (t.msecs,)

	dprint("Struct is: ", DBG_STRUCT)
	for s in Struct:
		dprint("%s" % (Struct[s],), DBG_STRUCT)
		
	dprint("Formula delay is %d, %d :: wait delay %d" % (D,DP,WD), DBG_SMON)
	# wait for new data...
	for line in inFile:
			dprint("###### New event received",DBG_SMON)
			updateState(cstate, traceOrder, line)
			with Timer() as t:
				incr_aStruct(Struct, cstate)
			incrtime = incrtime + t.secs
			incrcount = incrcount + 1

			dprint("Adding current formula", DBG_SMON)
			formulas.append((cstate["time"], inFormula))
			dprint(formulas, DBG_SMON)
			dprint("reducing all formulas", DBG_SMON)
			for i,f in enumerate(formulas[:]):
				#formulas[i] = (f[0], reduce(substitute_as(Struct, cstate, f)))
				formulas[i] = (f[0], simplify(ag_reduce(ag_Struct, cstate, f)))
			dprint(formulas, DBG_SMON)
			dprint("removing finished formulas and check violations...", DBG_SMON)
			# count avg reduction time
			rform = [f[0] for f in formulas if f[1] == True]
			for i in rform:
				redtime = redtime + (int(cstate["time"]) - int(i))
				redcount = redcount + 1
			# remove any True formulas from the list
			formulas[:] = [f for f in formulas if f[1] != True]
			# skip actually checking while we see if struct build works
			for i,f in enumerate(formulas[:]):
				if (f[1] == False):
						dprint("total incr time: %s, # incrs: %s, avg time: %s" % (incrtime, incrcount, incrtime/incrcount),DBG_TIME)
						if redcount != 0:
							dprint("total red time: %s, # red: %s, avg red time: %s" % (redtime, redcount, redtime/redcount),DBG_TIME)
						else:
							dprint("redcount was 0, weird...", DBG_TIME)
						print "!!!! VIOLATION DETECTED AT %s@%s" % (f[0],cstate["time"],)
						sys.exit(1)
				else:	# eventually never satisfied
					if (f[0]+WD <= cstate["time"]):
						dprint("total incr time: %s, # incrs: %s, avg time: %s" % (incrtime, incrcount, incrtime/incrcount),DBG_TIME)
						dprint("total red time: %s, # red: %s, avg red time: %s" % (redtime, redcount, redtime/redcount),DBG_TIME)
						print "VIOLATOR: %s" % (f,)
						print "!!!! VIOLATION DETECTED AT %s@%s" % (f[0],cstate["time"],)
						sys.exit(1)
	dprint("total incr time: %s, # incrs: %s, avg time: %s" % (incrtime, incrcount, incrtime/incrcount),DBG_TIME)
	dprint("total red time: %s, # red: %s, avg red time: %s" % (redtime, redcount, redtime/redcount),DBG_TIME)
	print "#### finished, trace satisfies formula"


def build_structure(Struct, formula, extbound=0):
	if (ftype(formula) == PROP_T):
		dprint("BUILDING: got a prop, returning", DBG_STRUCT)
		return True
	elif (ftype(formula) == NOT_T):
		dprint("BUILDING: got a not, recursing", DBG_STRUCT)
		build_fst_structure(Struct, rchild(formula), extbound)
		return True
	elif (ftype(formula) == OR_T):
		dprint("BUILDING: got an or, recursing both", DBG_STRUCT)
		build_fst_structure(Struct, lchild(formula), extbound)
		build_fst_structure(Struct, rchild(formula), extbound)
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
		build_fst_structure(Struct, untilP1(formula), extbound=d)
		build_fst_structure(Struct, untilP2(formula), extbound=d)
		return True
	elif (ftype(formula) == PALWAYS_T):
		dprint("BUILDING: got a past always, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		d = past_delay(formula) + extbound
		add_struct(Struct, cTag, d, rchild(formula))
		return build_fst_structure(Struct, rchild(formula), extbound=d)
	elif (ftype(formula) == PEVENT_T):
		dprint("BUILDING: got a past eventually, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		d = past_delay(formula) + extbound
		add_struct(Struct, cTag, d, rchild(formula))
		return build_fst_structure(Struct, rchild(formula), extbound=d)
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
		build_fst_structure(Struct, untilP1(formula), extbound=d)
		build_fst_structure(Struct, untilP2(formula), extbound=d)
		return True
	else:
		dprint("BUILDING ERROR: Got unmatched AST node while building", DBG_STRUCT);
		return False
	# shouldn't get here
	return False

def add_struct(Struct, tag, delay, formula):
	global algChoose
	if (algChoose == ALG_RES):
		newSt = aStructure(tag, formula, delay)
	else:
		dprint("!!!!SHOULD NOT GET HERE....!!!", DBG_ERROR)
		sys.exit(2)
	# Add interval that fills entire past bound 
	for i in range(0-delay, 0):
		newSt.addHist(i, True)
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
