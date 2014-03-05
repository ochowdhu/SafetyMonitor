#!/usr/bin/python
##
##
## @author Aaron Kane
## Putting everything together

### TODO:
###		Different algorithms:
###			Straight conservative: wait, use history trace?
###			Straight conservative w/structs -- much easier, but full waiting
###
###
###


import sys
import signal

## Some constants
EXP_T, PROP_T, NPROP_T, NOT_T, AND_T, OR_T, IMPLIES_T, EVENT_T, ALWAYS_T, UNTIL_T, PALWAYS_T, PEVENT_T, SINCE_T, INVALID_T = range(14)

## debug constants
DBG_STRUCT = 0x01
DBG_SMON = 0x02
DBG_HISTORY = 0x04
DBG_LEVEL = 0xFF
DBG_MASK = DBG_STRUCT | DBG_HISTORY | DBG_SMON
DEBUG = True
# fill some propositional values, and keep a history buffer
delim = ','
sTag = 0

def main():
	# do setup
	#### Handle input parameters
	##############################
	if len(sys.argv) > 2:
		inFormula = eval(sys.argv[1])
		inFile = open(sys.argv[2], "r")
	else:
		print "Bad Usage: python monitor.py <formula> <tracefile> [fastquit]"
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
	print "############## Beginning monitor algorithm: mon_cons_ST"
	#mon_cons_ST(inFile, inFormula, traceOrder)
	mon_cons(inFile, inFormula, traceOrder)


############# END MAIN ############
##################################

############# MONITOR ALGOS #######
###################################
def mon_cons(inFile, inFormula, traceOrder):
	# some algorithm local variables
	cstate = {}
	cHistory = {}
	eptr = 0
	cptr = 0
	# build struct and save delay
	D = delay(inFormula)
	dprint("Formula delay is %d" % (D,))
	# wait for new data...
	for line in inFile:
			dprint("###### New event received")
			updateState(cstate, traceOrder, line)
			cHistory[cptr] = cstate.copy()
			print "AT STATE %s" % (cstate,)
			while (eptr <= cptr and tau(cHistory, cptr) - tau(cHistory, eptr) >= D):
				dprint("@@@@ evaluating step: %d" % (eptr,))
				mon = smon_cons(cHistory, tau(cHistory,eptr), inFormula)
				if (not mon):
					print "VIOLATION FOUND"
					sys.exit(1)
				print "==== formula value at %d: %s" % (eptr, mon)
				eptr = eptr + 1
			## clean old history out
			## structs are cleaned automatically at update
			for i in cHistory.copy():
				if (tau(cHistory, cptr) - tau(cHistory, i) > D):
					cHistory.pop(i)
					print "removed %d from History" % (i,)
			cptr = cptr + 1
## END mon_cons

def smon_cons(hist, ctime, formula):
	(sid,cstate) = getState(hist, ctime)
	if (ftype(formula) == EXP_T):
		dprint("got an exp, returning", DBG_SMON)
		return smon_cons(hist, ctime, rchild(formula))
	elif (ftype(formula) == PROP_T):
		dprint("got a prop, returning", DBG_SMON)
		return cstate[rchild(formula)]
	elif (ftype(formula) == NPROP_T):
		dprint("got an nprop", DBG_SMON)
		return not cstate[rchild(formula)]
	elif (ftype(formula) == NOT_T):
		dprint("got a notprop", DBG_SMON)
		return not smon_cons(hist, ctime, rchild(formula))
	elif (ftype(formula) == AND_T):
		dprint("got an and, returning both", DBG_SMON)
		return smon_cons(hist, ctime, lchild(formula)) and smon_cons(hist, ctime, rchild(formula))
	elif (ftype(formula) == OR_T):
		dprint("got an or, returning both", DBG_SMON)
		return smon_cons(hist, ctime, lchild(formula)) or smon_cons(hist, ctime, rchild(formula))
	elif (ftype(formula) == IMPLIES_T):
		dprint("got an implies, returning both", DBG_SMON)
		return not smon_cons(hist, ctime, lchild(formula)) or smon_cons(hist, ctime, rchild(formula))
	elif (ftype(formula) == EVENT_T): 
		dprint("got an eventually at %d, checking structure" % (ctime,), DBG_SMON)
		l = ctime + formula[1]
		h = ctime + formula[2]

		dprint("checking range: [%d, %d]" % (l,h), DBG_SMON)
		end = None
		for i in sorted(hist, reverse=True):
			itime = tau(hist,i)
			dprint("eventually checking %d" % (i,), DBG_SMON)
			dprint("checking intersection of (%d,%d) and (%s,%s)"%(l,h,itime,end), DBG_SMON)
			isect_start = int_intersect_start((l,h), (itime, end))
			dprint("int_start is %s" % (isect_start,), DBG_SMON)
			if (int_intersect_exists((l,h), (itime,end)) 
				and smon_cons(hist, isect_start, rchild(formula))):
				return True
			end = tau(hist, i)
		# didn't find the event in the bounds
		return False
	elif (ftype(formula) == ALWAYS_T):
		dprint("got an always at %d, checking structure" %(ctime,), DBG_SMON)
		l = ctime + formula[1]
		h = ctime + formula[2]

		dprint("checking range: [%d, %d]" % (l,h), DBG_SMON)
		histIntE = None
		histIntS = None
		for i in sorted(hist, reverse=True):
			dprint("always checking %d" % (i,), DBG_SMON)
			dprint("updating always intervals: (%s, %s)" % (histIntS, histIntE), DBG_SMON)
			if (smon_cons(hist, tau(hist,i), rchild(formula))):
				histIntS = tau(hist, i)
			else:
				histIntE = tau(hist, i)
			dprint("checking always intervals: (%s, %s)" % (histIntS, histIntE), DBG_SMON)
			if (histIntS is not None and (histIntS <= histIntE or histIntE is None) 
				and int_subset((l,h), (histIntS, histIntE))):
				return True
		# didn't find the event in the bounds
		dprint("FINISHED ALWAYS, DIDN'T FIND ANYTHING", DBG_SMON)
		return False
	elif (ftype(formula) == UNTIL_T): 
		dprint("got an always, checking structure", DBG_SMON)
		l = ctime + formula[1]
		h = ctime + formula[2]
		dprint("checking range: %d - %d" % (l, h), DBG_SMON)

		# First check P2 occured (and save when it did)
		end = None
		untilend = None
		for i in sorted(hist, reverse=True):
			#if (tau(i) < l and before is None):
			if (int_intersect_exists((l,h), (tau(hist, i),end)) 
				and smon_cons(hist, hist[i], rchild(formula))):
				untilend = tau(hist, i)
			end = tau(hist, i)
		if untilend is None:
			return False
		dprint("Got Until end %s" % (end,), DBG_SMON)
		# Now check P1
		l = ctime
		h = untilend
		histIntE = None
		histIntS = None
		for i in sorted(hist, reverse=True):
			if (smon_cons(hist, hist[i], rchild(formula))):
				histIntS = tau(hist, i)
			else:
				histIntE = tau(hist, i)
			if (histIntS <= histIntE and int_subset((l,h), (histIntS, histIntE))):
				return True
		# didn't find the event in the bounds
		dprint("Until invariant not satisfied for [%d,%d]" % (l, h), DBG_SMON)
		return False
	elif (ftype(formula) == PEVENT_T):
		dprint("got a pevent, checking structure", DBG_SMON)
		l = ctime-formula[2]
		h = ctime-formula[1]

		dprint("checking range: [%d, %d]" % (l,h), DBG_SMON)
		end = None
		for i in sorted(hist, reverse=True):
			#if (tau(i) < l and before is None):
			if (int_intersect_exists((l,h), (tau(hist, i),end)) 
				and smon_cons(hist, hist[i], rchild(formula))):
				return True
			end = tau(hist, i)
		# didn't find the event in the bounds
		return False
	elif (ftype(formula) == PALWAYS_T):
		dprint("got a palways, checking structure", DBG_SMON)
		l = ctime-formula[2]
		h = ctime-formula[1]

		dprint("checking range: [%d, %d]" % (l,h), DBG_SMON)
		histIntE = None
		histIntS = None
		for i in sorted(hist, reverse=True):
			if (smon_cons(hist, hist[i], rchild(formula))):
				histIntS = tau(hist, i)
			else:
				histIntE = tau(hist, i)
			if (histIntS <= histIntE and int_subset((l,h), (histIntS, histIntE))):
				return True
		# didn't find the event in the bounds
		return False
	elif (ftype(formula) == SINCE_T):
		dprint("got a since, checking structure", DBG_SMON)
		l = ctime-formula[2]
		h = ctime-formula[1]
		# check if P2 happened
		dprint("checking range: [%d, %d]" % (l,h), DBG_SMON)
		end = None
		sinceend = None
		for i in sorted(hist, reverse=True):
			#if (tau(hist, i) < l and before is None):
			if (int_intersect_exists((l,h), (tau(hist, i),end)) 
				and smon_cons(hist, hist[i], rchild(formula))):
				sinceend = tau(hist, i)
			end = tau(hist, i)
		if sinceend is None:
			return False
		dprint("Got Since start %s" % (start,), DBG_SMON)
		# Now check P1
		l = sinceend
		h = ctime
		dprint("checking range: [%d, %d]" % (l,h), DBG_SMON)
		histIntE = None
		histIntS = None
		for i in sorted(hist, reverse=True):
			if (smon_cons(hist, hist[i], rchild(formula))):
				histIntS = tau(hist, i)
			else:
				histIntE = tau(hist, i)
			if (histIntS <= histIntE 
				and int_subset((l,h), (histIntS, histIntE))):
				return True
		# didn't find the event in the bounds
		dprint("Since invariant not satisfied for [%d,%d]" % (checkStart, checkEnd), DBG_SMON)
		return False
	# bad/unknown formula type
	else:
		return INVALID_T
## END smon_cons

def mon_cons_ST(inFile, inFormula, traceOrder):
	# some algorithm local variables
	cstate = {}
	Struct = {}
	cHistory = {}
	eptr = 0
	cptr = 0
	# build struct and save delay
	build_structure(Struct, inFormula)
	D = delay(inFormula)
	# wait for new data...
	for line in inFile:
			dprint("###### New event received")
			updateState(cstate, traceOrder, line)
			cHistory[cptr] = cstate.copy()
			print "AT STATE %s" % (cstate,)
			incr_struct(Struct, cstate)

			while (tau(cHistory, cptr) - tau(cHistory, eptr) >= D):
				dprint("@@@@ evaluating step: %d" % (eptr,))
				mon = smon_cons_ST(Struct, cHistory[eptr], inFormula)
				if (not mon):
					print "VIOLATION FOUND"
					sys.exit(1)
				print "==== formula value at %d: %s" % (eptr, mon)
				eptr = eptr + 1
			## clean old history out
			## structs are cleaned automatically at update
			for i in cHistory.copy():
				if (tau(cHistory, cptr) - tau(cHistory, i) > D):
					cHistory.pop(i)
					print "removed %d from History" % (i,)
			cptr = cptr + 1
## END mon_cons_ST()


def smon_cons_ST(Struct, cstate, formula):
	ctime = cstate["time"]
	if (ftype(formula) == EXP_T):
		dprint("got an exp, returning", DBG_SMON)
		return smon_cons_ST(Struct, cstate, rchild(formula))
	elif (ftype(formula) == PROP_T):
		dprint("got a prop, returning", DBG_SMON)
		return cstate[rchild(formula)]
	elif (ftype(formula) == NPROP_T):
		dprint("got an nprop", DBG_SMON)
		return not cstate[rchild(formula)]
	elif (ftype(formula) == NOT_T):
		dprint("got a notprop", DBG_SMON)
		return not smon_cons_ST(Struct, cstate, rchild(formula))
	elif (ftype(formula) == AND_T):
		dprint("got an and, returning both", DBG_SMON)
		return smon_cons_ST(Struct, cstate, lchild(formula)) and smon_cons_ST(Struct, cstate, rchild(formula))
	elif (ftype(formula) == OR_T):
		dprint("got an or, returning both", DBG_SMON)
		return smon_cons_ST(Struct, cstate, lchild(formula)) or smon_cons_ST(Struct, cstate, rchild(formula))
	elif (ftype(formula) == IMPLIES_T):
		dprint("got an implies, returning both", DBG_SMON)
		return not smon_cons_ST(Struct, cstate, lchild(formula)) or smon_cons_ST(Struct, cstate, rchild(formula))
	elif (ftype(formula) == EVENT_T): 
		dprint("got an eventually, checking structure", DBG_SMON)
		l = ctime + formula[1]
		h = ctime + formula[2]

		dprint("checking range: [%d, %d]" % (l,h), DBG_SMON)
		intlist = Struct[get_tags(formula)][-1]
		for i in intlist:
			if int_intersect_exists((l,h), i):
				return True
		# didn't find the event in the bounds
		return False
	elif (ftype(formula) == ALWAYS_T):
		dprint("got an always, checking structure", DBG_SMON)
		l = ctime + formula[1]
		h = ctime + formula[2]
		intlist = Struct[get_tags(formula)][-1]
		for i in intlist:
			if int_subset((l,h), i):
				return True
		# no interval contains invar
		return False
		pass
	elif (ftype(formula) == UNTIL_T): 
		dprint("got an always, checking structure", DBG_SMON)
		l = ctime + formula[1]
		h = ctime + formula[2]
		dprint("checking range: %d - %d" % (l, h), DBG_SMON)
		tags = get_tags(formula)

		# First check P2 occured (and save when it did)
		intlist = Struct[tags[1]][-1]
		end = None
		for i in intlist:
			# check intersection of intervals (including possibly unfinished right bound)
			if (int_intersect_exists((l,h), i)):
				end = max(l, i[0])
		if (end is None):
			return False		## TODO: return true if weak Since, need to decide
		dprint("Got Until end %s" % (end,), DBG_SMON)
		# Now check P1
		l = ctime
		h = end
		intlist = Struct[tags[0]][-1]						# get list for P1
		# and check P1 as a PALWAYS since P2 occured
		for i in intlist:
			if (int_subset((l,h), i)):
				return True
		dprint("Until invariant not satisfied for [%d,%d]" % (l, h), DBG_SMON)
		return False
	elif (ftype(formula) == PEVENT_T):
		dprint("got a pevent, checking structure", DBG_SMON)
		checkStart = ctime-formula[2]
		checkEnd = ctime-formula[1]

		dprint("checking range: [%d, %d]" % (checkStart, checkEnd), DBG_SMON)
		intlist = Struct[get_tags(formula)][-1]
		for i in intlist:
			# check intersection of intervals (including possibly unfinished right bound)
			# saved intervals need to be [l,h) so we don't return <<h,x>> satisfied by [l,h)
			if ((isopen_interval(i) or checkStart < i[1]) 
				and i[0] <= checkEnd):
				return True
		# didn't find the event in the bounds
		return False
	elif (ftype(formula) == PALWAYS_T):
		dprint("got a palways, checking structure", DBG_SMON)
		checkStart = ctime-formula[2]
		checkEnd = ctime-formula[1]

		dprint("checking range: %d - %d" % (checkStart, checkEnd), DBG_SMON)
		#dprint("Checking range: %s" % (checkRange,))
		intlist = Struct[get_tags(formula)][-1]
		for i in intlist:
			if (i[0] <= checkStart and 
				(isopen_interval(i) or checkEnd < i[1])):
				# start is in interval, and either open or interval contains end
				return True
		# no interval containing invariant
		return False
	elif (ftype(formula) == SINCE_T):
		dprint("got a since, checking structure", DBG_SMON)
		checkStart = ctime-formula[2]
		checkEnd = ctime-formula[1]
		dprint("checking range: %d - %d" % (checkStart, checkEnd), DBG_SMON)
		tags = get_tags(formula)
		# First, check that P2 did occur (and find when it first did)
		intlist = Struct[tags[1]][-1]
		start = None
		for i in intlist:
			# check intersection of intervals (including possibly unfinished right bound)
			if ((isopen_interval(i) or checkStart < i[1]) 
				and i[0] <= checkEnd):
				start = max(checkStart, i[0])
		if (start is None):
			return False		## TODO: return true if weak Since, need to decide
		dprint("Got Since start %s" % (start,), DBG_SMON)
		# Now check P1
		checkStart = start
		checkEnd = ctime
		intlist = Struct[tags[0]][-1]						# get list for P1
		# and check P1 as a PALWAYS since P2 occured
		for i in intlist:
			if (i[0] <= checkStart and 
				(isopen_interval(i) or checkEnd < i[1])):
				# start is in interval, and either open or interval contains end
				return True
		dprint("Since invariant not satisfied for [%d,%d]" % (checkStart, checkEnd), DBG_SMON)
		return False
	else:
		return INVALID_T
## END smon_cons_ST

############ Main/Monitor helpers ####
######################################
def updateState(cstate, traceOrder, line):
	vals = line.strip().split(delim)
	for i in range(0, len(vals)):
		print "%d| Updating %s to %s" % (i, traceOrder[i], vals[i])
		cstate[traceOrder[i]] = int(vals[i])
## start with no future temporal properties
def tau(hist, i):
	return hist[i]["time"]
		
def getState(hist, time):
	for i in sorted(hist, reverse=True):
		if (tau(hist,i) <= time):
			return (i,hist[i])

def ftype(formula):
	cNode = formula[0]
	if (cNode == "exp"):
		return EXP_T
	elif (cNode == "prop"):
		return PROP_T
	elif (cNode == "nprop"):
		return NPROP_T
	elif (cNode == "notprop"):
		return NOT_T
	elif (cNode == "andprop"):
		return AND_T
	elif (cNode == "orprop"):
		return OR_T
	elif (cNode == "impprop"):
		return IMPLIES_T
	elif (cNode == "eventprop"):
		return EVENT_T
	elif (cNode == "alwaysprop"):
		return ALWAYS_T
	elif (cNode == "untilprop"):
		return UNTIL_T
	#elif (cNode == "peventprop"):
	elif (cNode == "onceprop"):
		return PEVENT_T
	elif (cNode == "palwaysprop"):
		return PALWAYS_T
	elif (cNode == "sinceprop"):
		return SINCE_T
	else:
		return INVALID_T

def substitute(Struct, cstate, formula):
	if (ftype(formula) == EXP_T):
		return [formula[0], substitute(Struct, cstate, formula[1])]
	elif (ftype(formula) == PROP_T):
		return cstate[formula[1]]
	elif (ftype(formula) == NPROP_T):
		return not cstate[formula[1]]
	elif (ftype(formula) == NOT_T):
		return ['notprop', substitute(Struct, cstate, formula[1])]
	elif (ftype(formula) == AND_T):
		return ['andprop', substitute(Struct, cstate, formula[1]), substitute(Struct, cstate, formula[2])]
	elif (ftype(formula) == OR_T):
		return ['orprop', substitute(Struct, cstate, formula[1]), substitute(Struct, cstate, formula[2])]
	elif (ftype(formula) == IMPLIES_T):
		return ['impprop', substitute(Struct, cstate, formula[1]), substitute(Struct, cstate, formula[2])]
	elif (ftype(formula) == EVENT_T): 
		## Fill in with check and return formula if not sure yet
		return formula
	elif (ftype(formula) == ALWAYS_T):
		## Fill in with check and return formula if not sure yet
		return formula
	elif (ftype(formula) == UNTIL_T): 
		## Fill in with check and return formula if not sure yet
		return formula
	elif (ftype(formula) == PEVENT_T):
		return history_lookup_PE(Struct, cstate, formula)
	elif (ftype(formula) == PALWAYS_T):
		return history_lookup_PA(Struct, cstate, formula)
	elif (ftype(formula) == SINCE_T):
		return history_lookup_S(Struct, cstate, formula)
	else:
		return INVALID_T

def history_lookup_PE(Struct, cstate, formula):
	dprint("history lookup for pevent, checking structure", DBG_HISTORY)
	ctime = cstate["time"]
	checkStart = ctime-formula[2]
	checkEnd = ctime-formula[1]

	dprint("checking range: [%d, %d]" % (checkStart, checkEnd), DBG_HISTORY)
	intlist = Struct[get_tags(formula)][-1]
	for i in intlist:
		# check intersection of intervals (including possibly unfinished right bound)
		# saved intervals need to be [l,h) so we don't return <<h,x>> satisfied by [l,h)
		if ((isopen_interval(i) or checkStart < i[1]) 
			and i[0] <= checkEnd):
			return True
	# didn't find the event in the bounds
	return False

def history_lookup_PA(Struct, cstate, formula):
	dprint("history lookup for palways, checking structure", DBG_HISTORY)
	ctime = cstate["time"]
	checkStart = ctime-formula[2]
	checkEnd = ctime-formula[1]

	dprint("checking range: %d - %d" % (checkStart, checkEnd), DBG_HISTORY)
	#dprint("Checking range: %s" % (checkRange,))
	intlist = Struct[get_tags(formula)][-1]
	for i in intlist:
		if (i[0] <= checkStart and 
			(isopen_interval(i) or checkEnd < i[1])):
			# start is in interval, and either open or interval contains end
			return True
	# no interval containing invariant
	return False

def history_lookup_S(Struct, cstate, formula):
	dprint("history lookup for since, checking structure", DBG_HISTORY)
	ctime = cstate["time"]
	checkStart = ctime-formula[2]
	checkEnd = ctime-formula[1]
	dprint("checking range: %d - %d" % (checkStart, checkEnd), DBG_HISTORY)
	tags = get_tags(formula)
	# First, check that P2 did occur (and find when it first did)
	intlist = Struct[tags[1]][-1]
	start = None
	for i in intlist:
		# check intersection of intervals (including possibly unfinished right bound)
		if ((isopen_interval(i) or checkStart < i[1]) 
			and i[0] <= checkEnd):
			start = max(checkStart, i[0])
	if (start is None):
		return False		## TODO: return true if weak Since, need to decide
	dprint("Got Since start %s" % (start,), DBG_HISTORY)
	# Now check P1
	checkStart = start
	checkEnd = ctime
	intlist = Struct[tags[0]][-1]						# get list for P1
	# and check P1 as a PALWAYS since P2 occured
	for i in intlist:
		if (i[0] <= checkStart and 
			(isopen_interval(i) or checkEnd < i[1])):
			# start is in interval, and either open or interval contains end
			return True
	dprint("Since invariant not satisfied for [%d,%d]" % (checkStart, checkEnd), DBG_HISTORY)
	return False

def history_lookup(tag1, tag2):
	return 'history2'

#######################################
##### Delay Functions
#######################################
def delay(formula):
	if (ftype(formula) == EXP_T):
		return delay(rchild(formula))
	elif (ftype(formula) == PROP_T):
		return 0
	elif (ftype(formula) == NPROP_T):
		return 0
	elif (ftype(formula) == NOT_T):
		return delay(rchild(formula))
	elif (ftype(formula) == AND_T):
		return max(delay(lchild(formula)),delay(rchild(formula)))
	elif (ftype(formula) == OR_T):
		return max(delay(lchild(formula)),delay(rchild(formula)))
	elif (ftype(formula) == IMPLIES_T):
		return max(delay(lchild(formula)),delay(rchild(formula)))
	elif (ftype(formula) == EVENT_T): 
		return hbound(formula) + delay(rchild(formula))
	elif (ftype(formula) == ALWAYS_T):
		return hbound(formula) + delay(rchild(formula))
	elif (ftype(formula) == UNTIL_T): 
		return hbound(formula) + max(delay(untilP1(formula)),delay(untilP2(formula)))
	elif (ftype(formula) == PALWAYS_T):
		return delay(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		return delay(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		return max(delay(untilP1(formula)),delay(untilP2(formula)))
	else:
		dprint("DELAY ERROR: Got unmatched AST node while building");
		return None
	# shouldn't get here
	return None


def past_delay(formula):
	if (ftype(formula) == EXP_T):
		return delay(rchild(formula))
	elif (ftype(formula) == PROP_T):
		return 0
	elif (ftype(formula) == NPROP_T):
		return 0
	elif (ftype(formula) == NOT_T):
		return delay(rchild(formula))
	elif (ftype(formula) == AND_T):
		return max(delay(lchild(formula)),delay(rchild(formula)))
	elif (ftype(formula) == OR_T):
		return max(delay(lchild(formula)),delay(rchild(formula)))
	elif (ftype(formula) == IMPLIES_T):
		return max(delay(lchild(formula)),delay(rchild(formula)))
	elif (ftype(formula) == EVENT_T): 
		return delay(rchild(formula))
	elif (ftype(formula) == ALWAYS_T):
		return delay(rchild(formula))
	elif (ftype(formula) == UNTIL_T): 
		return max(delay(untilP1(formula)),delay(untilP2(formula)))
	elif (ftype(formula) == PALWAYS_T):
		return hbound(formula) + delay(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		return hbound(formula) + delay(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		return hbound(formula) + max(delay(untilP1(formula)),delay(untilP2(formula)))
	else:
		dprint("PAST-DELAY ERROR: Got unmatched AST node while building");
		return None
	# shouldn't get here
	return None
########################################
##### History Structures
#######################################

def build_structure(Struct, formula, extbound=(0,0)):
	if (ftype(formula) == EXP_T):
		dprint("BUILDING: got an exp, recursing", DBG_STRUCT)
		return build_structure(Struct, rchild(formula))
	elif (ftype(formula) == PROP_T):
		dprint("BUILDING: got a prop, returning", DBG_STRUCT)
		return True
	elif (ftype(formula) == NPROP_T):
		dprint("BUILDING: got an nprop, returning", DBG_STRUCT)
		return True
	elif (ftype(formula) == NOT_T):
		dprint("BUILDING: got a not, recursing", DBG_STRUCT)
		build_structure(Struct, rchild(formula))
		return True
	elif (ftype(formula) == AND_T):
		dprint("BUILDING: got an and, recursing both", DBG_STRUCT)
		build_structure(Struct, lchild(formula)) 
		build_structure(Struct, rchild(formula))
		return True
	elif (ftype(formula) == OR_T):
		dprint("BUILDING: got an or, recursing both", DBG_STRUCT)
		build_structure(Struct, lchild(formula))
		build_structure(Struct, rchild(formula))
		return True
	elif (ftype(formula) == IMPLIES_T):
		dprint("BUILDING: got an implies, recursing both", DBG_STRUCT)
		build_structure(Struct, lchild(formula)) 
		build_structure(Struct, rchild(formula))
		return True
	elif (ftype(formula) == EVENT_T): 
		dprint("BUILDING: got an eventually, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		add_struct(Struct, cTag, (formula[1], formula[2]+extbound[1]), rchild(formula))
		return build_structure(Struct, rchild(formula), extbound=(formula[1], formula[2]))
	elif (ftype(formula) == ALWAYS_T):
		dprint("BUILDING: got an always, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		add_struct(Struct, cTag, (formula[1], formula[2]+extbound[1]), rchild(formula))
		return build_structure(Struct, rchild(formula), extbound=(formula[1], formula[2]))
	elif (ftype(formula) == UNTIL_T): 
		dprint("BUILDING: got an until, ADDING STRUCT and recursing both", DBG_STRUCT)
		# Tags get put into formula[2] so tagging P2 then P1 makes formula into
		# [bound, bound, tagP1, tagP2, P1, P2]
		# do P2
		cTag = tag_formula(formula)
		add_struct(Struct, cTag, (formula[1], formula[2]+extbound[1]), untilP2(formula))
		# do P1
		cTag = tag_formula(formula)
		add_struct(Struct, cTag, (formula[1], formula[2]+extbound[1]), untilP1(formula))
		build_structure(Struct, untilP1(formula), extbound=(formula[1],formula[2]))
		build_structure(Struct, untilP2(formula), extbound=(formula[1],formula[2]))
		return True
	elif (ftype(formula) == PALWAYS_T):
		dprint("BUILDING: got a past always, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		add_struct(Struct, cTag, (formula[1], formula[2]+extbound[1]), rchild(formula))
		return build_structure(Struct, rchild(formula), extbound=(formula[1], formula[2]))
	elif (ftype(formula) == PEVENT_T):
		nestprint("BUILDING: got a past eventually, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		add_struct(Struct, cTag, (formula[1], formula[2]+extbound[1]), rchild(formula))
		return build_structure(Struct, rchild(formula), extbound=(formula[1], formula[2]))
	elif (ftype(formula) == SINCE_T):
		nestprint("BUILDING: got a since, ADDING BOTH STRUCTS and recursing both", DBG_STRUCT)
		# Tags get put into formula[2] so tagging P2 then P1 makes formula into
		# [bound, bound, tagP1, tagP2, P1, P2]
		# do P2
		cTag = tag_formula(formula)
		add_struct(Struct, cTag, (formula[1], formula[2]+extbound[1]), untilP2(formula))
		# do P1
		cTag = tag_formula(formula)
		add_struct(Struct, cTag, (formula[1], formula[2]+extbound[1]), untilP1(formula))
		build_structure(Struct, untilP1(formula), extbound=(formula[1],formula[2]))
		build_structure(Struct, untilP2(formula), extbound=(formula[1],formula[2]))
		return True
	else:
		nestprint("BUILDING ERROR: Got unmatched AST node while building", DBG_STRUCT);
		return False
	# shouldn't get here
	return False

def add_struct(Struct, tag, bounds, formula):
	newItem = [tag, formula, bounds[1], []]
	# Add interval that fills entire past bound 
	newItem[-1].append(new_interval(0-bounds[1]))
	Struct[tag] = newItem
	return

# add a tag to past time formula
def tag_formula(formula):
	global sTag
	formula.insert(3, sTag)
	sTag = sTag + 1
	return (sTag - 1)

# get tag of past-time formula
def get_tags(formula):
	#print "GET_TAGS OF %s" % (formula,)
	if (len(formula) == 5):
		return formula[3]
	elif (len(formula) == 7):
		return (formula[3], formula[4])
	return -1

def incr_struct(Struct, cstate):
	ctime = cstate["time"]
	taglist = list(Struct.keys())
	taglist.sort()
	taglist.reverse()
	# must check in order due to nested dependencies
	for t in taglist:
		cStruct = Struct[t]
		#print "Incrementing %s" % (cStruct,)
		cIntervalOpen = False
		if (len(cStruct[-1]) > 0):
			last_int = cStruct[-1][-1]	# get most recent interval from interval list
			cIntervalOpen = isopen_interval(last_int)	
		# else cIntervalOpen stays false
		if smon_cons_ST(Struct, cstate, cStruct[1]):
			# if not in an open interval, start a new one
			# if we are in an existing open interval, then we don't need to do anything
			if (not cIntervalOpen):
				cStruct[-1].append(new_interval(ctime))
		else: # Formula is not satisfied at current time
			if (cIntervalOpen):
				# close last interval in place
				cStruct[-1][-1] = close_interval(last_int, ctime)	

		# remove unneeded values from struct list
		intlist = cStruct[-1]
		for i in (intlist[:]):
			# remove any closed intervals that end earlier than our max look-back
			if (not isopen_interval(i) and (i[1] < ctime-cStruct[2])):
				intlist.remove(i)
		print "Incremented and cleaned: %s" % (cStruct,)
	return

# start a new interval tuple
def new_interval(start):
	return (start, None)
# end an existing interval tuple
def close_interval(interval, end):
	return (interval[0], end)
# check if interval is open (infinite)
def isopen_interval(interval):
	return interval[1] is None
# check if a value is in the interval
def in_interval(i, interval):
	# could cut down to i>=i[0] and (i[1] is None or i <= i[1])
	if (interval[1] is None):
		return i >= interval[0]
	else:
		return i >= interval[0] and i < interval[1]
# make access to intervals a little more clear
def iEnd(interval):
	return interval[1]
def iStart(interval):
	return interval[0]
# order of intervals matters, only checking infinite on history
# do the intervals intersect?
def int_intersect_exists(test_i, history_i):
	if ((isopen_interval(history_i) or iStart(test_i) <= iEnd(history_i)) 
		and iStart(history_i) < iEnd(test_i)):
		return True
	else:
		return False
# get start point of intersection
def int_intersect_start(test_i, history_i):
	if int_intersect_exists(test_i, history_i):
		return max(iStart(test_i), iStart(history_i))
	return None
# is test subset of history
def int_subset(test_i, history_i):
	if ((iStart(history_i) <= iStart(test_i)) and
		(isopen_interval(history_i) or iEnd(test_i) < iEnd(history_i))):
		return True
	return False
#### Utilities
######################################
def dprint(string, lvl=0xFF):
#	print "DPRINT %s %d" % (string, lvl)
	if (DBG_MASK & lvl):
		print string

#def dprint(string, lvl):
#	if (DBG_MASK & DBG_LEVEL):
#		print string

def nestprint(string):
	print pphead,
	print string

########## Formula Utilities
# get leftmost child
def lchild(formula): 
	return formula[1]
# get rightmost child
def rchild(formula): 
	return formula[-1]
## formula children for (p1 U_i p2)
def untilP1(formula):
	return formula[-2]
def untilP2(formula):
	return formula[-1]
# get lower temporal bound
def lbound(formula):
	return formula[1]
# get higher temporal bound
def hbound(formula):
	return formula[2]
#### Python stuff - set main and catch ^C
#########################################
def signal_handler(signal, frame):
	print "Caught ctrl-c, exiting..."
	sys.exit(1)

if __name__ == "__main__":
	main()
