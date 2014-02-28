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

DEBUG = True
# fill some propositional values, and keep a history buffer
cstate = {}
cHistory = []
traceOrder = []
delim = ','
Struct = {}
sTag = 0

pphead = ""

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
	# build cstate
	names = inFile.readline().strip().split(delim)
	# allow comments above names
	while (names[0].startswith("#")):
		names = inFile.readline().strip().split(delim)
	for n in names:
		cstate[n] = 0
		traceOrder.append(n)
	print "Read proposition names from file:"
	for n in cstate.keys():
		print n
	print "TraceOrder is: %s" % (traceOrder,)

	build_structure(inFormula)

	for s in Struct:
		print "Struct: %s -- %s" % (s,Struct[s])
	
	for line in inFile:
			updateState(line)
			cHistory.append(cstate.copy())
			print "AT STATE %s" % (cstate,)
			incr_struct(cstate["time"])
			for s in Struct:
				print "Struct: %s" % (Struct[s],)

	for h in cHistory:
		print h

	#print "Trying substitute:"
	#print "starting with %s" % (inFormula,)
	#nFormula = substitute(inFormula)
	#print "substituted: %s" % (nFormula,)

############# END MAIN ############
##################################

############# MONITOR ALGOS #######
###################################


###### CONSERVATIVE, DELAY WAIT WITH STRUCTURES
def mon_cons(formula):
	pass
def smon_cons_ST(ctime, formula):
	if (ftype(formula) == EXP_T):
		dprint("got an exp, returning")
		return smon_cons_ST(ctime, rchild(formula))
	elif (ftype(formula) == PROP_T):
		dprint("got a prop, returning")
		return cstate[rchild(formula)]
	elif (ftype(formula) == NPROP_T):
		dprint("got an nprop")
		return not cstate[rchild(formula)]
	elif (ftype(formula) == NOT_T):
		dprint("got a notprop")
		return not smon_cons_ST(ctime, rchild(formula))
	elif (ftype(formula) == AND_T):
		dprint("got an and, returning both")
		return smon_cons_ST(ctime, lchild(formula)) and smon_cons_ST(ctime, rchild(formula))
	elif (ftype(formula) == OR_T):
		dprint("got an or, returning both")
		return smon_cons_ST(ctime, lchild(formula)) or smon_cons_ST(ctime, rchild(formula))
	elif (ftype(formula) == IMPLIES_T):
		dprint("got an implies, returning both")
		return not smon_cons_ST(ctime, lchild(formula)) or smon_cons_ST(ctime, rchild(formula))
	elif (ftype(formula) == EVENT_T): 
		dprint("got an eventually, ADDING OBLIGATION")
		l = ctime + formula[1]
		h = ctime + formula[2]

		dprint("checking range: [%d, %d]" % (l,h))
		intlist = Struct[get_tags(formula)][-1]
		for i in intlist:
			if int_intersect_exists((l,h), i):
				return True
		# didn't find the event in the bounds
		return False
	elif (ftype(formula) == ALWAYS_T):
		dprint("got an always, ADDING INVARIANT")
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
		dprint("got an always, ADDING OBLIGATION AND INVAR")
		l = ctime + formula[1]
		h = ctime + formula[2]
		dprint("checking range: %d - %d" % (l, h))
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
		dprint("Got Until end %s" % (end,))
		# Now check P1
		l = ctime
		h = end
		intlist = Struct[tags[0]][-1]						# get list for P1
		# and check P1 as a PALWAYS since P2 occured
		for i in intlist:
			if (int_subset((l,h), i)):
				return True
		dprint("Until invariant not satisfied for [%d,%d]" % (l, h))
		return False
	elif (ftype(formula) == PEVENT_T):
		dprint("got a pevent, checking structure")
		checkStart = ctime-formula[2]
		checkEnd = ctime-formula[1]

		dprint("checking range: [%d, %d]" % (checkStart, checkEnd))
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
		dprint("got a palways, checking structure")
		checkStart = ctime-formula[2]
		checkEnd = ctime-formula[1]

		dprint("checking range: %d - %d" % (checkStart, checkEnd))
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
		dprint("got a since, checking structure")
		checkStart = ctime-formula[2]
		checkEnd = ctime-formula[1]
		dprint("checking range: %d - %d" % (checkStart, checkEnd))
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
		dprint("Got Since start %s" % (start,))
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
		dprint("Since invariant not satisfied for [%d,%d]" % (checkStart, checkEnd))
		return False
	else:
		return INVALID_T

############ Main/Monitor helpers ####
######################################
def updateState(line):
	vals = line.strip().split(delim)
	for i in range(0, len(vals)):
		print "%d| Updating %s to %s" % (i, traceOrder[i], vals[i])
		cstate[traceOrder[i]] = int(vals[i])
## start with no future temporal properties
		
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

def substitute(formula):
	if (ftype(formula) == EXP_T):
		return [formula[0], substitute(formula[1])]
	elif (ftype(formula) == PROP_T):
		return cstate[formula[1]]
	elif (ftype(formula) == NPROP_T):
		return not cstate[formula[1]]
	elif (ftype(formula) == NOT_T):
		return ['notprop', substitute(formula[1])]
	elif (ftype(formula) == AND_T):
		return ['andprop', substitute(formula[1]), substitute(formula[2])]
	elif (ftype(formula) == OR_T):
		return ['orprop', substitute(formula[1]), substitute(formula[2])]
	elif (ftype(formula) == IMPLIES_T):
		return ['impprop', substitute(formula[1]), substitute(formula[2])]
	elif (ftype(formula) == EVENT_T): 
		return ['eventprop', 'TAG']
	elif (ftype(formula) == ALWAYS_T):
		return ['alwaysprop', 'TAG']
	elif (ftype(formula) == UNTIL_T): 
		return ['untilprop', 'TAG']
	elif (ftype(formula) == PEVENT_T):
		return history_lookup1(formula[3])
	elif (ftype(formula) == PALWAYS_T):
		return history_lookup1(formula[3])
		pass
	elif (ftype(formula) == SINCE_T):
		return history_lookup(formula[3], formula[4])
	else:
		return INVALID_T

def history_lookup1(tag):
	return "history"

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

def build_structure(formula, extbound=(0,0)):
	if (ftype(formula) == EXP_T):
		dprint("BUILDING: got an exp, recursing")
		return build_structure(rchild(formula))
	elif (ftype(formula) == PROP_T):
		dprint("BUILDING: got a prop, returning")
		return True
	elif (ftype(formula) == NPROP_T):
		dprint("BUILDING: got an nprop, returning")
		return True
	elif (ftype(formula) == NOT_T):
		dprint("BUILDING: got a not, recursing")
		build_structure(rchild(formula))
		return True
	elif (ftype(formula) == AND_T):
		dprint("BUILDING: got an and, recursing both")
		build_structure(lchild(formula)) 
		build_structure(rchild(formula))
		return True
	elif (ftype(formula) == OR_T):
		dprint("BUILDING: got an or, recursing both")
		build_structure(lchild(formula))
		build_structure(rchild(formula))
		return True
	elif (ftype(formula) == IMPLIES_T):
		dprint("BUILDING: got an implies, recursing both")
		build_structure(lchild(formula)) 
		build_structure(rchild(formula))
		return True
	elif (ftype(formula) == EVENT_T): 
		dprint("BUILDING: got an eventually, ADDING STRUCT and recursing")
		cTag = tag_formula(formula)
		add_struct(cTag, (formula[1], formula[2]+extbound[1]), rchild(formula))
		return build_structure(rchild(formula), extbound=(formula[1], formula[2]))
	elif (ftype(formula) == ALWAYS_T):
		dprint("BUILDING: got an always, ADDING STRUCT and recursing")
		cTag = tag_formula(formula)
		add_struct(cTag, (formula[1], formula[2]+extbound[1]), rchild(formula))
		return build_structure(rchild(formula), extbound=(formula[1], formula[2]))
	elif (ftype(formula) == UNTIL_T): 
		dprint("BUILDING: got an until, ADDING STRUCT and recursing both")
		# Tags get put into formula[2] so tagging P2 then P1 makes formula into
		# [bound, bound, tagP1, tagP2, P1, P2]
		# do P2
		cTag = tag_formula(formula)
		add_struct(cTag, (formula[1], formula[2]+extbound[1]), untilP2(formula))
		# do P1
		cTag = tag_formula(formula)
		add_struct(cTag, (formula[1], formula[2]+extbound[1]), untilP1(formula))
		build_structure(untilP1(formula), extbound=(formula[1],formula[2]))
		build_structure(untilP2(formula), extbound=(formula[1],formula[2]))
		return True
	elif (ftype(formula) == PALWAYS_T):
		dprint("BUILDING: got a past always, ADDING STRUCT and recursing")
		cTag = tag_formula(formula)
		add_struct(cTag, (formula[1], formula[2]+extbound[1]), rchild(formula))
		return build_structure(rchild(formula), extbound=(formula[1], formula[2]))
	elif (ftype(formula) == PEVENT_T):
		nestprint("BUILDING: got a past eventually, ADDING STRUCT and recursing")
		cTag = tag_formula(formula)
		add_struct(cTag, (formula[1], formula[2]+extbound[1]), rchild(formula))
		return build_structure(rchild(formula), extbound=(formula[1], formula[2]))
	elif (ftype(formula) == SINCE_T):
		nestprint("BUILDING: got a since, ADDING BOTH STRUCTS and recursing both")
		# Tags get put into formula[2] so tagging P2 then P1 makes formula into
		# [bound, bound, tagP1, tagP2, P1, P2]
		# do P2
		cTag = tag_formula(formula)
		add_struct(cTag, (formula[1], formula[2]+extbound[1]), untilP2(formula))
		# do P1
		cTag = tag_formula(formula)
		add_struct(cTag, (formula[1], formula[2]+extbound[1]), untilP1(formula))
		build_structure(untilP1(formula), extbound=(formula[1],formula[2]))
		build_structure(untilP2(formula), extbound=(formula[1],formula[2]))
		return True
	else:
		nestprint("BUILDING ERROR: Got unmatched AST node while building");
		return False
	# shouldn't get here
	return False

def add_struct(tag, bounds, formula):
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
	print "GET_TAGS OF %s" % (formula,)
	if (len(formula) == 5):
		return formula[3]
	elif (len(formula) == 7):
		return (formula[3], formula[4])
	return -1

def incr_struct(time):
	taglist = list(Struct.keys())
	taglist.sort()
	taglist.reverse()
	# must check in order due to nested dependencies
	for t in taglist:
		cStruct = Struct[t]
		print "Incrementing %s" % (cStruct,)
		cIntervalOpen = False
		if (len(cStruct[-1]) > 0):
			last_int = cStruct[-1][-1]	# get most recent interval from interval list
			cIntervalOpen = isopen_interval(last_int)	
		# else cIntervalOpen stays false
		if smon_cons_ST(time, cStruct[1]):
			# if not in an open interval, start a new one
			# if we are in an existing open interval, then we don't need to do anything
			if (not cIntervalOpen):
				cStruct[-1].append(new_interval(time))
		else: # Formula is not satisfied at current time
			if (cIntervalOpen):
				# close last interval in place
				cStruct[-1][-1] = close_interval(last_int, time)	

		# remove unneeded values from struct list
		intlist = cStruct[-1]
		for i in (intlist[:]):
			# remove any closed intervals that end earlier than our max look-back
			if (not isopen_interval(i) and (i[1] < time-cStruct[2])):
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
		return i >= interval[0] and i <= interval[1]
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
# is test subset of history
def int_subset(test_i, history_i):
	if ((iStart(history_i) <= iStart(test_i)) and
		(isopen_interval(history_i) or iEnd(test_i) < iEnd(history_i))):
		return True
	return False
#### Utilities
######################################
def dprint(string):
	if DEBUG:
		print string

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
