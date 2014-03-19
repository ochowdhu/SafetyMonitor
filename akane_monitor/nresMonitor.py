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
DBG_STRUCT = 0x01
DBG_SMON = 0x02
DBG_HISTORY = 0x04
DBG_LEVEL = 0xFF
DBG_MASK = DBG_STRUCT | DBG_HISTORY 
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
	mon_residue(inFile, inFormula, traceOrder)
############# END MAIN ############
##################################

def mon_residue(inFile, inFormula, traceOrder):
	# some algorithm local variables
	cstate = {}
	cHistory = {}
	formulas = []
	Struct = {}
	# build struct and save delay
	D = delay(inFormula)
	DP = past_delay(inFormula)
	build_structure(Struct, inFormula)

	for s in Struct:
		print "%s" % (Struct[s],)
	dprint("Formula delay is %d, %d" % (D,DP))
	# wait for new data...
	for line in inFile:
			dprint("###### New event received")
			updateState(cstate, traceOrder, line)
			incr_struct_res(Struct, cstate)
			#incr_struct(Struct, cstate)

			print "Adding current formula"
			#formulas.append((cstate["time"]+D, future_tag(cstate["time"], inFormula)))
			#formulas.append((cstate["time"], future_tag(cstate["time"], inFormula)))
			formulas.append((cstate["time"], inFormula))
			dprint(formulas)
			print "reducing all formulas"
			for i,f in enumerate(formulas[:]):
				formulas[i] = (f[0], reduce(substitute_per_ag(Struct, cstate, f)))
			dprint(formulas)
			print "removing finished formulas and check violations..."
			# remove any True formulas from the list
			formulas[:] = [f for f in formulas if f[1] != True]
			for i,f in enumerate(formulas[:]):
				if (f[1] == False):
						print "VIOLATION DETECTED AT %s" % (cstate["time"],)
						sys.exit(1)
				else:	# eventually never satisfied
					if (f[0]+D <= cstate["time"]):
						print "VIOLATOR: %s" % (f,)
						print "VIOLATION DETECTED AT %s" % (cstate["time"],)
						sys.exit(1)
	print "finished, trace satisfies formula"
## END mon_residue


def substitute_per_ag(Struct, cstate, formula_entry):
	formtime = formula_entry[0]
	formula = formula_entry[1]
	if (ftype(formula) == EXP_T):
		return [formula[0], substitute_per_ag(Struct, cstate, (formtime, formula[1]))]
	elif (ftype(formula) == VALUE_T):
		return formula
	elif (ftype(formula) == PROP_T):
		#return cstate[formula[1]]
		if (cstate[formula[1]]):
			return True
		else:
			return False
	elif (ftype(formula) == NPROP_T):
		#return not cstate[formula[1]]
		if (cstate[formula[1]]):
			return False
		else:
			return True
	elif (ftype(formula) == NOT_T):
		return ['notprop', substitute_per_ag(Struct, cstate, (formtime, formula[1]))]
	elif (ftype(formula) == AND_T):
		return ['andprop', substitute_per_ag(Struct, cstate, (formtime, formula[1])), substitute_per_ag(Struct, cstate, (formtime,formula[2]))]
	elif (ftype(formula) == OR_T):
		return ['orprop', substitute_per_ag(Struct, cstate, (formtime,formula[1])), substitute_per_ag(Struct, cstate, (formtime, formula[2]))]
	elif (ftype(formula) == IMPLIES_T):
		return ['impprop', substitute_per_ag(Struct, cstate, (formtime,formula[1])), substitute_per_ag(Struct, cstate, (formtime, formula[2]))]
	elif (ftype(formula) == EVENT_T): 
		print "subbing event"
		## Fill in with check and return formula if not sure yet
		l = formula[1] + formtime
		h = formula[2] + formtime
		intlist = Struct[get_tags(formula)][-1]
		for i in intlist:
				if (int_closed_intersect_exists((l,h),i)):
					print "intersect found %s, (%s,%s)"% (i, l, h)
					return True
		if (cstate["time"] > (h + delay(rchild(formula)))):
			return False
		return formula
	elif (ftype(formula) == ALWAYS_T):
		print "subbing always"
		l = formula[1] + formtime
		h = formula[2] + formtime
		intlist = Struct[get_tags(formula)][-1]
		if (in_closed_int(cstate["time"], (l,h))):
			for i in intlist:
				if (int_closed_subset((l,h),i)): 
					if (cstate["time"] >= formula[2]):
						return True
					else:
						return formula
			return False
		elif (cstate["time"] > (h + delay(rchild(formula)))):
			return True
		return formula
	elif (ftype(formula) == UNTIL_T): 
		l = formula[1] + formtime
		h = formula[2] + formtime
		tags = get_tags(formula)

		# check for P2
		end = None
		intlist = Struct[tags[1]][-1]
		for i in intlist:
			if (int_closed_intersect_exists((l,h),i)):
				end = int_closed_intersect_start((l,h),i)
		if (end is None and cstate["time"] > h):
			return False
		elif (end is None):
			return formula

		l = formtime
		h = end
		# check that P1 still going
		intlist = Struct[tags[0]][-1]
		for i in intlist:
			if (int_closed_subset((l,h),i)): 
					return True
		return False
	elif (ftype(formula) == PEVENT_T):
		ctime = cstate["time"]
		l = ctime - hbound(formula)
		h = ctime - lbound(formula)
		
		intlist = Struct[get_tags(formula)][0]
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

def reduce(formula):
	if (ftype(formula) == EXP_T):
		#return [formula[0], reduce(formula[1])]
		return reduce(formula[1])
	elif (ftype(formula) == VALUE_T):
		return formula
	elif (ftype(formula) == PROP_T):
		dprint("shouldn't get here, already sub'd")
		return cstate[formula[1]]
	elif (ftype(formula) == NPROP_T):
		dprint("shouldn't get here, already sub'd")
		return not cstate[formula[1]]
	elif (ftype(formula) == NOT_T):
		child = reduce(formula[1])
		if (ftype(child) == VALUE_T):
			return not child
		else:
			return ['notprop', child]
	elif (ftype(formula) == AND_T):
		child1 = reduce(formula[1])
		child2 = reduce(formula[2])
		if (child1 == False or child == False):
			return False
		elif (child1 == True and child2 == True):
			return True
		else:
			return ['andprop', child1, child2]
	elif (ftype(formula) == OR_T):
		child1 = reduce(formula[1])
		child2 = reduce(formula[2])
		if (child1 == True or child2 == True):
			return True
		elif (child1 == False and child2 == False):
			return False
		else:
			return ['orprop', child1, child2]
	elif (ftype(formula) == IMPLIES_T):
		child1 = reduce(formula[1])
		child2 = reduce(formula[2])
		if (child1 == False or child2 == True):
			return True
		elif (child1 == True and child2 == False):
			return False
		else:
			return ['impprop', child1, child2]
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
		dprint("Can't get here, should've been removed by sub()")
		return INVALID_T
	elif (ftype(formula) == PALWAYS_T):
		dprint("Can't get here, should've been removed by sub()")
		return INVALID_T
	elif (ftype(formula) == SINCE_T):
		dprint("Can't get here, should've been removed by sub()")
		return INVALID_T
	else:
		return INVALID_T

def checkRes(formula):
	print "Checking %s" % (formula,)
	if (ftype(formula) == EXP_T):
		if (formula[1] == True):
			return True
	elif (formula == True):
			return True
	return False

######### Utilities
################################################
def updateState(cstate, traceOrder, line):
	vals = line.strip().split(delim)
	for i in range(0, len(vals)):
		print "%d| Updating %s to %s" % (i, traceOrder[i], vals[i])
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
		dprint("DELAY ERROR: Got unmatched AST node while building");
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
		dprint("PAST-DELAY ERROR: Got unmatched AST node while building");
		return None
	# shouldn't get here
	return None

########################################
##### History Structures
#######################################

def build_structure(Struct, formula, extbound=0):
	print "current struct is %s" % (Struct,)
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

def incr_struct_res(Struct, cstate):
	ctime = cstate["time"]
	taglist = list(Struct.keys())
	taglist.sort()
	taglist.reverse()
	# must check in order due to nested dependencies
	for t in taglist:
		cStruct = Struct[t]
		#print "Incrementing %s" % (cStruct,)
		#cIntervalOpen = False
		if (len(cStruct[-1]) > 0):
			last_int = cStruct[-1][-1]	# get most recent interval from interval list
		#	cIntervalOpen = isopen_interval(last_int)	

		#subform = substitute_per_ag(Struct, cstate, (ctime, cStruct[1]))
		######################################################
		################ Increment structure depending on type
		if (ftype(cStruct[1]) == EVENT_T):
			#print "INC EVENT %s" % cStruct[1]
			h = hbound(cStruct[1])
			l = lbound(cStruct[1])
			checklist = Struct[get_tags(cStruct[1])][-1]

			if (len(checklist) > 0):
				check = checklist[-1]
				print "updating eventually based on %s" % (check,)
				addInterval((iStart(check)-h, iEnd(check)-l), cStruct[-1])
		elif (ftype(cStruct[1]) == ALWAYS_T):
			print "INC ALWAYS"
			h = hbound(cStruct[1])
			l = lbound(cStruct[1])
			checkInt = (ctime - (h-l), ctime)
			checklist = Struct[get_tags(cStruct[1])][-1]

			if (len(checklist) > 0):
				check = checklist[-1]
				print "checking if %s can be an always %s" % (check, checkInt)
				if (alCheck(check, checkInt)):
					addInterval((iStart(check)-l, iEnd(check)-h), cStruct[-1])
		elif (ftype(cStruct[1]) == UNTIL_T):
			print "INC UNTIL"
			h = hbound(cStruct[1])
		#	subform1 = substitute_per(Struct, cstate, untilP1(cStruct[1]))
			subform2 = substitute_per_ag(Struct, cstate, (ctime, untilP2(cStruct[1])))
			h = hbound(cStruct[1])
			l = lbound(cStruct[1])
			tags = get_tags(cStruct[1])

			checkE = Struct[tags[1]][-1]
			if (len(checkE) > 0):
				lastE = checkE[-1]
				print "until checking eventually %s" % (lastE,)
				alList = Struct[tags[0]][-1]
				for a in alList:
					print "checking if %s can be an always %s" % (a, lastE)
					if (int_closed_intersect_exists(a, lastE)):
						start = iStart(a)
						end = min(iEnd(a),iEnd(lastE))
						addInterval((start,end), cStruct[-1])
		else:
			print "INC PROP/PT"
			# else cIntervalOpen stays false
			subform = substitute_per_ag(Struct, cstate, (ctime, cStruct[1]))
			if (checkRes(reduce(subform)) == True):
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
		print "Incremented and cleaned: %s" % (cStruct,)
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
