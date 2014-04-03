#!/usr/bin/python
##
##
## @author Aaron Kane
##
## Pulling some utility functions into a module to use across monitor algorithms

## Some constants
EXP_T, PROP_T, NPROP_T, NOT_T, AND_T, OR_T, IMPLIES_T, EVENT_T, ALWAYS_T, UNTIL_T, PALWAYS_T, PEVENT_T, SINCE_T, VALUE_T, INVALID_T = range(15)

TAGi, FORMULAi, DELAYi, VALIDi, LISTi, FLISTi = range(0,6) 

ALC_ALIVE, ALC_VIOLATE, ALC_SATISFY = range(0,3)
ALG_RES, ALG_STCONS, ALG_PURECONS = range(0,3)

## debug constants
DBG_ERROR = 0x01
DBG_STRUCT = 0x02
DBG_SMON = 0x04
DBG_STATE = 0x08
DBG_TIME = 0x10
#DBG_MASK = DBG_ERROR | DBG_STRUCT | DBG_SMON | DBG_STATE 
DBG_MASK = DBG_ERROR | DBG_TIME

# global constants
PERIOD = 1
sTag = 0


def setDBG_MASK(val):
	global DBG_MASK
	DBG_MASK = val
class ipstructure:
	def __init__(self, tag, formula=[], delay=0):
		self.tag = tag
		self.formula = formula
		self.delay = delay
		self.history = []
		self.residues = []
		self.valid = 0

	def addHist(self, time, val):
		if (val):
			added = False
			for i in self.history:
				if i.extendedBy(time):
					i.addEntry(time)
					added = True
			if (not added):
				self.history.append(Interval(time, time+PERIOD))
		# Add to validity whether True or false
		self.valid = max(self.valid, time+PERIOD)
	def addRes(self, Struct, history, step, formula):
		self.residues.append((step, substitute_stcons(Struct, history, step, (step, formula))))
	def cleanRes(self):
		self.residues = [f for f in self.residues if (f[1] != True and f[1] != False)]
	def cleanHist(self):
		self.history = [i for i in self.history if (i.end >= self.valid-self.delay)]
	def updateHist(self):
		for res in self.residues:
			if (res[1] == True):
				self.addHist(res[0], True)
			elif (res[1] == False):
				self.addHist(res[0], False)
	def incrRes(self, Struct, history, step):
		for i,f in enumerate(self.residues):
			self.residues[i] = (f[0], reduce(substitute_stcons(Struct, history, step, f)))
	def alCheck(self, interval):
		trInt = interval.truncate(self.valid)
		# if truncate is empty, then we can't check any of interval yet
		if (trInt.empty()):
			return ALC_ALIVE
		# can check something, lets look
		found_super = False
		for i in self.history:
			if (i.superset(trInt)):
				found_super = True
		# didn't find always from start to current, violation
		if (not found_super):
			return ALC_VIOLATE
		# found entire interval, satisfies
		elif (found_super and trInt == interval):
			return ALC_SATISFY
		# else found but not finished, keep going
		return ALC_ALIVE
	def __str__(self):
		return "Struct: [%d|| DEL: %d FORM: %s VAL: %d :: HIST: %s, RES: %s]" % (self.tag, self.delay, self.formula, self.valid, self.history, self.residues)
class istructure:
	def __init__(self, tag, formula=[], delay=0):
		self.tag = tag
		self.formula = formula
		self.delay = delay
		self.history = []
		self.residues = []
		self.valid = 0

	def addHist(self, time, val):
		if (val):
			added = False
			for i in self.history:
				if i.extendedBy(time):
					i.addEntry(time)
					added = True
			if (not added):
				self.history.append(Interval(time, time+PERIOD))
		# Add to validity whether True or false
		self.valid = max(self.valid, time+PERIOD)
	def addRes(self, Struct, cstate, time, formula):
		self.residues.append((time, substitute_perint_agp(Struct, cstate, (time, formula))))
	def cleanRes(self):
		self.residues = [f for f in self.residues if (f[1] != True and f[1] != False)]
	def cleanHist(self):
		self.history = [i for i in self.history if (i.end >= self.valid-self.delay)]
	def updateHist(self):
		for res in self.residues:
			if (res[1] == True):
				self.addHist(res[0], True)
			elif (res[1] == False):
				self.addHist(res[0], False)
	def incrRes(self, Struct, cstate):
		for i,f in enumerate(self.residues):
			self.residues[i] = (f[0], reduce(substitute_perint_agp(Struct, cstate, f)))
	def alCheck(self, interval):
		trInt = interval.truncate(self.valid)
		# if truncate is empty, then we can't check any of interval yet
		if (trInt.empty()):
			return ALC_ALIVE
		# can check something, lets look
		found_super = False
		for i in self.history:
			if (i.superset(trInt)):
				found_super = True
		# didn't find always from start to current, violation
		if (not found_super):
			return ALC_VIOLATE
		# found entire interval, satisfies
		elif (found_super and trInt == interval):
			return ALC_SATISFY
		# else found but not finished, keep going
		return ALC_ALIVE
	def __str__(self):
		return "Struct: [%d|| DEL: %d FORM: %s VAL: %d :: HIST: %s, RES: %s]" % (self.tag, self.delay, self.formula, self.valid, self.history, self.residues)
	
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

class Interval(object):
	def __init__(self, start, end):
			self.start = start
			self.end = end

	def __str__(self):
		return "[%d,%d)" % (self.start, self.end)
	def __repr__(self):
		return "[%d,%d)" % (self.start, self.end)

	def __contains__(self, point):
		return (point >= self.start and point < self.end)
	def __eq__(self, other):
		return (self.start == other.start and self.end == other.end)
	def __ne__(self, other):
		return (self.start != other.start or self.end != other.end)

	def intersection(self, interval):
		return Interval(max(self.start, interval.start), min(self.end, interval.end))

	def intersects(self, interval):
		return not self.intersection(interval).empty()
		#if (self.start <= interval.start):
		#	if (self.end > interval.start):
		#		return True
		#	return False
		#else:
		#	if (interval.end > self.start):
		#		return True
		#	return False
	def addEntry(self, entry):
		if (entry == self.end):
			self.end = entry+PERIOD
			return True
		if (entry == self.start-PERIOD):
			self.start = entry
			return True
		else:
			return False
	def extendedBy(self, entry):
		return (entry == self.end or entry == self.start-PERIOD)
	def truncate(self, v):
		return Interval(self.start, min(self.end, v))
	def superset(self, interval):
		return (self.start <= interval.start and self.end >= interval.end)
	def prop_superset(self, interval):
		return (self.start <= interval.start and self.end > interval.end)
	def empty(self):
		return self.start >= self.end

# add a tag to past time formula
def tag_formula(formula):
	global sTag
	formula.insert(3, sTag)
	sTag = sTag + 1
	return (sTag - 1)

# get tag of past-time formula
def get_tags(formula):
	if (len(formula) == 5):
		return formula[3]
	elif (len(formula) == 7):
		return (formula[3], formula[4])
	return -1

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

def not_future(formula):
	if (ftype(formula) == EXP_T):
		return not_future(Struct, rchild(formula))
	elif (ftype(formula) == VALUE_T):
		return True
	elif (ftype(formula) == PROP_T):
		return True
	elif (ftype(formula) == NPROP_T):
		return True
	elif (ftype(formula) == NOT_T):
		return not_future(Struct, rchild(formula))
	elif (ftype(formula) == AND_T):
		return not_future(Struct, lchild(formula)) and not_future(Struct, rchild(formula))
	elif (ftype(formula) == OR_T):
		return not_future(Struct, lchild(formula)) and not_future(Struct, rchild(formula))
	elif (ftype(formula) == IMPLIES_T):
		return not_future(Struct, lchild(formula)) and not_future(Struct, rchild(formula))
	elif (ftype(formula) == EVENT_T): 
		return False
	elif (ftype(formula) == ALWAYS_T):	
		return False
	elif (ftype(formula) == UNTIL_T): 
		return False
	elif (ftype(formula) == PALWAYS_T):
		return not_future(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		return not_future(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		return not_future(untilP1(formula)) and not_future(untilP2(formula))
	else:
		# shouldn't get here
		dprint("future checking error...", DBG_ERROR)
		return False

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
		#print "checking (%d,%d)" % (sStart, sEnd)
		#print "sub: %s" % subStruct2
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct2.history):
				if (subStruct2.history[t] == True):
					start = t
					allF = False
					break
			else:
				allF = False
		# if we're past the time we have to have an answer, we didn't see the eventually
		#print "start: %s" % start
		found = True
		if allF: 
			return False
		elif (start is None):
			return formula

		# did find eventually, check P1
		sEnd = formtime
		sStart = start
		allT = True
		#print "checking (%d,%d)" % (sStart, sEnd)
		#print "sub: %s" % subStruct1
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
		return ['impprop', substitute_perint_agp(Struct, cstate, (formtime,formula[1])), substitute_perint_agp(Struct, cstate, (formtime, formula[2]))]
	elif (ftype(formula) == EVENT_T): 
		subStruct = Struct[get_tags(formula)]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		check = Interval(sStart, sEnd+PERIOD)
		
		for i in subStruct.history:
			if i.intersects(check):
				return True
		# not waiting on any data, if formula satisfied would've returned true above
		if (subStruct.valid > sEnd):
			return False
		return formula
	elif (ftype(formula) == ALWAYS_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		check = Interval(sStart, sEnd+PERIOD)

		alcheck = subStruct.alCheck(check)
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
		check = Interval(sStart, sEnd+PERIOD)
		end = None
		efound = True

		for i in subStruct2.history:
			if i.intersects(check):
				end = i.intersection(check).start
		# didn't find P2 and past time
		if (end is None and subStruct2.valid > sEnd):
			return False
		elif (end is None):
			end = subStruct2.valid
			efound = False
		
		# did find eventually, check P1
		sEnd = end + PERIOD		# end value is inclusive
		sStart = formtime
		check = Interval(sStart, sEnd)
		alcheck = subStruct1.alCheck(check)

		if (alcheck == ALC_SATISFY and efound):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE or ALC_SAT and not found
			return formula
	elif (ftype(formula) == PEVENT_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = formtime - lbound(formula)
		sStart = formtime - hbound(formula)
		check = Interval(sStart, sEnd+PERIOD)
		
		for i in subStruct.history:
			if i.intersects(check):
				return True
		# not waiting on any data, if formula satisfied would've returned true above
		if (subStruct.valid > sEnd):
			return False
		return formula
	elif (ftype(formula) == PALWAYS_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = formtime - lbound(formula)
		sStart = formtime - hbound(formula)
		check = Interval(sStart, sEnd+PERIOD)

		alcheck = subStruct.alCheck(check)
		if (alcheck == ALC_SATISFY):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE
			return formula
	elif (ftype(formula) == SINCE_T):
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sEnd = formtime - lbound(formula)
		sStart = formtime - hbound(formula)


		check = Interval(sStart, sEnd+PERIOD)
		start = None
		efound = True

		for i in subStruct2.history:
			if i.intersects(check):
				start = i.intersection(check).start
		# didn't find P2 and past time
		if (start is None and subStruct2.valid > sEnd):
			return False
		elif (start is None):
			start = subStruct2.valid
			efound = False

		# did find eventually, check P1
		sEnd = formtime + PERIOD	# end is inclusive
		sStart = start 
		check = Interval(sStart, sEnd)
		alcheck = subStruct1.alCheck(check)

		if (alcheck == ALC_SATISFY and efound):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE or ALC_SAT and not found
			return formula
	else:
		return INVALID_T

def substitute_stcons(Struct, history, eptr, formula_entry):
	formtime = formula_entry[0]
	formula = formula_entry[1]
	if (ftype(formula) == EXP_T):
		return [formula[0], substitute_stcons(Struct, history, eptr, (formtime, lchild(formula)))]
	elif (ftype(formula) == VALUE_T):
		return formula
	elif (ftype(formula) == PROP_T):
		if (history[eptr][lchild(formula)]):
			return True
		else:
			return False
	elif (ftype(formula) == NPROP_T):
		if (history[eptr][lchild(formula)]):
			return False
		else:
			return True
	elif (ftype(formula) == NOT_T):
		return ['notprop', substitute_stcons(Struct, history, eptr, (formtime, lchild(formula)))]
	elif (ftype(formula) == AND_T):
		return ['andprop', substitute_stcons(Struct, history, eptr, (formtime, lchild(formula))), substitute_stcons(Struct, history, eptr, (formtime,rchild(formula)))]
	elif (ftype(formula) == OR_T):
		return ['orprop', substitute_stcons(Struct, history, eptr, (formtime,lchild(formula))), substitute_stcons(Struct, history, eptr, (formtime, rchild(formula)))]
	elif (ftype(formula) == IMPLIES_T):
		return ['impprop', substitute_stcons(Struct, history, eptr, (formtime,lchild(formula))), substitute_stcons(Struct, history, eptr, (formtime, rchild(formula)))]
	elif (ftype(formula) == EVENT_T): 
		l = lbound(formula) + formtime
		h = hbound(formula) + formtime
		
		for i in range(l, h+PERIOD):
			if reduce(substitute_stcons(Struct, history, i, (i, rchild(formula)))):
				return True
		return False
	elif (ftype(formula) == ALWAYS_T):
		l = lbound(formula) + formtime
		h = hbound(formula) + formtime

		for i in range(l, h+PERIOD):
			if (not reduce(substitute_stcons(Struct, history, i, (i, rchild(formula))))):
				return False
		return True
	elif (ftype(formula) == UNTIL_T): 
		l = lbound(formula) + formtime
		h = hbound(formula) + formtime
		end = None
		for i in range(l, h+PERIOD):
			if reduce(substitute_stcons(Struct, history, i, (i, untilP2(formula)))):
				end = i
				break
		if (end is None):
			return False
		#
		l = formtime
		h = end

		for i in range(l, h+PERIOD):
			if (not reduce(substitute_stcons(Struct, history, i, (i, untilP1(formula))))):
				return False
		return True
	elif (ftype(formula) == PEVENT_T):
		if (not_future(formula)):
			subStruct = Struct[get_tags(formula)]
			sEnd = formtime - lbound(formula)
			sStart = formtime - hbound(formula)
			check = Interval(sStart, sEnd+PERIOD)
			
			for i in subStruct.history:
				if i.intersects(check):
					return True
			# not waiting on any data, if formula satisfied would've returned true above
			if (subStruct.valid > sEnd):
				return False
			return formula
		#### Nested, Don't have struct, check manually
		else:
			l = formtime - hbound(formula)
			h = formtime - lbound(formula)
			
			for i in range(l, h+PERIOD):
				if reduce(substitute_stcons(Struct, history, i, (i, rchild(formula)))):
					return True
			return False
	elif (ftype(formula) == PALWAYS_T):
		if (not_future(formula)):
			subStruct = Struct[get_tags(formula)]
			sEnd = formtime - lbound(formula)
			sStart = formtime - hbound(formula)
			check = Interval(sStart, sEnd+PERIOD)

			alcheck = subStruct.alCheck(check)
			if (alcheck == ALC_SATISFY):
				return True
			elif (alcheck == ALC_VIOLATE):
				return False
			else: # alcheck == ALC_ALIVE
				return formula
		#### nested future, don't have struct, check manually
		else: 
			l = formtime - hbound(formula)
			h = formtime - lbound(formula)

			for i in range(l, h+PERIOD):
				if (not reduce(substitute_stcons(Struct, history, i, (i, rchild(formula))))):
					return False
			return True
	elif (ftype(formula) == SINCE_T):
		if (not_future(formula)):
			tags = get_tags(formula)
			subStruct1 = Struct[tags[0]]
			subStruct2 = Struct[tags[1]]
			sEnd = formtime - lbound(formula)
			sStart = formtime - hbound(formula)

			check = Interval(sStart, sEnd+PERIOD)
			start = None
			efound = True

			for i in subStruct2.history:
				if i.intersects(check):
					start = i.intersection(check).start
			# didn't find P2 and past time
			if (start is None and subStruct2.valid > sEnd):
				return False
			elif (start is None):
				start = subStruct2.valid
				efound = False

			# did find eventually, check P1
			sEnd = formtime + PERIOD	# end is inclusive
			sStart = start 
			check = Interval(sStart, sEnd)
			alcheck = subStruct1.alCheck(check)

			if (alcheck == ALC_SATISFY and efound):
				return True
			elif (alcheck == ALC_VIOLATE):
				return False
			else: # alcheck == ALC_ALIVE or ALC_SAT and not found
				return formula
		# nested future, don't have struct, check manually
		else:
			l = formtime - hbound(formula)
			h = formtime - lbound(formula)
			start = None
			for i in range(l, h+PERIOD):
				if reduce(substitute_stcons(Struct, history, i, (i, untilP2(formula)))):
					end = i
					break
			if (start is None):
				return False
			#
			l = start
			h = formtime 
			for i in range(l, h+PERIOD):
				if (not reduce(substitute_stcons(Struct, history, i, (i, untilP1(formula))))):
					return False
			return True
	else:
		return INVALID_T

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
		if (child1 == False or child2 == False):
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
	elif (ftype(formula) == PALWAYS_T):
		return formula
	elif (ftype(formula) == SINCE_T):
		return formula
	else:
		return INVALID_T


def dprint(string, lvl=0xFF):
#	print "DPRINT %s %d" % (string, lvl)
	if (DBG_MASK & lvl):
		print string
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
	#print "wdelay %s" % formula
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
def nfdelay(formula):
	if (ftype(formula) == EXP_T):
		return nfdelay(rchild(formula))
	elif (ftype(formula) == PROP_T):
		return 0
	elif (ftype(formula) == NPROP_T):
		return 0
	elif (ftype(formula) == NOT_T):
		return nfdelay(rchild(formula))
	elif (ftype(formula) == AND_T):
		return max(nfdelay(lchild(formula)),nfdelay(rchild(formula)))
	elif (ftype(formula) == OR_T):
		return max(nfdelay(lchild(formula)),nfdelay(rchild(formula)))
	elif (ftype(formula) == IMPLIES_T):
		return max(nfdelay(lchild(formula)),nfdelay(rchild(formula)))
	elif (ftype(formula) == EVENT_T): 
		return nfdelay(rchild(formula))
	elif (ftype(formula) == ALWAYS_T):
		return nfdelay(rchild(formula))
	elif (ftype(formula) == UNTIL_T): 
		return max(nfdelay(untilP1(formula)),nfdelay(untilP2(formula)))
	elif (ftype(formula) == PALWAYS_T):
		if (not_future(formula)):
			return nfdelay(rchild(formula))
		return hbound(formula) + nfdelay(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		if (not_future(formula)):
			return nfdelay(rchild(formula))
		return hbound(formula) + nfdelay(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		if (not_future(formula)):
			return max(nfdelay(untilP1(formula)),nfdelay(untilP2(formula)))
		return hbound(formula) + max(nfdelay(untilP1(formula)),nfdelay(untilP2(formula)))
	else:
		dprint("NESTED-FUTURE-DELAY ERROR: Got unmatched AST node while building", DBG_ERROR);
		return None
	# shouldn't get here
	return None

########## Interval Utils
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
