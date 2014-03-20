#!/usr/bin/python
##
##
## @author Aaron Kane
##
## Starting a clean nested residual monitor file. 
##	 Full file is getting a little crowded

import sys
import signal
import monIntervals as monI 

## Some constants
EXP_T, PROP_T, NPROP_T, NOT_T, AND_T, OR_T, IMPLIES_T, EVENT_T, ALWAYS_T, UNTIL_T, PALWAYS_T, PEVENT_T, SINCE_T, VALUE_T, INVALID_T = range(15)

## debug constants
DBG_ERROR = 0x01
DBG_STRUCT = 0x02
DBG_SMON = 0x04
DBG_STATE = 0x08
DBG_MASK = DBG_ERROR | DBG_STRUCT | DBG_SMON | DBG_STATE 
#DBG_MASK = DBG_ERROR
DEBUG = True
# global constants
PERIOD = 10
delim = ','
sTag = 0


###### Keeping this script compatible with resMonitor for now
def main():
	# do setup
	#### Handle input parameters
	##############################
	algChoose = 0
	if len(sys.argv) > 3:
		PERIOD = int(sys.argv[3])
	if len(sys.argv) > 2:
		inFormula = eval(sys.argv[1])	# DANGEROUS. DON'T PASS ME ARBITRARY CODE
		inFile = open(sys.argv[2], "r")
	else:
		print "Bad Usage: python monitor.py <formula> <tracefile> [period]"
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
	print "############## Beginning monitor algorithm: residue"
	mon_cons_ST_per(inFile, inFormula, traceOrder)
############# END MAIN ############
##################################

def mon_cons_ST_per(inFile, inFormula, traceOrder):
	# some algorithm local variables
	cstate = {}
	Struct = {}
	cHistory = {}
	eptr = 0
	cptr = 0
	# build struct and save delay
	build_structure(Struct, inFormula)
	dprint("Using Struct %s" % (Struct,), DBG_STRUCT)
	D = delay(inFormula)
	DP = past_delay(inFormula)
	# wait for new data...
	for line in inFile:
			dprint("###### New event received", DBG_SMON)
			updateState(cstate, traceOrder, line)
			cHistory[cptr] = cstate.copy()
			dprint("AT STATE %s" % (cstate,), DBG_SMON)
			incr_struct_per(Struct, cHistory, tau(cHistory, cptr))

			while (eptr <= cptr and tau(cHistory, cptr) - tau(cHistory, eptr) >= D):
				dprint("@@@@ evaluating step: %d" % (eptr,), DBG_SMON)
				mon = smon_cons_ST_per(Struct, cHistory, tau(cHistory, eptr), inFormula)
				if (not mon):
					print "VIOLATION FOUND AT TIME %s@%s" % (tau(cHistory, eptr), tau(cHistory, cptr))
					sys.exit(1)
				dprint("==== formula value at %d: %s" % (eptr, mon), DBG_SMON)
				eptr = eptr + 1
			## clean old history out
			## structs are cleaned automatically at update
			for i in cHistory.copy():
				if (tau(cHistory, cptr) - tau(cHistory, i) > max(D,DP)):
					cHistory.pop(i)
					dprint("removed %d from History" % (i,), DBG_SMON)
			cptr = cptr + 1
## END mon_cons_ST()

def smon_cons_ST_per(Struct, hist, ctime, formula):
	(sid,cstate) = getState(hist, ctime)
	if (ftype(formula) == EXP_T):
		dprint("got an exp, returning", DBG_SMON)
		return smon_cons_ST_per(Struct, hist, ctime, rchild(formula))
	elif (ftype(formula) == PROP_T):
		dprint("got a prop, returning", DBG_SMON)
		if (cstate[rchild(formula)]):
			return True
		else:
			return False
	elif (ftype(formula) == NPROP_T):
		dprint("got an nprop", DBG_SMON)
		if (cstate[rchild(formula)]):
			return False
		else:
			return True
	elif (ftype(formula) == NOT_T):
		dprint("got a notprop", DBG_SMON)
		return not smon_cons_ST_per(Struct, hist, ctime, rchild(formula))
	elif (ftype(formula) == AND_T):
		dprint("got an and, returning both", DBG_SMON)
		return smon_cons_ST_per(Struct, hist, ctime, lchild(formula)) and smon_cons_ST_per(Struct, hist, ctime, rchild(formula))
	elif (ftype(formula) == OR_T):
		dprint("got an or, returning both", DBG_SMON)
		return smon_cons_ST_per(Struct, hist, ctime, lchild(formula)) or smon_cons_ST_per(Struct, hist, ctime, rchild(formula))
	elif (ftype(formula) == IMPLIES_T):
		dprint("got an implies, returning both", DBG_SMON)
		return not smon_cons_ST_per(Struct, hist, ctime, lchild(formula)) or smon_cons_ST_per(Struct, hist, ctime, rchild(formula))
	elif (ftype(formula) == EVENT_T): 
		dprint("got an eventually at %d, checking structure" % (ctime,), DBG_SMON)
		l = ctime + lbound(formula)
		h = ctime + hbound(formula)
		# check structure for existance
		intlist = Struct[get_tags(formula)][-1]
		for i in intlist:
			if (int_closed_intersect_exists((l,h),i)):
				return True
		# didn't find formula
		return False
	elif (ftype(formula) == ALWAYS_T):
		dprint("got an always at %d, checking structure" %(ctime,), DBG_SMON)
		l = ctime + lbound(formula)
		h = ctime + hbound(formula)
		dprint("checking range: [%d, %d]" % (l,h), DBG_SMON)
		# check structure for interval
		intlist = Struct[get_tags(formula)][-1]
		for i in intlist:
			if (int_closed_subset((l,h),i)):
				return True
		# no existing interval, so fails
		return False
	elif (ftype(formula) == UNTIL_T): 
		dprint("got an always, checking structure", DBG_SMON)
		l = ctime + lbound(formula)
		h = ctime + hbound(formula)
		tags = get_tags(formula)
		dprint("checking range: %d - %d" % (l, h), DBG_SMON)

		# Check for P2
		end = None
		intlist = Struct[tags[1]][-1]
		for i in intlist:
			if (int_closed_intersect_exists((l,h),i)):
				end = int_closed_intersect_start((l,h),i)
		# no P2 found, so Since is False
		if (end is None):
			return False
		# Now check for P1
		l = ctime 
		h = end
		intlist = Struct[tags[0]][-1]
		for i in intlist:
			if (int_closed_subset((l,h),i)):
				return True
		return False
	elif (ftype(formula) == PEVENT_T):
		l = ctime - hbound(formula)
		h = ctime - lbound(formula)
		
		intlist = Struct[get_tags(formula)][-1]
		for i in intlist:
			if (int_closed_intersect_exists((l,h),i)):
				return True
		return False
	elif (ftype(formula) == PALWAYS_T):
		ctime = cstate["time"]
		l = ctime - hbound(formula)
		h = ctime - lbound(formula)

		intlist = Struct[get_tags(formula)][-1]
		for i in intlist:
			if (int_closed_subset((l,h),i)):
				return True
		return False
	elif (ftype(formula) == SINCE_T):
		ctime = cstate["time"]
		l = ctime - hbound(formula)
		h = ctime - lbound(formula)
		tags = get_tags(formula)

		# Check for P2
		start = None
		intlist = Struct[tags[1]][-1]
		for i in intlist:
			if (int_closed_intersect_exists((l,h),i)):
				start = int_intersect_start((l,h),i)
		# no P2 found, so Since is False
		if (start is None):
			return False
		# Now check for P1
		l = start
		h = ctime
		intlist = Struct[tags[0]][-1]
		for i in intlist:
			if (int_closed_subset((l,h),i)):
				return True
		return False
	else:
		return INVALID_T
## END smon_cons_ST_per
######### Utilities
################################################
def updateState(cstate, traceOrder, line):
	vals = line.strip().split(delim)
	for i in range(0, len(vals)):
		dprint("%d| Updating %s to %s" % (i, traceOrder[i], vals[i]), DBG_STATE)
		cstate[traceOrder[i]] = int(vals[i])

def ftype(formula):
	# check for value (needed for post substitute residual formulas)
	if (formula == 0 or formula == 1 or formula == True or formula == False):
		return VALUE_T
	# then check normal values
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
		dprint("DELAY ERROR: Got unmatched AST node while building", DBG_ERROR);
		return None
	# shouldn't get here
	return None
def past_delay(formula):
	if (ftype(formula) == EXP_T):
		return past_delay(rchild(formula))
	elif (ftype(formula) == PROP_T):
		return 0
	elif (ftype(formula) == NPROP_T):
		return 0
	elif (ftype(formula) == NOT_T):
		return past_delay(rchild(formula))
	elif (ftype(formula) == AND_T):
		return max(past_delay(lchild(formula)),past_delay(rchild(formula)))
	elif (ftype(formula) == OR_T):
		return max(past_delay(lchild(formula)),past_delay(rchild(formula)))
	elif (ftype(formula) == IMPLIES_T):
		return max(past_delay(lchild(formula)),past_delay(rchild(formula)))
	elif (ftype(formula) == EVENT_T): 
		return past_delay(rchild(formula))
	elif (ftype(formula) == ALWAYS_T):
		return past_delay(rchild(formula))
	elif (ftype(formula) == UNTIL_T): 
		return max(past_delay(untilP1(formula)),past_delay(untilP2(formula)))
	elif (ftype(formula) == PALWAYS_T):
		return hbound(formula) + past_delay(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		return hbound(formula) + past_delay(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		return hbound(formula) + max(past_delay(untilP1(formula)),past_delay(untilP2(formula)))
	else:
		dprint("PAST-DELAY ERROR: Got unmatched AST node while building", DBG_ERROR);
		return None
	# shouldn't get here
	return None

########################################
##### History Structures
#######################################

def build_structure(Struct, formula, extbound=0):
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
		d = delay(formula) + extbound
		add_struct(Struct, cTag, d, rchild(formula))
		return build_structure(Struct, rchild(formula), extbound=d)
	elif (ftype(formula) == ALWAYS_T):
		dprint("BUILDING: got an always, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		d = delay(formula) + extbound
		add_struct(Struct, cTag, d, rchild(formula))
		return build_structure(Struct, rchild(formula), extbound=d)
	elif (ftype(formula) == UNTIL_T): 
		dprint("BUILDING: got an until, ADDING STRUCT and recursing both", DBG_STRUCT)
		# Tags get put into formula[2] so tagging P2 then P1 makes formula into
		# [bound, bound, tagP1, tagP2, P1, P2]
		# do P2
		cTag = tag_formula(formula)
		d2 = delay(untilP2(formula)) + extbound
		add_struct(Struct, cTag, d2, untilP2(formula))
		# do P1
		cTag = tag_formula(formula)
		d1 = delay(untilP1(formula)) + extbound
		add_struct(Struct, cTag, d1, untilP1(formula))
		build_structure(Struct, untilP1(formula), extbound=d1)
		build_structure(Struct, untilP2(formula), extbound=d2)
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
		# do P2
		cTag = tag_formula(formula)
		d2 = delay(untilP2(formula)) + extbound
		add_struct(Struct, cTag, d2, untilP2(formula))
		# do P1
		cTag = tag_formula(formula)
		d1 = delay(untilP1(formula)) + extbound
		add_struct(Struct, cTag, d1, untilP1(formula))
		build_structure(Struct, untilP1(formula), extbound=d1)
		build_structure(Struct, untilP2(formula), extbound=d2)
		return True
	else:
		dprint("BUILDING ERROR: Got unmatched AST node while building", DBG_STRUCT);
		return False
	# shouldn't get here
	return False

def add_struct(Struct, tag, delay, formula):
	newItem = [tag, formula, delay, []]
	# Add interval that fills entire past bound 
	#newItem[-1].append(new_interval(0-bounds[1]))
	newItem[-1].append((0-delay, 0))
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

def incr_struct_per(Struct, hist, ctime):
	taglist = list(Struct.keys())
	taglist.sort()
	taglist.reverse()
	# must check in order due to nested dependencies
	for t in taglist:
		cStruct = Struct[t]

		######################################################
		################ Increment structure depending on type
		if (ftype(cStruct[1]) == EVENT_T):
			#print "INC EVENT %s" % cStruct[1]
			h = hbound(cStruct[1])
			l = lbound(cStruct[1])
			checklist = Struct[get_tags(cStruct[1])][-1]

			if (len(checklist) > 0):
				check = checklist[-1]
				#print "updating eventually based on %s" % (check,)
				addInterval((iStart(check)-h, iEnd(check)-l), cStruct[-1])
		elif (ftype(cStruct[1]) == ALWAYS_T):
			h = hbound(cStruct[1])
			l = lbound(cStruct[1])
			checkInt = (ctime - (h-l), ctime)
			checklist = Struct[get_tags(cStruct[1])][-1]

			if (len(checklist) > 0):
				check = checklist[-1]
				#print "checking if %s can be an always %s" % (check, checkInt)
				if (alCheck(check, checkInt)):
					addInterval((iStart(check)-l, iEnd(check)-h), cStruct[-1])
		elif (ftype(cStruct[1]) == UNTIL_T):
			h = hbound(cStruct[1])
			l = lbound(cStruct[1])
			tags = get_tags(cStruct[1])

			checkE = Struct[tags[1]][-1]
			if (len(checkE) > 0):
				lastE = checkE[-1]
				#print "until checking eventually %s" % (lastE,)
				alList = Struct[tags[0]][-1]
				for a in alList:
					#print "checking if %s can be an always %s" % (a, lastE)
					if (int_closed_intersect_exists(a, lastE)):
						start = iStart(a)
						end = min(iEnd(a),iEnd(lastE))
						addInterval((start,end), cStruct[-1])
		else:
			# else cIntervalOpen stays false
			if (smon_cons_ST_per(Struct, hist, ctime, cStruct[1])):
				addInterval((ctime,ctime), cStruct[-1])
			# Else Formula is not satisfied at current time

		#########################################
		###################### Chopping
		# remove unneeded values from struct list
		intlist = cStruct[-1]
		for i in (intlist[:]):
			# remove any closed intervals that end earlier than our max look-back
			if (not isopen_interval(i) and (i[1] < ctime-cStruct[2])):
				intlist.remove(i)
		dprint("Incremented and cleaned: %s" % (cStruct,), DBG_STRUCT)
	return

def alCheck(hist, new):
	lenHist = iEnd(hist) - iStart(hist)
	lenNew = iEnd(new) - iStart(new)
	return (lenHist >= lenNew)

def dprint(string, lvl=0xFF):
#	print "DPRINT %s %d" % (string, lvl)
	if (DBG_MASK & lvl):
		print string

############ INTERVAL UTILITIES

# add interval to list
def addInterval(int, structlist):
	if (len(structlist) > 0):
		last = structlist[-1]
	else:
		last = (None, None)
	#if (iEnd(last) >= iStart(int)):
	if (iStart(int)-PERIOD <= iEnd(last)):
	#if (iEnd(last)+PERIOD >= iStart(int)):
		structlist[-1] = (iStart(last), iEnd(int))
	else:
		structlist.append(int)
# start a new interval tuple
def new_interval(start):
	return (start, None)

# end an existing interval tuple
def close_interval(interval, end):
	return (interval[0], end)

# check if interval is open (infinite)
def isopen_interval(interval):
	return interval[1] is None

# check if i in [l,h]
def in_closed_int(i, interval):
	return (i >= interval[0] and i <= interval[1])

# check if i in [l,h) 
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
	if ((isopen_interval(history_i) or iStart(test_i) < iEnd(history_i)) 
		and iStart(history_i) <= iEnd(test_i)):
		return True
	else:
		return False

def int_closed_intersect_exists(test_i, history_i):
	if ((isopen_interval(history_i) or iStart(test_i) <= iEnd(history_i)) 
		and iStart(history_i) <= iEnd(test_i)):
		return True
	else:
		return False

# get start point of intersection
def int_intersect_start(test_i, history_i):
	if int_intersect_exists(test_i, history_i):
		return max(iStart(test_i), iStart(history_i))
	return None

# get start point of closed intersection
def int_closed_intersect_start(test_i, history_i):
	if int_closed_intersect_exists(test_i, history_i):
		return max(iStart(test_i), iStart(history_i))
	return None

# is test subset of history
def int_subset(test_i, history_i):
	if ((iStart(history_i) <= iStart(test_i)) and
		(isopen_interval(history_i) or iEnd(test_i) < iEnd(history_i))):
		return True
	return False

# check where test_i is a subset of the closed interval history_i
def int_closed_subset(test_i, history_i):
	if ((iStart(history_i) <= iStart(test_i)) and
		(isopen_interval(history_i) or iEnd(test_i) <= iEnd(history_i))):
		return True
	return False

########## Formula Utilities
def tau(hist, i):
	return hist[i]["time"]
		
def getState(hist, time):
	for i in sorted(hist, reverse=True):
		if (tau(hist,i) <= time):
			return (i,hist[i])

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
