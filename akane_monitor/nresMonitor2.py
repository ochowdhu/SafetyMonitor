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

TAGi, FORMULAi, DELAYi, VALIDi, LISTi, FLISTi = range(0,6) 

## debug constants
DBG_ERROR = 0x01
DBG_STRUCT = 0x02
DBG_SMON = 0x04
DBG_STATE = 0x08
DBG_MASK = DBG_ERROR | DBG_STRUCT | DBG_SMON | DBG_STATE 
#DBG_MASK = DBG_ERROR
DEBUG = True
# global constants
PERIOD = 1
delim = ','
sTag = 0


class structure:
	def __init__(self, tag, formula=[], delay=0):
		self.tag = tag
		self.formula = formula
		self.delay = delay
		self.history = {}
		self.residues = []
		self.valid = 0

	def addHist(self, time, val):
		self.history[time] = val
	def addRes(self, time, formula):
		self.residues.append((time,formula))
	def cleanRes(self):
		self.residues = [f for f in self.residues if (f[1] != True and f[1] != False)]
	def updateHist(self):
		for res in self.residues:
			if (res[1] == True):
				self.addHist(res[0], True)
			elif (res[1] == False):
				self.addHist(res[0], False)
	def incrRes(self, Struct, cstate):
		for i,f in enumerate(self.residues):
			self.residues[i] = (f[0], reduce(substitute_per_agp(Struct, cstate, f)))
	def __str__(self):
		return "Struct: [%d|| DEL: %d FORM: %s VAL: %d :: HIST: %s, RES: %s]" % (self.tag, self.delay, self.formula, self.valid, self.history, self.residues)
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
	print "############## Beginning monitor algorithm: residuep"
	#mon_residue(inFile, inFormula, traceOrder)
	mon_residuep(inFile, inFormula, traceOrder)
############# END MAIN ############
##################################

def mon_residuep(inFile, inFormula, traceOrder):
	# some algorithm local variables
	cstate = {}
	cHistory = {}
	formulas = []
	Struct = {}
	# build struct and save delay
	D = delay(inFormula)
	DP = past_delay(inFormula)
	build_structurep(Struct, inFormula)

	dprint("Struct is: ", DBG_STRUCT)
	for s in Struct:
		dprint("%s" % (Struct[s],), DBG_STRUCT)
		
	dprint("Formula delay is %d, %d :: wait delay %d" % (D,DP, wdelay(inFormula)), DBG_SMON)
	# wait for new data...
	for line in inFile:
			dprint("###### New event received",DBG_SMON)
			updateState(cstate, traceOrder, line)
			incr_struct_resp(Struct, cstate)
			#dprint("INCREMENTED, DEBUG")
			#for s in Struct:
			#	dprint("%s" % (Struct[s],), DBG_STRUCT)

			dprint("Adding current formula", DBG_SMON)
			formulas.append((cstate["time"], inFormula))
			dprint(formulas, DBG_SMON)
			dprint("reducing all formulas", DBG_SMON)
			for i,f in enumerate(formulas[:]):
				formulas[i] = (f[0], reduce(substitute_per_agp(Struct, cstate, f)))
			dprint(formulas, DBG_SMON)
			dprint("removing finished formulas and check violations...", DBG_SMON)
			# remove any True formulas from the list
			formulas[:] = [f for f in formulas if f[1] != True]
			# skip actually checking while we see if struct build works
			for i,f in enumerate(formulas[:]):
				if (f[1] == False):
						print "VIOLATION DETECTED AT %s@%s" % (f[0],cstate["time"],)
						sys.exit(1)
				else:	# eventually never satisfied
					if (f[0]+D <= cstate["time"]):
						print "VIOLATOR: %s" % (f,)
						print "VIOLATION DETECTED AT %s@%s" % (f[0],cstate["time"],)
						sys.exit(1)
	print "finished, trace satisfies formula"

def substitute_per_agp(Struct, cstate, formula_entry):
	ctime = cstate["time"]
	formtime = formula_entry[0]
	formula = formula_entry[1]
	if (ftype(formula) == EXP_T):
		return [formula[0], substitute_per_agp(Struct, cstate, (formtime, formula[1]))]
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
		return ['notprop', substitute_per_agp(Struct, cstate, (formtime, formula[1]))]
	elif (ftype(formula) == AND_T):
		return ['andprop', substitute_per_agp(Struct, cstate, (formtime, formula[1])), substitute_per_agp(Struct, cstate, (formtime,formula[2]))]
	elif (ftype(formula) == OR_T):
		return ['orprop', substitute_per_agp(Struct, cstate, (formtime,formula[1])), substitute_per_agp(Struct, cstate, (formtime, formula[2]))]
	elif (ftype(formula) == IMPLIES_T):
		print "Got implies %s" % formula
		return ['impprop', substitute_per_agp(Struct, cstate, (formtime,formula[1])), substitute_per_agp(Struct, cstate, (formtime, formula[2]))]
	elif (ftype(formula) == EVENT_T): 
		subStruct = Struct[get_tags(formula)]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		allF = True
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct.history):
				if (subStruct.history[t] == True):
					return True
			else:
				allF = False
		# if we're past the time we have to have an answer, we didn't see the eventually
		if (allF == True):# or ctime > formtime + wdelay(formula)):
			return False
		return formula
	elif (ftype(formula) == ALWAYS_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		allT = True
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct.history):
				if (subStruct.history[t] == False):
					return False
			else:
				allT = False
		# past time and still alive, return true
		if (allT == True):
			return True
		# trying explicit checking for True return first
		#if (ctime > formtime + wdelay(formula)):
		#	return True
		return formula
	elif (ftype(formula) == UNTIL_T): 
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		end = None
		allF = True
		maxvalid = -1
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct2.history):
				maxvalid = max(maxvalid, t)
				if (subStruct2.history[t] == True):
					end = t
					allF = False
					break
			else:
				allF = False
		# if we're past the time we have to have an answer, we didn't see the eventually
		# TODO need aggressive until/since, gotta check current but be able to wait for P2
		found = True
		if allF:
			return False
		elif (end is None):
			end = maxvalid
			found = False
		
		# did find eventually, check P1
		sEnd = end
		sStart = formtime
		allT = True
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct1.history):
				if (subStruct1.history[t] == False):
					return False
			else:
				allT = False
		# past time and still alive, return true
		if (allT == True and found):
			return True
		return formula
	elif (ftype(formula) == PEVENT_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = formtime - lbound(formula)
		sStart = formtime - hbound(formula)
		allF = True
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct.history):
				if (subStruct.history[t] == True):
					return True
			else:
				allF = False
		# if we're past the time we have to have an answer, we didn't see the eventually
		if (allF == True):	# or ctime > formtime + wdelay(formula)):
			return False
		return formula
	elif (ftype(formula) == PALWAYS_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = formtime - lbound(formula)
		sStart = formtime - hbound(formula)
		allT = True
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct.history):
				if (subStruct.history[t] == False):
					return False
			else:
				allT = False
		# past time and still alive, return true
		if (allT == True):
			return True
		# trying explicit checking for True return first
		#if (ctime > formtime + wdelay(formula)):
		#	return True
		return formula
	elif (ftype(formula) == SINCE_T):
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sEnd = formtime - lbound(formula)
		sStart = formtime - hbound(formula)
		start = None
		allF = True
		print "checking (%d,%d)" % (sStart, sEnd)
		print "sub: %s" % subStruct2
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct2.history):
				if (subStruct2.history[t] == True):
					start = t
					allF = False
					break
			else:
				allF = False
		# if we're past the time we have to have an answer, we didn't see the eventually
		print "start: %s" % start
		found = True
		if allF: 
			return False
		elif (start is None):
			return formula

		# did find eventually, check P1
		sEnd = formtime
		sStart = start
		allT = True
		print "checking (%d,%d)" % (sStart, sEnd)
		print "sub: %s" % subStruct1
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct1.history):
				if (subStruct1.history[t] == False):
					return False
			else:
				allT = False
		# past time and still alive, return true
		if (allT == True):
			return True
		return formula
	else:
		return INVALID_T

def build_structurep(Struct, formula, extbound=0):
	if (ftype(formula) == EXP_T):
		dprint("BUILDING: got an exp, recursing", DBG_STRUCT)
		return build_structurep(Struct, rchild(formula))
	elif (ftype(formula) == PROP_T):
		dprint("BUILDING: got a prop, returning", DBG_STRUCT)
		return True
	elif (ftype(formula) == NPROP_T):
		dprint("BUILDING: got an nprop, returning", DBG_STRUCT)
		return True
	elif (ftype(formula) == NOT_T):
		dprint("BUILDING: got a not, recursing", DBG_STRUCT)
		build_structurep(Struct, rchild(formula))
		return True
	elif (ftype(formula) == AND_T):
		dprint("BUILDING: got an and, recursing both", DBG_STRUCT)
		build_structurep(Struct, lchild(formula)) 
		build_structurep(Struct, rchild(formula))
		return True
	elif (ftype(formula) == OR_T):
		dprint("BUILDING: got an or, recursing both", DBG_STRUCT)
		build_structurep(Struct, lchild(formula))
		build_structurep(Struct, rchild(formula))
		return True
	elif (ftype(formula) == IMPLIES_T):
		dprint("BUILDING: got an implies, recursing both", DBG_STRUCT)
		build_structurep(Struct, lchild(formula)) 
		build_structurep(Struct, rchild(formula))
		return True
	elif (ftype(formula) == EVENT_T): 
		dprint("BUILDING: got an eventually, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		d = delay(formula) + extbound
		add_structp(Struct, cTag, d, rchild(formula))
		return build_structurep(Struct, rchild(formula), extbound=d)
	elif (ftype(formula) == ALWAYS_T):
		dprint("BUILDING: got an always, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		d = delay(formula) + extbound
		add_structp(Struct, cTag, d, rchild(formula))
		return build_structurep(Struct, rchild(formula), extbound=d)
	elif (ftype(formula) == UNTIL_T): 
		dprint("BUILDING: got an until, ADDING STRUCT and recursing both", DBG_STRUCT)
		# Tags get put into formula[2] so tagging P2 then P1 makes formula into
		# [bound, bound, tagP1, tagP2, P1, P2]
		# do P2
		cTag = tag_formula(formula)
		d2 = delay(untilP2(formula)) + extbound
		add_structp(Struct, cTag, d2, untilP2(formula))
		# do P1
		cTag = tag_formula(formula)
		d1 = delay(untilP1(formula)) + extbound
		add_structp(Struct, cTag, d1, untilP1(formula))
		build_structurep(Struct, untilP1(formula), extbound=d1)
		build_structurep(Struct, untilP2(formula), extbound=d2)
		return True
	elif (ftype(formula) == PALWAYS_T):
		dprint("BUILDING: got a past always, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		d = past_delay(formula) + extbound
		add_structp(Struct, cTag, d, rchild(formula))
		return build_structurep(Struct, rchild(formula), extbound=d)
	elif (ftype(formula) == PEVENT_T):
		dprint("BUILDING: got a past eventually, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		d = past_delay(formula) + extbound
		add_structp(Struct, cTag, d, rchild(formula))
		return build_structurep(Struct, rchild(formula), extbound=d)
	elif (ftype(formula) == SINCE_T):
		dprint("BUILDING: got a since, ADDING BOTH STRUCTS and recursing both", DBG_STRUCT)
		# Tags get put into formula[2] so tagging P2 then P1 makes formula into
		# [bound, bound, tagP1, tagP2, P1, P2]
		# do P2
		cTag = tag_formula(formula)
		d2 = delay(untilP2(formula)) + extbound
		add_structp(Struct, cTag, d2, untilP2(formula))
		# do P1
		cTag = tag_formula(formula)
		d1 = delay(untilP1(formula)) + extbound
		add_structp(Struct, cTag, d1, untilP1(formula))
		build_structurep(Struct, untilP1(formula), extbound=d1)
		build_structurep(Struct, untilP2(formula), extbound=d2)
		return True
	else:
		dprint("BUILDING ERROR: Got unmatched AST node while building", DBG_STRUCT);
		return False
	# shouldn't get here
	return False

def add_structp(Struct, tag, delay, formula):
	newSt = structure(tag, formula, delay)
	# Add interval that fills entire past bound 
	for i in range(0-delay, 0):
		newSt.addHist(i, True)
	Struct[tag] = newSt
	print "Added %s to %s" % (newSt, Struct)
	return

def reduce(formula):
	if (ftype(formula) == EXP_T):
		#return [formula[0], reduce(formula[1])]
		return reduce(formula[1])
	elif (ftype(formula) == VALUE_T):
		return formula
	elif (ftype(formula) == PROP_T):
		dprint("shouldn't get here, already sub'd", DBG_ERROR)
		return cstate[formula[1]]
	elif (ftype(formula) == NPROP_T):
		dprint("shouldn't get here, already sub'd", DBG_ERROR)
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
		return formula
		#dprint("Can't get here, should've been removed by sub()", DBG_ERROR)
		#return INVALID_T
	elif (ftype(formula) == PALWAYS_T):
		return formula
		#dprint("Can't get here, should've been removed by sub()", DBG_ERROR)
		#return INVALID_T
	elif (ftype(formula) == SINCE_T):
		return formula
		#dprint("Can't get here, should've been removed by sub()", DBG_ERROR)
		#return INVALID_T
	else:
		return INVALID_T

def incr_struct_resp(Struct, cstate):
	ctime = cstate["time"]
	taglist = list(Struct.keys())
	taglist.sort()
	taglist.reverse()
	# must check in order due to nested dependencies
	for t in taglist:
		cStruct = Struct[t]

		# add current time residue to each structure
		newform = substitute_per_agp(Struct, cstate, (ctime, cStruct.formula))
		cStruct.addRes(ctime, newform)

		# reduce all residues with new time
		cStruct.incrRes(Struct, cstate)
		# update history based on residues
		cStruct.updateHist()
		# remove finished residues
		cStruct.cleanRes()

		#########################################
		###################### Chopping
		# remove unneeded values from struct list
		#intlist = cStruct[-1]
		#for i in (intlist[:]):
		#	# remove any closed intervals that end earlier than our max look-back
		#	if (not isopen_interval(i) and (i[1] < ctime-cStruct[2])):
		#		intlist.remove(i)
		dprint("Incremented and cleaned: %s" % (cStruct,), DBG_STRUCT)
	return
##########################################
############ UTILS ######################

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
def wdelay(formula):
	print "wdelay %s" % formula
	if (ftype(formula) == EXP_T):
		return wdelay(rchild(formula))
	elif (ftype(formula) == PROP_T):
		return 0
	elif (ftype(formula) == NPROP_T):
		return 0
	elif (ftype(formula) == NOT_T):
		return wdelay(rchild(formula))
	elif (ftype(formula) == AND_T):
		return max(wdelay(lchild(formula)),wdelay(rchild(formula)))
	elif (ftype(formula) == OR_T):
		return max(wdelay(lchild(formula)),wdelay(rchild(formula)))
	elif (ftype(formula) == IMPLIES_T):
		return max(wdelay(lchild(formula)),wdelay(rchild(formula)))
	elif (ftype(formula) == EVENT_T): 
		return hbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == ALWAYS_T):
		return hbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == UNTIL_T): 
		return hbound(formula) + max(wdelay(untilP1(formula)),wdelay(untilP2(formula)))
	elif (ftype(formula) == PALWAYS_T):
		return -1*lbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		return -1*lbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		return -1*lbound(formula) + max(wdelay(untilP1(formula)),wdelay(untilP2(formula)))
	else:
		dprint("DELAY ERROR: Got unmatched AST node while building", DBG_ERROR);
		return None
	# shouldn't get here
	return None
def mwdelay(formula):
	if (ftype(formula) == EXP_T):
		return wdelay(rchild(formula))
	elif (ftype(formula) == PROP_T):
		return 0
	elif (ftype(formula) == NPROP_T):
		return 0
	elif (ftype(formula) == NOT_T):
		return wdelay(rchild(formula))
	elif (ftype(formula) == AND_T):
		return max(wdelay(lchild(formula)),wdelay(rchild(formula)))
	elif (ftype(formula) == OR_T):
		return max(wdelay(lchild(formula)),wdelay(rchild(formula)))
	elif (ftype(formula) == IMPLIES_T):
		return max(wdelay(lchild(formula)),wdelay(rchild(formula)))
	elif (ftype(formula) == EVENT_T): 
		return hbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == ALWAYS_T):
		return lbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == UNTIL_T): 
		return hbound(formula) + max(wdelay(untilP1(formula)),wdelay(untilP2(formula)))
	elif (ftype(formula) == PALWAYS_T):
		return -1*hbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		return -1*lbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		return -1*lbound(formula) + max(wdelay(untilP1(formula)),wdelay(untilP2(formula)))
	else:
		dprint("DELAY ERROR: Got unmatched AST node while building", DBG_ERROR);
		return None
	# shouldn't get here
	return None

############## PRINT/DEBUG ############
#######################################
def dprint(string, lvl=0xFF):
#	print "DPRINT %s %d" % (string, lvl)
	if (DBG_MASK & lvl):
		print string

############ INTERVAL UTILITIES
#######################################
#######################################

# add interval to list
def addInterval(intv, structlist):
	if (len(structlist) > 0):
		last = structlist[-1]
	else:
		last = (None, None)
	#if (iEnd(last) >= iStart(int)):
	if (iStart(intv)-PERIOD <= iEnd(last)):
	#if (iEnd(last)+PERIOD >= iStart(int)):
		structlist[-1] = (iStart(last), iEnd(intv))
	else:
		structlist.append(intv)
# start a new interval tuple
def new_interval(start):
	return (start, None)

# end an existing interval tuple
def close_interval(interval, end):
	return (interval[0], end)

# check if interval is open (infinite)
def isopen_interval(interval):
	return interval[1] is None

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
def intersect_exists(test_i, history_i):
	if ((isopen_interval(history_i) or iStart(test_i) < iEnd(history_i)) 
		and iStart(history_i) <= iEnd(test_i)):
		return True
	else:
		return False

# get start point of intersection
def intersect_start(test_i, history_i):
	if int_intersect_exists(test_i, history_i):
		return max(iStart(test_i), iStart(history_i))
	return None

# is test subset of history
def subset(test_i, history_i):
	if ((iStart(history_i) <= iStart(test_i)) and
		(isopen_interval(history_i) or iEnd(test_i) < iEnd(history_i))):
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
