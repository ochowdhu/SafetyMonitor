#!/usr/bin/python
##
##
## @author Aaron Kane
##
## Starting a clean nested residual monitor file. 
##	 Full file is getting a little crowded

import sys
import signal

# Get some stuff out of here, easier to deal with
from monUtils import *

# global constants
delim = ','


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
	formulas = []
	Struct = {}
	# build struct and save delay
	D = delay(inFormula)
	DP = past_delay(inFormula)
	WD = wdelay(inFormula)
	build_structurep(Struct, inFormula)

	dprint("Struct is: ", DBG_STRUCT)
	for s in Struct:
		dprint("%s" % (Struct[s],), DBG_STRUCT)
		
	dprint("Formula delay is %d, %d :: wait delay %d" % (D,DP,WD), DBG_SMON)
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
					if (f[0]+WD <= cstate["time"]):
						print "VIOLATOR: %s" % (f,)
						print "VIOLATION DETECTED AT %s@%s" % (f[0],cstate["time"],)
						sys.exit(1)
	print "finished, trace satisfies formula"

def mon_cons_residue(inFile, inFormula, traceOrder):
	pass

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

def substitute_perint_agp(Struct, cstate, formula_entry):
	ctime = cstate["time"]
	formtime = formula_entry[0]
	formula = formula_entry[1]
	if (ftype(formula) == EXP_T):
		return [formula[0], substitute_perint_agp(Struct, cstate, (formtime, formula[1]))]
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
		return ['notprop', substitute_perint_agp(Struct, cstate, (formtime, formula[1]))]
	elif (ftype(formula) == AND_T):
		return ['andprop', substitute_perint_agp(Struct, cstate, (formtime, formula[1])), substitute_perint_agp(Struct, cstate, (formtime,formula[2]))]
	elif (ftype(formula) == OR_T):
		return ['orprop', substitute_perint_agp(Struct, cstate, (formtime,formula[1])), substitute_perint_agp(Struct, cstate, (formtime, formula[2]))]
	elif (ftype(formula) == IMPLIES_T):
		print "Got implies %s" % formula
		return ['impprop', substitute_perint_agp(Struct, cstate, (formtime,formula[1])), substitute_perint_agp(Struct, cstate, (formtime, formula[2]))]
	elif (ftype(formula) == EVENT_T): 
		subStruct = Struct[get_tags(formula)]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		check = (sStart, sEnd+PERIOD)
		
		for i in substruct.history:
			if i.intersects(check):
				return True
		# not waiting on any data, if formula satisfied would've returned true above
		if (substruct.valid >= sEnd):
			return False
		return formula
	elif (ftype(formula) == ALWAYS_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		check = (sStart, sEnd+PERIOD)

		alcheck = substruct.alCheck(check)
		if (alcheck == ALC_SATISFY):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE
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

#### Python stuff - set main and catch ^C
#########################################
def signal_handler(signal, frame):
	print "Caught ctrl-c, exiting..."
	sys.exit(1)

if __name__ == "__main__":
	main()
