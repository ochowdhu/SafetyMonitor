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
algChoose = None 

###### Keeping this script compatible with resMonitor for now
def main():
	global algChoose
	# do setup
	signal.signal(signal.SIGINT, signal_handler)
	#### Handle input parameters
	##############################
	#algChoose = 0
	if len(sys.argv) > 4:
		PERIOD = int(sys.argv[3])
	if len(sys.argv) > 3:
		inFormula = eval(sys.argv[1])	# DANGEROUS. DON'T PASS ME ARBITRARY CODE
		inFile = open(sys.argv[2], "r")
		algChoose = int(sys.argv[3])
	else:
		print "Bad Usage: python monitor.py <formula> <tracefile> <algChoose> [period]"
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
	if (algChoose == 0):
		mon_intresidue(inFile, inFormula, traceOrder)
	elif (algChoose == 1):
		mon_purecons(inFile, inFormula, traceOrder)
	elif (algChoose == 2):
		mon_stcons(inFile, inFormula, traceOrder)
	else:
		print "No algorithm chosen, quitting..."
############# END MAIN ############
##################################

############## BEGIN MONITOR FUNCTIONS ###########
def mon_stcons(inFile, inFormula, traceOrder):
	allPass = True
	FastDie = True
	cstate = {}
	formulas =[]
	history = {}
	Struct = {}
	build_past_structure(Struct, inFormula)
	WD = wdelay(inFormula)
	#
	eptr = 0
	cptr = 0
	#
	dprint("Using delay %s" % WD)
	#
	for line in inFile:
		updateState(cstate, traceOrder, line)
		history[cptr] = cstate.copy()
		#
		ctime = cstate["time"]
		dprint("current state is %s" % (cstate,))
		#
		while ((eptr <= cptr) and (tau(history, cptr) - tau(history, eptr) >= WD)):
			evaltime = tau(history,eptr)
			dprint("checking time %s" % evaltime)
			mon = reduce(substitute_stcons(Struct, cstate, (eptr, inFormula)))
			#
			allPass = allPass and mon
			if (FastDie and bool(mon) == False):
				dprint("!!!!FORMULA VIOLATED %s@%s" % (eptr, cptr))
				sys.exit(5)
			eptr = eptr + 1
		cptr = cptr + 1
		#
		# clean history
		histremove = [k for k in history if (cstate["time"] - history[k]["time"] > WD)]	
		for k in histremove:
			del history[k]
	if allPass:
		print "#### Trace Satisfied formula ###"
	else:
		print "### Trace Violated formula ###"

def mon_purecons(inFile, inFormula, traceOrder):
	allPass = True
	FastDie = True
	cstate = {}
	formulas =[]
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
		updateState(cstate, traceOrder, line)
		history[cptr] = cstate.copy()
		#
		ctime = cstate["time"]
		dprint("current state is %s" % (cstate,))
		#
		while ((eptr <= cptr) and (tau(history, cptr) - tau(history, eptr) >= WD)):
			evaltime = tau(history,eptr)
			dprint("checking time %s" % evaltime)
			mon = smon_purecons(eptr, history, inFormula)
			#
			allPass = allPass and mon
			if (FastDie and bool(mon) == False):
				dprint("!!!!FORMULA VIOLATED %s@%s" % (eptr, cptr))
				sys.exit(5)
			eptr = eptr + 1
		cptr = cptr + 1
		#
		# clean history
		histremove = [k for k in history if (cstate["time"] - history[k]["time"] > (PD+D))]	
		for k in histremove:
			del history[k]
	if allPass:
		print "#### Trace Satisfied formula ###"
	else:
		print "### Trace Violated formula ###"

def mon_intresidue(inFile, inFormula, traceOrder):
	# some algorithm local variables
	cstate = {}
	formulas = []
	Struct = {}
	# build struct and save delay
	D = delay(inFormula)
	DP = past_delay(inFormula)
	WD = wdelay(inFormula)
	build_structure(Struct, inFormula)

	dprint("Struct is: ", DBG_STRUCT)
	for s in Struct:
		dprint("%s" % (Struct[s],), DBG_STRUCT)
		
	dprint("Formula delay is %d, %d :: wait delay %d" % (D,DP,WD), DBG_SMON)
	# wait for new data...
	for line in inFile:
			dprint("###### New event received",DBG_SMON)
			updateState(cstate, traceOrder, line)
			incr_struct_intres(Struct, cstate)
			#dprint("INCREMENTED, DEBUG")
			#for s in Struct:
			#	dprint("%s" % (Struct[s],), DBG_STRUCT)

			dprint("Adding current formula", DBG_SMON)
			formulas.append((cstate["time"], inFormula))
			dprint(formulas, DBG_SMON)
			dprint("reducing all formulas", DBG_SMON)
			for i,f in enumerate(formulas[:]):
				formulas[i] = (f[0], reduce(substitute_perint_agp(Struct, cstate, f)))
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

########### END MONITOR FUNCTIONS ############

####### CONSERVATIVE SOLVE ###############
def tau(history, cptr):
	return history[cptr]["time"]

def smon_purecons(cstep, history, formula):
	if (cstep < 0):
		return True
	if (ftype(formula) == EXP_T):
		#dprint("got an exp, returning")
		return smon_purecons(cstep, history, rchild(formula))
	elif (ftype(formula) == PROP_T):
		#dprint("got a prop, returning")
		return history[cstep][rchild(formula)]
	elif (ftype(formula) == NPROP_T):
		#dprint("got an nprop")
		return not history[cstep][rchild(formula)]
	elif (ftype(formula) == AND_T):
		#dprint("got an and, returning both")
		return smon_purecons(cstep, history, lchild(formula)) and smon_purecons(cstep, history, rchild(formula))
	elif (ftype(formula) == OR_T):
		#dprint("got an or, returning both")
		return smon_purecons(cstep, history, lchild(formula)) or smon_purecons(cstep, history, rchild(formula))
	elif (ftype(formula) == IMPLIES_T):
		#dprint("got an implies, returning both")
		return not smon_purecons(cstep, history, lchild(formula)) or smon_purecons(cstep, history, rchild(formula))
	elif (ftype(formula) == EVENT_T): 
		#dprint("got an eventually, checking struct")
		l = tau(history, cstep) + formula[1]
		h = tau(history, cstep) + formula[2]

		#dprint("checking range: [%d, %d]" % (l,h))
		for i in range(l, h+PERIOD):
			if smon_purecons(i, history, rchild(formula)):
				return True
		# didn't find the event in the bounds
		return False
	elif (ftype(formula) == ALWAYS_T):
		#dprint("got an always, checking struct")
		l = tau(history, cstep) + formula[1]
		h = tau(history, cstep) + formula[2]
		#dprint("checking range: [%d, %d]" % (l,h))
		for i in range(l, h+PERIOD):
			if not smon_purecons(i, history, rchild(formula)):
				return False 
		# didn't find point where subform was false
		return True
	elif (ftype(formula) == UNTIL_T): 
		#dprint("got until, checking struct")
		l = tau(history, cstep) + formula[1]
		h = tau(history, cstep) + formula[2]
		end = None
		#dprint("checking range: [%d, %d]" % (l,h))
		for i in range(l, h+PERIOD):
			if smon_purecons(i, history, untilP2(formula)):
				end = i
				break
		# didn't find the event in the bounds
		if (end is None):
			return False

		# found P2, check always P1
		l = tau(history, cstep)
		h = end
		#dprint("checking range: [%d, %d]" % (l,h))
		for i in range(l, h+PERIOD):
			if not smon_purecons(i, history, untilP1(formula)):
				return False 
		# didn't find point where subform was false
		return True
	elif (ftype(formula) == PEVENT_T):
		#dprint("got a pevent, checking structure")

		#dprint("got an eventually, checking struct")
		l = tau(history, cstep) - formula[2]
		h = tau(history, cstep) - formula[1]

		#dprint("checking range: [%d, %d]" % (l,h))
		for i in range(l, h+PERIOD):
			if smon_purecons(i, history, rchild(formula)):
				return True
		# didn't find the event in the bounds
		return False
	elif (ftype(formula) == PALWAYS_T):
		#dprint("got a palways, checking structure")
		l = tau(history, cstep) - formula[2]
		h = tau(history, cstep) - formula[1]
		#dprint("checking range: [%d, %d]" % (l,h))
		for i in range(l, h+PERIOD):
			if not smon_purecons(i, history, rchild(formula)):
				return False 
		# didn't find point where subform was false
		return True
	elif (ftype(formula) == SINCE_T):
		#dprint("got until, checking struct")
		l = tau(history, cstep) - formula[2]
		h = tau(history, cstep) - formula[1]
		#dprint("checking range: %d - %d" % (l, h))
		start = None
		#dprint("checking range: [%d, %d]" % (l,h))
		for i in range(l, h+PERIOD):
			if smon_purecons(i, history, untilP2(formula)):
				start = i
				break
		# didn't find the event in the bounds
		if (start is None):
			return False

		# found P2, check always P1
		l = start
		h = tau(history, cstep)
		#dprint("checking range: [%d, %d]" % (l,h))
		for i in range(l, h+PERIOD):
			if not smon_purecons(i, history, untilP1(formula)):
				return False 
		# didn't find point where subform was false
		return True
	else:
		return INVALID_T

######### END CONSERVATIVE SOLVE ##########


########## FULL STRUCT ############
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
	global algChoose
	if (algChoose == 0):
		newSt = istructure(tag, formula, delay)
	elif (algChoose == 2):
		newSt = ipstructure(tag, formula, delay)
	else:
		print "!!!!SHOULD NOT GET HERE....!!!"
		sys.exit(2)
	# Add interval that fills entire past bound 
	for i in range(0-delay, 0):
		newSt.addHist(i, True)
	Struct[tag] = newSt
	print "Added %s to %s" % (newSt, Struct)
	return

def incr_struct_intres(Struct, cstate):
	ctime = cstate["time"]
	taglist = list(Struct.keys())
	taglist.sort()
	taglist.reverse()
	# must check in order due to nested dependencies
	for t in taglist:
		cStruct = Struct[t]

		# add current time residue to each structure
		#newform = substitute_perint_agp(Struct, cstate, (ctime, cStruct.formula))
		cStruct.addRes(Struct, cstate, ctime, cStruct.formula)

		# reduce all residues with new time
		cStruct.incrRes(Struct, cstate)
		# update history based on residues
		cStruct.updateHist()
		# remove finished residues
		cStruct.cleanRes()
		# remove finished histories
		cStruct.cleanHist()

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
##### END FULL STRUCT #########

######### PAST-ONLY STRUCT #####

def build_past_structure(Struct, formula, extbound=0):
	if (ftype(formula) == EXP_T):
		dprint("BUILDING: got an exp, recursing", DBG_STRUCT)
		return build_past_structure(Struct, rchild(formula))
	elif (ftype(formula) == PROP_T):
		dprint("BUILDING: got a prop, returning", DBG_STRUCT)
		return True
	elif (ftype(formula) == NPROP_T):
		dprint("BUILDING: got an nprop, returning", DBG_STRUCT)
		return True
	elif (ftype(formula) == NOT_T):
		dprint("BUILDING: got a not, recursing", DBG_STRUCT)
		build_past_structure(Struct, rchild(formula))
		return True
	elif (ftype(formula) == AND_T):
		dprint("BUILDING: got an and, recursing both", DBG_STRUCT)
		build_past_structure(Struct, lchild(formula)) 
		build_past_structure(Struct, rchild(formula))
		return True
	elif (ftype(formula) == OR_T):
		dprint("BUILDING: got an or, recursing both", DBG_STRUCT)
		build_past_structure(Struct, lchild(formula))
		build_past_structure(Struct, rchild(formula))
		return True
	elif (ftype(formula) == IMPLIES_T):
		dprint("BUILDING: got an implies, recursing both", DBG_STRUCT)
		build_past_structure(Struct, lchild(formula)) 
		build_past_structure(Struct, rchild(formula))
		return True
	elif (ftype(formula) == EVENT_T): 
		dprint("BUILDING: got an eventually, ADDING STRUCT and recursing", DBG_STRUCT)
	#	cTag = tag_formula(formula)
	#	d = delay(formula) + extbound
	#	add_struct(Struct, cTag, d, rchild(formula))
		return build_past_structure(Struct, rchild(formula), extbound=d)
	elif (ftype(formula) == ALWAYS_T):
		dprint("BUILDING: got an always, ADDING STRUCT and recursing", DBG_STRUCT)
		#cTag = tag_formula(formula)
		#d = delay(formula) + extbound
		#add_struct(Struct, cTag, d, rchild(formula))
		return build_past_structure(Struct, rchild(formula), extbound=d)
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
		build_past_structure(Struct, untilP1(formula), extbound=d1)
		build_past_structure(Struct, untilP2(formula), extbound=d2)
		return True
	elif (ftype(formula) == PALWAYS_T):
		dprint("BUILDING: got a past always, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		d = past_delay(formula) + extbound
		add_struct(Struct, cTag, d, rchild(formula))
		return build_past_structure(Struct, rchild(formula), extbound=d)
	elif (ftype(formula) == PEVENT_T):
		dprint("BUILDING: got a past eventually, ADDING STRUCT and recursing", DBG_STRUCT)
		cTag = tag_formula(formula)
		d = past_delay(formula) + extbound
		add_struct(Struct, cTag, d, rchild(formula))
		return build_past_structure(Struct, rchild(formula), extbound=d)
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
		build_past_structure(Struct, untilP1(formula), extbound=d1)
		build_past_structure(Struct, untilP2(formula), extbound=d2)
		return True
	else:
		dprint("BUILDING ERROR: Got unmatched AST node while building", DBG_STRUCT);
		return False
	# shouldn't get here
	return False


####### END PAST-ONLY STRUCT #########

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
